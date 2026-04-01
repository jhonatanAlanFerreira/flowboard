from typing import List, Dict
from sentence_transformers import SentenceTransformer
from app.clients.weaviate_client import get_weaviate_client
from app.observability.phoenix import get_tracer
import time

client = get_weaviate_client()
tracer = get_tracer()


class RetrievalService:
    def __init__(self):
        self.client = client
        self.class_name = "Chunk"
        self.model = SentenceTransformer("all-MiniLM-L6-v2")

    def search(self, query: str, user_id: int, limit: int = 20) -> List[Dict]:
        user_id_string = str(user_id)
        query_vector = self.model.encode(query).tolist()

        with tracer.start_as_current_span("service.retrieval") as span:
            span.set_attribute("input.query", query)
            span.set_attribute("input.user_id", user_id_string)

            with tracer.start_as_current_span("hybrid.search") as hybrid_span:
                start = time.time()

                response = (
                    self.client.query
                    .get(self.class_name, ["workspace_id", "content"])
                    .with_hybrid(
                        query=query,
                        vector=query_vector,
                        alpha=0.8
                    )
                    .with_where({
                        "path": ["user_id"],
                        "operator": "Equal",
                        "valueString": user_id_string
                    })
                    .with_additional(["score"])
                    .with_limit(limit)
                    .do()
                )

                hybrid_span.set_attribute(
                    "latency_ms",
                    int((time.time() - start) * 1000)
                )

            hits = response.get("data", {}).get("Get", {}).get(self.class_name) or []

            results = []
            for hit in hits:
                results.append({
                    "workspace_id": hit["workspace_id"],
                    "score": float(hit["_additional"]["score"])
                })

            # sort (usually already sorted, but safe)
            results.sort(key=lambda x: x["score"], reverse=True)

            top_results = results[:5]

            span.set_attribute("output.count", len(top_results))
            span.set_attribute(
                "output.top_score",
                top_results[0]["score"] if top_results else 0
            )

            return top_results