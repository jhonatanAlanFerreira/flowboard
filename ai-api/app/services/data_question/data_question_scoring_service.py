import json
from typing import Dict, List
from datetime import datetime, timezone
from app.observability.phoenix import get_tracer

tracer = get_tracer()

class DataQuestionScoringService:
    """
    Ranks and scores hydrated chunks based on search confidence,
    recency, completion status, and search overlap.
    """

    def score_and_rank_chunks(self, query: str, chunks: List[Dict], limit: int = 15) -> List[Dict]:
        """
        Calculates a priority score for each chunk and returns the top K items.
        """
        with tracer.start_as_current_span("service.scoring") as span:
            span.set_attribute("input.query", query)
            span.set_attribute("input.initial_count", len(chunks))

            scored_chunks = []
            now = datetime.now(timezone.utc)

            for chunk in chunks:
                base_score = float(chunk.get("search_score", 0.0))
                
                # If users ask "What have I completed?", this logic can be inverted.
                status_weight = 0.2 if not chunk.get("done", False) else -0.5
                
                # Double Retrieval Boost (Found in both targeted and global search)
                both_weight = 0.3 if chunk.get("found_in_both", False) else 0.0
                
                # Recency Boosting (Decay math)
                recency_weight = 0.0
                created_at_str = chunk.get("created_at")
                
                if created_at_str:
                    try:
                        # Handle standard ISO strings (like "2026-03-30T20:08:36+00:00")
                        created_date = datetime.fromisoformat(created_at_str.replace('Z', '+00:00'))
                        days_old = (now - created_date).days
                        
                        # Apply a bonus if the task was created in the last 30 days
                        if days_old <= 7:
                            recency_weight = 0.3
                        elif days_old <= 30:
                            recency_weight = 0.15
                    except Exception as e:
                        # Fail silently and skip recency if the date format breaks
                        pass

                # Final Composite Score
                final_score = base_score + status_weight + both_weight + recency_weight

                # Store the calculated weights for transparency in the logs
                chunk["final_calculated_score"] = round(final_score, 4)
                chunk["weights"] = {
                    "base": base_score,
                    "status": status_weight,
                    "overlap": both_weight,
                    "recency": recency_weight
                }
                
                scored_chunks.append(chunk)

            # Sort by the final calculated score in descending order
            ranked_chunks = sorted(
                scored_chunks, 
                key=lambda x: x["final_calculated_score"], 
                reverse=True
            )

            top_candidates = ranked_chunks[:limit]

            span.set_attribute("output.ranked_count", len(top_candidates))
            
            # Log the IDs of the top candidates for tracking
            top_ids = [str(c.get("chunk_id")) for c in top_candidates]
            span.set_attribute("output.top_ranked_ids", json.dumps(top_ids))

            return top_candidates