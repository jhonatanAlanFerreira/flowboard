import json
from typing import Dict, List
import weaviate.classes.query as wvc_query
from sentence_transformers import SentenceTransformer
from app.clients.weaviate_client import get_weaviate_client
from app.config import settings
from app.observability.phoenix import get_tracer
from app.schemas.data_question import RetrievedChunk

client = get_weaviate_client()
tracer = get_tracer()


def normalize_text(value: str) -> str:
    return str(value).strip().lower()


class DataQuestionRetrievalService:
    def __init__(self, config=None):
        self.config = config or settings.data_question_retrieval
        self.client = client
        self.class_name = self.config.class_name
        self.model = SentenceTransformer(self.config.model_name)
        self.collection = self.client.collections.get(self.class_name)

    def retrieve_chunks_for_question(
        self, query: str, user_id: int, prediction_result: Dict
    ) -> List[RetrievedChunk]:
        """
        Retrieves task chunks based on predicted workspaces and applies a global fallback.
        Merges and ranks the candidates.
        """
        user_id_string = str(user_id)
        query_norm = normalize_text(query)
        query_vector = self.model.encode(query_norm).tolist()

        workspace_id = prediction_result.get("predicted_workspace_id")
        confidence = prediction_result.get("confidence_score", 0.0)

        with tracer.start_as_current_span("service.question_retrieval") as span:
            span.set_attribute("input.query", query)
            span.set_attribute("input.user_id", user_id_string)
            span.set_attribute("input.predicted_workspace_id", str(workspace_id))
            span.set_attribute("input.confidence", confidence)

            all_hits = []
            targeted_chunk_ids = set()

            if workspace_id and confidence >= self.config.confidence_threshold:
                targeted_hits = self._execute_search(
                    query_norm,
                    query_vector,
                    user_id_string,
                    limit=self.config.targeted_search_limit,
                    workspace_id=str(workspace_id),
                )
                all_hits.extend(targeted_hits)

                for hit in targeted_hits:
                    targeted_chunk_ids.add(hit.get("chunk_id"))

                global_hits = self._execute_search(
                    query_norm,
                    query_vector,
                    user_id_string,
                    limit=self.config.global_fallback_limit,
                    workspace_id=None,
                )
                all_hits.extend(global_hits)
            else:
                global_hits = self._execute_search(
                    query_norm,
                    query_vector,
                    user_id_string,
                    limit=self.config.pure_global_limit,
                    workspace_id=None,
                )
                all_hits.extend(global_hits)

            seen_chunk_ids = set()
            unique_hits: List[RetrievedChunk] = []

            for hit in all_hits:
                c_id = hit.get("chunk_id")

                if c_id in seen_chunk_ids:
                    for u_hit in unique_hits:
                        if u_hit.chunk_id == c_id:
                            u_hit.found_in_both = True
                            break
                    continue

                seen_chunk_ids.add(c_id)

                unique_hits.append(
                    RetrievedChunk(
                        chunk_id=c_id,
                        workspace_id=hit.get("workspace_id"),
                        tasklist_id=hit.get("tasklist_id"),
                        content=hit.get("content"),
                        search_score=hit.get("search_score"),
                        found_in_both=False,
                    )
                )

            for u_hit in unique_hits:
                if not u_hit.found_in_both and u_hit.chunk_id in targeted_chunk_ids:
                    count = sum(
                        1 for h in all_hits if h.get("chunk_id") == u_hit.chunk_id
                    )
                    if count > 1:
                        u_hit.found_in_both = True

            span.set_attribute("output.retrieved_count", len(unique_hits))
            return unique_hits

    def _execute_search(
        self,
        query_norm: str,
        query_vector: List[float],
        user_id_string: str,
        limit: int,
        workspace_id: str = None,
    ) -> List[Dict]:

        filters = wvc_query.Filter.by_property("user_id").equal(
            user_id_string
        ) & wvc_query.Filter.by_property("type").equal("task")

        if workspace_id:
            filters = filters & wvc_query.Filter.by_property("workspace_id").equal(
                workspace_id
            )

        response = self.collection.query.hybrid(
            query=query_norm,
            vector=query_vector,
            alpha=self.config.hybrid_alpha,
            filters=filters,
            limit=limit,
            return_properties=["chunk_id", "workspace_id", "tasklist_id", "content"],
            return_metadata=wvc_query.MetadataQuery(score=True),
        )

        return [
            {
                "chunk_id": obj.properties.get("chunk_id"),
                "workspace_id": obj.properties.get("workspace_id"),
                "tasklist_id": obj.properties.get("tasklist_id"),
                "content": obj.properties.get("content"),
                "search_score": obj.metadata.score,
            }
            for obj in response.objects
        ]
