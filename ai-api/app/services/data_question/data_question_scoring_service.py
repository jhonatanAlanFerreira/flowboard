from datetime import datetime, timezone
import json
from typing import Dict, List
from app.config import settings
from app.observability.phoenix import get_tracer
from app.models.request.search_strategist_request import HydratedChunk
from app.schemas.data_question import ScoredChunk, ChunkWeights

tracer = get_tracer()

class DataQuestionScoringService:
    """
    Ranks and scores hydrated chunks based on search confidence,
    recency, completion status, and search overlap.
    """

    def __init__(self, config=None):
        self.config = config or settings.data_question_scoring

    def score_and_rank_chunks(self, query: str, chunks: List[HydratedChunk], limit: int = None) -> List[ScoredChunk]:
        """
        Calculates a priority score for each chunk and returns the top K items.
        """
        limit = limit if limit is not None else self.config.default_limit

        with tracer.start_as_current_span("service.scoring") as span:
            span.set_attribute("input.query", query)
            span.set_attribute("input.initial_count", len(chunks))

            scored_chunks: List[ScoredChunk] = []
            now = datetime.now(timezone.utc)

            for chunk_data in chunks:
                chunk = ScoredChunk(**chunk_data.model_dump())

                base_score = float(chunk.search_score or 0.0)
                
                status_weight = (
                    self.config.not_done_weight if not chunk.done 
                    else self.config.done_weight
                )
                
                both_weight = self.config.double_retrieval_boost if chunk.found_in_both else 0.0
                
                recency_weight = 0.0
                if chunk.created_at:
                    try:
                        created_date = datetime.fromisoformat(chunk.created_at.replace('Z', '+00:00'))
                        days_old = (now - created_date).days
                        
                        if days_old <= self.config.recent_days_threshold:
                            recency_weight = self.config.recent_days_boost
                        elif days_old <= self.config.mid_days_threshold:
                            recency_weight = self.config.mid_days_boost
                    except Exception:
                        pass

                chunk.final_calculated_score = round(base_score + status_weight + both_weight + recency_weight, 4)
                chunk.weights = ChunkWeights(
                    base=base_score,
                    status=status_weight,
                    overlap=both_weight,
                    recency=recency_weight
                )
                
                scored_chunks.append(chunk)

            # Sort objects by attribute
            ranked_chunks = sorted(
                scored_chunks, 
                key=lambda x: x.final_calculated_score, 
                reverse=True
            )

            top_candidates = ranked_chunks[:limit]

            span.set_attribute("output.ranked_count", len(top_candidates))
            top_ids = [str(c.chunk_id) for c in top_candidates]
            span.set_attribute("output.top_ranked_ids", json.dumps(top_ids))

            return top_candidates

