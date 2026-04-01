from typing import List, Dict
from sentence_transformers import SentenceTransformer
from app.clients.weaviate_client import get_weaviate_client
from app.observability.phoenix import get_tracer
from collections import defaultdict
import json
import math

client = get_weaviate_client()
tracer = get_tracer()


class RetrievalService:
    def __init__(self):
        self.client = client
        self.class_name = "Chunk"
        self.model = SentenceTransformer("all-MiniLM-L6-v2")

    def search(self, query: str, user_id: int, top_k: int = 5) -> List[Dict]:
        user_id_string = str(user_id)
        query_vector = self.model.encode(query).tolist()

        with tracer.start_as_current_span("service.retrieval") as span:
            span.set_attribute("input.query", query)
            span.set_attribute("input.user_id", user_id_string)
            span.set_attribute("input.top_k", top_k)

            response = (
                self.client.query
                .get(self.class_name, ["workspace_id", "content", "chunk_id"])
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
                .do()
            )

            hits = response.get("data", {}).get("Get", {}).get(self.class_name) or []

            workspace_chunks = defaultdict(list)

            for hit in hits:
                wid = hit["workspace_id"]
                score = float(hit["_additional"]["score"])
                chunk_id = hit["chunk_id"]

                workspace_chunks[wid].append({
                    "score": score,
                    "chunk_id": chunk_id
                })

            span.set_attribute(
            "retrieval.workspace_match_count",
            json.dumps({wid: len(chunks) for wid, chunks in workspace_chunks.items()})
)

            workspace_data = {}

            for wid, chunks in workspace_chunks.items():
                scores = [c["score"] for c in chunks]

                max_score = max(scores)
                count = len(scores)

                final_score = max_score + 0.1 * math.log(1 + count)

                # keep best chunk for explainability
                best_chunk = max(chunks, key=lambda x: x["score"])

                workspace_data[wid] = {
                    "workspace_id": wid,
                    "score": final_score,
                    "max_score": max_score,
                    "match_count": count,
                    "chunk_id": best_chunk["chunk_id"]
                }

            results = list(workspace_data.values())
            results.sort(key=lambda x: x["score"], reverse=True)

            top_results = results[:top_k]

            span.set_attribute("output.top_results", json.dumps(top_results))

            return top_results