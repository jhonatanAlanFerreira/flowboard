from typing import List, Dict
from sentence_transformers import SentenceTransformer
from app.clients.weaviate_client import get_weaviate_client
from app.observability.phoenix import get_tracer
from collections import defaultdict
from app.services.collection.scoring_collection_service import ScoringCollectionService
from app.services.collection.workspace_selection_collection_service import WorkspaceSelectionCollectionService
import json

client = get_weaviate_client()
tracer = get_tracer()
scoring_collection_service = ScoringCollectionService()
selection_collection_service = WorkspaceSelectionCollectionService()


class RetrievalCollectionService:
    def __init__(self):
        self.client = client
        self.class_name = "Chunk"
        self.model = SentenceTransformer("all-MiniLM-L6-v2")

    def get_relevant_workspaces(self, query: str, user_id: int, top_k: int = 50) -> List[Dict]:
        user_id_string = str(user_id)
        query_vector = self.model.encode(query).tolist()

        with tracer.start_as_current_span("service.retrieval") as span:
            span.set_attribute("input.query", query)
            span.set_attribute("input.user_id", user_id_string)
            span.set_attribute("input.top_k", top_k)

            # Retrieval
            response = (
                self.client.query
                .get(self.class_name, ["workspace_id", "content", "chunk_id"])
                .with_hybrid(query=query, vector=query_vector, alpha=0.6)
                .with_where({
                    "operator": "And",
                    "operands": [
                        {
                            "path": ["user_id"],
                            "operator": "Equal",
                            "valueString": user_id_string
                        },
                        {
                            "path": ["type"],
                            "operator": "Equal",
                            "valueString": "task"
                        }
                    ]
                })
                .with_additional(["score"])
                .do()
            )

            hits = response.get("data", {}).get("Get", {}).get(self.class_name) or []

            # Group chunks by workspace
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

            # Ranking
            ranked_results = scoring_collection_service.rank_workspaces(workspace_chunks)

            # Selection / filtering
            selected_results = selection_collection_service.select(ranked_results)

            # Limit top_k
            top_results = selected_results[:top_k]

            span.set_attribute("output.top_results", json.dumps(top_results))

            return top_results
        


    def get_relevant_lists_for_workspaces(self, workspace_ids: list[str], query: str):
        query_vector = self.model.encode(query).tolist()

        response = (
            self.client.query
            .get("Chunk", ["tasklist_id", "chunk_id"])
            .with_where({
                "operator": "And",
                "operands": [
                    {
                        "path": ["workspace_id"],
                        "operator": "ContainsAny",
                        "valueTextArray": workspace_ids
                    },
                    {
                        "path": ["type"],
                        "operator": "Equal",
                        "valueString": "task"
                    }
                ]
            })
            .with_hybrid(query=query, vector=query_vector, alpha=0.8)
            .with_additional(["score"])
            .do()
        )

        hits = response.get("data", {}).get("Get", {}).get("Chunk", [])

        if not hits:
            return []

        # grouping ONLY
        lists = defaultdict(lambda: {"scores": [], "chunks": []})

        for hit in hits:
            list_id = hit["tasklist_id"]
            score = float(hit["_additional"]["score"])
            chunk_id = hit["chunk_id"]

            lists[list_id]["scores"].append(score)
            lists[list_id]["chunks"].append({
                "chunk_id": chunk_id,
                "score": score
            })

        return scoring_collection_service.rank_lists(lists)