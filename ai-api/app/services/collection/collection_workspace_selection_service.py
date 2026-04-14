from typing import List
from app.config import settings
from app.observability.phoenix import get_tracer
from app.schemas.workspace import WorkspaceResult

tracer = get_tracer()

class CollectionWorkspaceSelectionService:

    def __init__(
        self,
        min_similarity: float = None,
        relative_threshold: float = None,
        limit: int = None,
        config = None
    ):
        self.config = config or settings.collection_workspace_selection
        
        self.min_similarity = min_similarity if min_similarity is not None else self.config.min_similarity
        self.relative_threshold = relative_threshold if relative_threshold is not None else self.config.relative_threshold
        self.limit = limit if limit is not None else self.config.limit

    def select(self, candidates: List[WorkspaceResult]) -> List[WorkspaceResult]:
        with tracer.start_as_current_span("service.selection.select") as span:
            if not candidates:
                span.set_attribute("selection.input_count", 0)
                return []

            input_count = len(candidates)
            best = max(c.score for c in candidates)
            
            span.set_attributes({
                "selection.input_count": input_count,
                "selection.best_score": best,
                "selection.thresholds.min_similarity": self.min_similarity,
                "selection.thresholds.relative": self.relative_threshold
            })

            # Filter 1: Absolute Similarity
            filtered = self._filter_min_similarity(candidates)
            count_after_min = len(filtered)
            
            # Filter 2: Relative to best
            filtered = self._filter_relative_to_best(filtered, best)
            count_after_relative = len(filtered)

            # Process and Sort
            rescored = self._rescore(filtered, best)
            results = self._sort_and_limit(rescored)

            span.set_attributes({
                "selection.count_after_min": count_after_min,
                "selection.count_after_relative": count_after_relative,
                "selection.output_count": len(results)
            })

            return results

    def _filter_min_similarity(self, candidates: List[WorkspaceResult]) -> List[WorkspaceResult]:
        return [c for c in candidates if c.score >= self.min_similarity]

    def _filter_relative_to_best(self, candidates: List[WorkspaceResult], best: float) -> List[WorkspaceResult]:
        return [c for c in candidates if c.score >= best * self.relative_threshold]

    def _rescore(self, candidates: List[WorkspaceResult], best: float) -> List[WorkspaceResult]:
        for c in candidates:
            c.final_score = round(self._compute_score(c, best), 4)
        return candidates

    def _sort_and_limit(self, candidates: List[WorkspaceResult]) -> List[WorkspaceResult]:
        return sorted(
            candidates,
            key=lambda x: x.final_score,
            reverse=True
        )[:self.limit]

    def _compute_score(self, c: WorkspaceResult, best: float) -> float:
        sim = c.score

        recency = self._recency_score(c)
        structure = self._structure_score(c)

        return (
            sim * self.config.similarity_weight +
            recency * self.config.recency_weight +
            structure * self.config.structure_weight
        )

    def _recency_score(self, c: WorkspaceResult) -> float:
        return self.config.default_recency_score

    def _structure_score(self, c: WorkspaceResult) -> float:
        return self.config.default_structure_score
