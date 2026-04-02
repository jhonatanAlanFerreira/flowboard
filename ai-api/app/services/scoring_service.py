from typing import List, Dict
import math


class ScoringService:

    def rank_workspaces(self, workspace_chunks: Dict) -> List[Dict]:
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

        return results
    

    def rank_lists(self, lists: dict) -> list[dict]:
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
        return ranked_lists
    

    def _compute_features(self, scores: list[float]) -> dict:
        if not scores:
            return {
                "relevance": 0,
                "volume": 0,
                "concentration": 0
            }

        scores_sorted = sorted(scores, reverse=True)

        # Relevance (top 3)
        top_k = scores_sorted[:3]
        relevance = sum(top_k) / len(top_k)

        # Volume
        relevant_chunks = [s for s in scores if s >= 0.7]
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
            features["relevance"] * 0.6 +
            features["volume_norm"] * 0.25 +
            features["concentration"] * 0.15
        )

    def _sort_chunks(self, chunks: list[dict]) -> list[dict]:
        return sorted(chunks, key=lambda x: x["score"], reverse=True)