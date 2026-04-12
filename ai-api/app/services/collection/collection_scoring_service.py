import math
from typing import List, Dict
from app.config import settings
from app.observability.phoenix import get_tracer

tracer = get_tracer()

class CollectionScoringService:

    def __init__(self, config=None):
        self.config = config or settings.collection_scoring

    def rank_workspaces(self, workspace_chunks: Dict) -> List[Dict]:
        with tracer.start_as_current_span("service.scoring.workspaces") as span:
            span.set_attribute("input.workspace_count", len(workspace_chunks))
            
            workspace_data = {}

            for wid, chunks in workspace_chunks.items():
                scores = [c["score"] for c in chunks]
                max_score = max(scores)
                count = len(scores)

                final_score = max_score + self.config.workspace_log_weight * math.log(1 + count)

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

            # Trace top results summary (IDs and Scores only)
            span.set_attribute("output.ranked_count", len(results))
            if results:
                span.set_attribute("output.top_score", results[0]["score"])
            
            return results
    

    def rank_lists(self, lists: dict) -> list[dict]:
        with tracer.start_as_current_span("service.scoring.lists") as span:
            span.set_attribute("input.lists_count", len(lists))
            
            ranked_lists = []

            for list_id, data in lists.items():
                features = self._compute_features(data["scores"])
                score = self._compute_score(features)
                chunks = self._sort_chunks(data["chunks"])

                ranked_lists.append({
                    "tasklist_id": list_id,
                    "score": round(score, 4),
                    **features,
                    "chunks": chunks
                })

            ranked_lists.sort(key=lambda x: x["score"], reverse=True)
            
            span.set_attribute("output.ranked_count", len(ranked_lists))
            if ranked_lists:
                span.set_attribute("output.best_list_id", ranked_lists[0]["tasklist_id"])
                
            return ranked_lists
    

    def _compute_features(self, scores: list[float], top_k: int = None) -> dict:
        if not scores:
            return {"relevance": 0, "volume": 0, "concentration": 0, "volume_norm": 0}

        top_k = top_k if top_k is not None else self.config.feature_top_k

        scores_sorted = sorted(scores, reverse=True)

        # Relevance (top k)
        top_k_scores = scores_sorted[:top_k]
        relevance = sum(top_k_scores) / len(top_k_scores) if top_k_scores else 0

        # Volume (extracted hardcoded 0.7 threshold)
        relevant_chunks = [s for s in scores if s >= self.config.relevance_threshold]
        volume = len(relevant_chunks)

        # Concentration
        concentration = volume / len(scores)

        return {
            "relevance": round(relevance, 4),
            "volume": volume,
            "concentration": round(concentration, 4),
            "volume_norm": math.log(1 + volume)  
        }

    def _compute_score(self, features: dict) -> float:
        return (
            features["relevance"] * self.config.relevance_weight +
            features["volume_norm"] * self.config.volume_norm_weight +
            features["concentration"] * self.config.concentration_weight
        )

    def _sort_chunks(self, chunks: list[dict]) -> list[dict]:
        return sorted(chunks, key=lambda x: x["score"], reverse=True)
