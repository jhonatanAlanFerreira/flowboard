import math
import re
from typing import List, Dict, Optional
from app.config import settings
from app.observability.phoenix import get_tracer
from app.models.response.patterns_extract_reponse import TaskListPatterns, Pattern
from app.schemas.chunk import ScoredTaskList, TaskListChunk

tracer = get_tracer()


class CollectionPatternExtractionService:
    def __init__(self, config=None):
        self.config = config or settings.collection_pattern_extraction
        self.similarity_threshold = self.config.similarity_threshold

    def extract_patterns_from_lists(
        self,
        lists_data: List[ScoredTaskList],
        top_k_tags: int = None,
        min_score: float = None,
    ) -> List[TaskListPatterns]:
        """
        Processes a list of ScoredTaskList objects to find recurring
        thematic patterns (tags) within their chunks.
        """
        top_k_tags = top_k_tags if top_k_tags is not None else self.config.top_k_tags
        min_score = min_score if min_score is not None else self.config.min_score

        with tracer.start_as_current_span("service.patterns.extract") as span:
            span.set_attributes(
                {
                    "patterns.input_lists_count": len(lists_data),
                    "patterns.config.top_k": top_k_tags,
                    "patterns.config.min_score": min_score,
                }
            )

            results: List[TaskListPatterns] = []
            total_raw_tags = 0

            for list_obj in lists_data:
                list_id = list_obj.tasklist_id

                chunks = self._filter_chunks(list_obj.chunks, min_score)
                if not chunks:
                    continue

                tag_items = self._extract_tag_items(chunks)
                total_raw_tags += len(tag_items)

                tag_groups = self._group_tags(tag_items)
                ranked_groups = self._rank_tag_groups(tag_groups, chunks)
                selected = self._select_diverse_tags(ranked_groups, top_k_tags)

                results.append(
                    TaskListPatterns(
                        tasklist_id=list_id, patterns=self._format_patterns(selected)
                    )
                )

            span.set_attributes(
                {
                    "patterns.total_raw_tags_found": total_raw_tags,
                    "patterns.output_lists_count": len(results),
                }
            )

            return results

    def _filter_chunks(
        self, chunks: List[TaskListChunk], min_score: float
    ) -> List[TaskListChunk]:
        return [c for c in chunks if c.score >= min_score]

    def _extract_tag_items(self, chunks: List[TaskListChunk]) -> List[dict]:
        tag_items = []
        for chunk in chunks:
            tags = getattr(chunk, "tags", []) or []
            task_desc = getattr(chunk, "task_description", "")

            for tag in tags:
                tag_items.append(
                    {
                        "tag": self.normalize_tag(tag),
                        "score": chunk.score,
                        "task": task_desc,
                    }
                )
        return tag_items

    def _group_tags(self, tag_items: List[dict]) -> List[dict]:
        tag_groups = []
        for item in tag_items:
            placed = False
            for group in tag_groups:
                if self.tags_are_similar(item["tag"], group["representative"]):
                    group["items"].append(item)
                    placed = True
                    break
            if not placed:
                tag_groups.append({"representative": item["tag"], "items": [item]})
        return tag_groups

    def _rank_tag_groups(
        self, tag_groups: List[dict], chunks: List[TaskListChunk]
    ) -> List[dict]:
        ranked_groups = []
        for group in tag_groups:
            features = self._compute_tag_features(group["items"], chunks)
            score = self._compute_tag_score(features)
            best_item = max(group["items"], key=lambda x: x["score"])

            ranked_groups.append(
                {
                    "tag": group["representative"],
                    "score": score,
                    "task": best_item["task"],
                }
            )

        ranked_groups.sort(key=lambda x: x["score"], reverse=True)
        return ranked_groups

    def _select_diverse_tags(self, ranked_groups: List[dict], top_k: int) -> List[dict]:
        selected = []
        for candidate in ranked_groups:
            is_similar = any(
                self.tags_are_similar(candidate["tag"], s["tag"]) for s in selected
            )
            if not is_similar:
                selected.append(candidate)
            if len(selected) == top_k:
                break
        return selected

    def _format_patterns(self, selected: List[dict]) -> List[Pattern]:
        return [
            Pattern(tag=s["tag"], score=round(s["score"], 4), task=s["task"])
            for s in selected
        ]

    def _compute_tag_features(
        self, items: List[dict], chunks: List[TaskListChunk]
    ) -> dict:
        scores = [i["score"] for i in items]
        limit = self.config.top_scores_limit
        top_scores = sorted(scores, reverse=True)[:limit]
        relevance = sum(top_scores) / len(top_scores) if top_scores else 0

        frequency = len(items)
        coverage = frequency / len(chunks) if chunks else 0

        return {
            "relevance": relevance,
            "frequency": frequency,
            "coverage": coverage,
            "freq_norm": math.log(1 + frequency),
        }

    def _compute_tag_score(self, f: dict) -> float:
        return (
            f["relevance"] * self.config.relevance_weight
            + f["freq_norm"] * self.config.freq_norm_weight
            + f["coverage"] * self.config.coverage_weight
        )

    def normalize_tag(self, tag: str) -> str:
        tag = tag.lower()
        tag = tag.replace("_", " ")
        tag = re.sub(r"[^a-z0-9\s]", "", tag)
        return tag.strip()

    def tags_are_similar(self, tag1: str, tag2: str) -> bool:
        if tag1 in tag2 or tag2 in tag1:
            return True
        t1_words = set(tag1.split())
        t2_words = set(tag2.split())
        if not t1_words or not t2_words:
            return False
        overlap = len(t1_words & t2_words)
        min_len = min(len(t1_words), len(t2_words))
        return (overlap / min_len) >= self.similarity_threshold
