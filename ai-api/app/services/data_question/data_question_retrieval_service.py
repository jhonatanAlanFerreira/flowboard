import json
from typing import Dict, List
from sentence_transformers import SentenceTransformer
from app.clients.weaviate_client import get_weaviate_client
from app.observability.phoenix import get_tracer

client = get_weaviate_client()
tracer = get_tracer()

def normalize_text(value: str) -> str:
    return str(value).strip().lower()

class DataQuestionRetrievalService:
    def __init__(self):
        self.client = client
        self.class_name = "Chunk"
        self.model = SentenceTransformer("all-MiniLM-L6-v2")

    def retrieve_chunks_for_question(
        self, 
        query: str, 
        user_id: int, 
        prediction_result: Dict
    ) -> List[Dict]:
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
            
            # Keep track of targeted chunk IDs specifically
            targeted_chunk_ids = set()

            # SCENARIO A: Agent predicted a Workspace with reasonable confidence
            if workspace_id and confidence >= 0.5:
                # Targeted Search (Limit 20)
                targeted_hits = self._execute_search(
                    query_norm, query_vector, user_id_string, 
                    limit=20, workspace_id=str(workspace_id)
                )
                all_hits.extend(targeted_hits)
                
                # Fill the set with IDs from the targeted search
                for hit in targeted_hits:
                    targeted_chunk_ids.add(hit.get("chunk_id"))

                # Global Backup (Limit 10)
                global_hits = self._execute_search(
                    query_norm, query_vector, user_id_string, 
                    limit=10, workspace_id=None
                )
                all_hits.extend(global_hits)

            # SCENARIO B: No workspace found or low confidence
            else:
                # Wide Net Global Search (Limit 50)
                global_hits = self._execute_search(
                    query_norm, query_vector, user_id_string, 
                    limit=50, workspace_id=None
                )
                all_hits.extend(global_hits)

            seen_chunk_ids = set()
            unique_hits = []
            
            for hit in all_hits:
                c_id = hit.get("chunk_id")
                
                # If we've already added this chunk to our unique list
                if c_id in seen_chunk_ids:
                    # If this chunk is appearing again, it means it was in both searches!
                    # We find it in our unique list and set the flag to True
                    for u_hit in unique_hits:
                        if u_hit.get("chunk_id") == c_id:
                            u_hit["found_in_both"] = True
                            break
                    continue
                
                # If it's a brand new chunk ID we haven't processed yet:
                seen_chunk_ids.add(c_id)
                
                # Default flag state is False
                hit["found_in_both"] = False
                
                unique_hits.append(hit)

            # Secondary check for Scenario A: 
            # If a chunk was found during Global but originated in the Targeted set
            for u_hit in unique_hits:
                c_id = u_hit.get("chunk_id")
                # If it's not marked yet but belongs to both sets
                if not u_hit["found_in_both"] and c_id in targeted_chunk_ids:
                    # Verify if it was also returned in the global batch
                    count = sum(1 for h in all_hits if h.get("chunk_id") == c_id)
                    if count > 1:
                        u_hit["found_in_both"] = True

            span.set_attribute("output.retrieved_count", len(unique_hits))
            
            top_10_descriptions = [hit.get("content") for hit in unique_hits[:10]]
            span.set_attribute("output.top_10_tasks", json.dumps(top_10_descriptions))

            return unique_hits

    def _execute_search(
        self, 
        query_norm: str, 
        query_vector: List[float], 
        user_id_string: str, 
        limit: int, 
        workspace_id: str = None
    ) -> List[Dict]:
        """
        Helper method to run a hybrid search against Weaviate v3 with optional WS filter.
        """
        operands = [
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

        if workspace_id:
            operands.append({
                "path": ["workspace_id"],
                "operator": "Equal",
                "valueString": workspace_id
            })

        where_clause = {
            "operator": "And",
            "operands": operands
        }

        response = (
            self.client.query
            .get(self.class_name, ["chunk_id", "workspace_id", "tasklist_id", "content"])
            .with_hybrid(query=query_norm, vector=query_vector, alpha=0.7)
            .with_where(where_clause)
            .with_additional(["score"])
            .with_limit(limit)
            .do()
        )

        hits = response.get("data", {}).get("Get", {}).get(self.class_name) or []
        
        results = []
        for hit in hits:
            results.append({
                "chunk_id": hit.get("chunk_id"),
                "workspace_id": hit.get("workspace_id"),
                "tasklist_id": hit.get("tasklist_id"),
                "content": hit.get("content"),
                "search_score": hit.get("_additional", {}).get("score")
            })
            
        return results
