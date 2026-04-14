from typing import List, Dict
from sentence_transformers import SentenceTransformer
from app.clients.weaviate_client import get_weaviate_client
from app.observability.phoenix import get_tracer
from collections import defaultdict
from app.services.workflow.workflow_scoring_service import WorkflowScoringService
from app.services.workflow.workflow_workspace_selection_service import (
    WorkflowWorkspaceSelectionService,
)
from app.schemas.workspace import WorkspaceResult
from weaviate.classes.query import Filter, MetadataQuery
import weaviate.classes as wvc
import json

client = get_weaviate_client()
tracer = get_tracer()
workflow_scoring_service = WorkflowScoringService()
workflow_selection_service = WorkflowWorkspaceSelectionService()


def normalize_text(value: str) -> str:
    return str(value).strip().lower()


class WorkflowRetrievalService:
    def __init__(self):
        self.client = client
        self.class_name = "Chunk"
        self.model = SentenceTransformer("all-MiniLM-L6-v2")

    def get_relevant_workspaces(
        self, query: str, user_id: int, top_k: int = 5
    ) -> List[WorkspaceResult]:
        user_id_string = str(user_id)
        query_norm = normalize_text(query)
        query_vector = self.model.encode(query_norm).tolist()

        with tracer.start_as_current_span("service.retrieval") as span:
            span.set_attribute("input.query", query)
            span.set_attribute("input.user_id", user_id_string)
            span.set_attribute("input.top_k", top_k)

            # Retrieval
            collection = self.client.collections.get(self.class_name)

            response = collection.query.hybrid(
                query=query_norm,
                vector=query_vector,
                alpha=0.5,
                limit=top_k,
                filters=(
                    Filter.by_property("user_id").equal(user_id_string)
                    & Filter.by_property("type").equal("list")
                ),
                return_properties=["workspace_id", "content", "chunk_id"],
                return_metadata=MetadataQuery(score=True),
            )

            hits = response.objects

            # Group chunks by workspace
            workspace_chunks = defaultdict(list)
            for hit in hits:
                wid = hit.properties["workspace_id"]
                chunk_id = hit.properties["chunk_id"]
                score = float(hit.metadata.score)

                workspace_chunks[wid].append({"score": score, "chunk_id": chunk_id})

            span.set_attribute(
                "retrieval.workspace_match_count",
                json.dumps(
                    {wid: len(chunks) for wid, chunks in workspace_chunks.items()}
                ),
            )

            # Ranking
            ranked_results: List[WorkspaceResult] = (
                workflow_scoring_service.rank_workspaces(workspace_chunks)
            )

            # Selection / filtering
            selected_results: List[WorkspaceResult] = workflow_selection_service.select(
                ranked_results
            )

            # Limit top_k
            top_results = selected_results[:top_k]

            span.set_attribute(
                "output.top_results",
                json.dumps([tr.model_dump(mode="json") for tr in top_results]),
            )

            return top_results
