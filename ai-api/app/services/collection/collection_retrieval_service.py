import json
from collections import defaultdict
from typing import List, Dict
import weaviate.classes.query as wvc_query
from sentence_transformers import SentenceTransformer
from app.clients.weaviate_client import get_weaviate_client
from app.config import settings
from app.observability.phoenix import get_tracer
from app.services.collection.collection_scoring_service import CollectionScoringService
from app.services.collection.collection_workspace_selection_service import (
    CollectionWorkspaceSelectionService,
)
from app.schemas.workspace import WorkspaceResult
from app.schemas.chunk import TaskListResult, TaskListChunk, ScoredTaskList

client = get_weaviate_client()
tracer = get_tracer()
collection_scoring_service = CollectionScoringService()
collection_selection_service = CollectionWorkspaceSelectionService()


def normalize_text(value: str) -> str:
    return str(value).strip().lower()


class CollectionRetrievalService:
    def __init__(self, config=None):
        self.config = config or settings.collection_retrieval
        self.client = client
        self.class_name = self.config.class_name
        self.model = SentenceTransformer(self.config.model_name)
        self.collection = self.client.collections.get(self.class_name)

    def get_relevant_workspaces(
        self, query: str, user_id: int, top_k: int = None
    ) -> List[WorkspaceResult]:
        user_id_string = str(user_id)
        query_norm = normalize_text(query)
        query_vector = self.model.encode(query_norm).tolist()
        top_k = top_k if top_k is not None else self.config.workspace_retrieval_top_k

        with tracer.start_as_current_span("service.retrieval") as span:
            span.set_attribute("input.query", query)
            span.set_attribute("input.user_id", user_id_string)
            span.set_attribute("input.top_k", top_k)

            response = self.collection.query.hybrid(
                query=query_norm,
                vector=query_vector,
                alpha=self.config.workspace_hybrid_alpha,
                filters=(
                    wvc_query.Filter.by_property("user_id").equal(user_id_string)
                    & wvc_query.Filter.by_property("type").equal("task")
                ),
                return_properties=["workspace_id", "content", "chunk_id"],
                return_metadata=wvc_query.MetadataQuery(score=True),
            )

            # Group chunks by workspace
            workspace_chunks: Dict[str, List[WorkspaceResult]] = defaultdict(list)

            for obj in response.objects:
                props = obj.properties
                wid = props["workspace_id"]
                score = float(obj.metadata.score)
                chunk_id = props["chunk_id"]

                result = WorkspaceResult(
                    workspace_id=wid,
                    score=score,
                    max_score=score,
                    match_count=1,
                    chunk_id=chunk_id,
                    final_score=0.0,
                )
                workspace_chunks[wid].append(result)

            span.set_attribute(
                "retrieval.workspace_match_count",
                json.dumps(
                    {wid: len(results) for wid, results in workspace_chunks.items()}
                ),
            )

            ranked_results = collection_scoring_service.rank_workspaces(
                workspace_chunks
            )
            selected_results = collection_selection_service.select(ranked_results)
            top_results = selected_results[:top_k]

            span.set_attribute(
                "output.top_results",
                json.dumps([tr.model_dump(mode="json") for tr in top_results]),
            )

            return top_results

    def get_relevant_lists_for_workspaces(
        self, workspace_ids: list[str], query: str, top_k: int = None
    ) -> List[ScoredTaskList]:
        if not workspace_ids:
            return []

        query_norm = normalize_text(query)
        query_vector = self.model.encode(query_norm).tolist()
        top_k = top_k if top_k is not None else self.config.list_retrieval_top_k

        # v4 Search with ContainsAny filter
        response = self.collection.query.hybrid(
            query=query_norm,
            vector=query_vector,
            alpha=self.config.list_hybrid_alpha,
            filters=(
                wvc_query.Filter.by_property("workspace_id").contains_any(workspace_ids)
                & wvc_query.Filter.by_property("type").equal("task")
            ),
            return_properties=["tasklist_id", "chunk_id"],
            return_metadata=wvc_query.MetadataQuery(score=True),
        )

        if not response.objects:
            return []

        lists: Dict[str, TaskListResult] = {}

        for obj in response.objects:
            props = obj.properties
            list_id = props["tasklist_id"]
            score = float(obj.metadata.score)
            chunk_id = props["chunk_id"]

            if list_id not in lists:
                lists[list_id] = TaskListResult(tasklist_id=list_id)

            lists[list_id].scores.append(score)
            lists[list_id].chunks.append(TaskListChunk(chunk_id=chunk_id, score=score))

        return collection_scoring_service.rank_lists(lists)[:top_k]
