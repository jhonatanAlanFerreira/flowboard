from typing import List, Dict


class WorkspaceSelectionService:

    def __init__(
        self,
        min_similarity: float = 0.7,
        relative_threshold: float = 0.8,
        limit: int = 5
    ):
        self.min_similarity = min_similarity
        self.relative_threshold = relative_threshold
        self.limit = limit


    def select(self, candidates: List[Dict]) -> List[Dict]:
        if not candidates:
            return []

        best = max(c["score"] for c in candidates)

        filtered = self._filter_min_similarity(candidates)
        filtered = self._filter_relative_to_best(filtered, best)

        rescored = self._rescore(filtered, best)

        return self._sort_and_limit(rescored)

    def _filter_min_similarity(self, candidates: List[Dict]) -> List[Dict]:
        return [
            c for c in candidates
            if c["score"] >= self.min_similarity
        ]

    def _filter_relative_to_best(self, candidates: List[Dict], best: float) -> List[Dict]:
        return [
            c for c in candidates
            if c["score"] >= best * self.relative_threshold
        ]

    def _rescore(self, candidates: List[Dict], best: float) -> List[Dict]:
        results = []

        for c in candidates:
            new_score = self._compute_score(c, best)

            results.append({
                **c,
                "final_score": round(new_score, 4)
            })

        return results

    def _sort_and_limit(self, candidates: List[Dict]) -> List[Dict]:
        return sorted(
            candidates,
            key=lambda x: x["final_score"],
            reverse=True
        )[:self.limit]

    def _compute_score(self, c: Dict, best: float) -> float:
        sim = c["score"]

        # placeholders for future signals
        recency = self._recency_score(c)
        structure = self._structure_score(c)

        return (
            sim * 0.6 +
            recency * 0.15 +
            structure * 0.25
        )

    def _recency_score(self, c: Dict) -> float:
        # TODO: plug real data later
        return 0.5

    def _structure_score(self, c: Dict) -> float:
        # TODO: e.g. number of lists, tasks, density
        return 0.5