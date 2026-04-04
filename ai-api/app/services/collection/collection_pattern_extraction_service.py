import math
import re
from typing import List, Dict
from app.observability.phoenix import get_tracer

tracer = get_tracer()

class CollectionPatternExtractionService:
    def __init__(self, similarity_threshold: float = 0.5):
        self.similarity_threshold = similarity_threshold

    def extract_patterns_from_lists(
        self,
        lists_data: List[Dict],
        top_k_tags: int = 3,
        min_score: float = 0
    ) -> List[Dict]:
        with tracer.start_as_current_span("service.patterns.extract") as span:
            span.set_attributes({
                "patterns.input_lists_count": len(lists_data),
                "patterns.config.top_k": top_k_tags,
                "patterns.config.min_score": min_score
            })
            
            results = []
            total_raw_tags = 0

            for list_data in lists_data:
                list_id = list_data["tasklist_id"]

                chunks = self._filter_chunks(list_data["chunks"], min_score)
                if not chunks:
                    continue

                tag_items = self._extract_tag_items(chunks)
                total_raw_tags += len(tag_items)
                
                tag_groups = self._group_tags(tag_items)
                ranked_groups = self._rank_tag_groups(tag_groups, chunks)
                selected = self._select_diverse_tags(ranked_groups, top_k_tags)

                results.append({
                    "tasklist_id": list_id,
                    "patterns": self._format_patterns(selected)
                })

            span.set_attributes({
                "patterns.total_raw_tags_found": total_raw_tags,
                "patterns.output_lists_count": len(results)
            })
            
            return results


    def _filter_chunks(self, chunks: List[Dict], min_score: float) -> List[Dict]:
        return [c for c in chunks if c["score"] >= min_score]

    def _extract_tag_items(self, chunks: List[Dict]) -> List[Dict]:
        tag_items = []

        for chunk in chunks:
            for tag in chunk.get("tags", []):
                tag_items.append({
                    "tag": self.normalize_tag(tag),
                    "score": chunk["score"],
                    "task": chunk.get("task_description", "")
                })

        return tag_items
    

    def _group_tags(self, tag_items: List[Dict]) -> List[Dict]:
        tag_groups = []

        for item in tag_items:
            placed = False

            for group in tag_groups:
                if self.tags_are_similar(item["tag"], group["representative"]):
                    group["items"].append(item)
                    placed = True
                    break

            if not placed:
                tag_groups.append({
                    "representative": item["tag"],
                    "items": [item]
                })

        return tag_groups
    

    def _rank_tag_groups(self, tag_groups: List[Dict], chunks: List[Dict]) -> List[Dict]:
        ranked_groups = []

        for group in tag_groups:
            features = self._compute_tag_features(group["items"], chunks)
            score = self._compute_tag_score(features)

            best_item = max(group["items"], key=lambda x: x["score"])

            ranked_groups.append({
                "tag": group["representative"],
                "score": score,
                "task": best_item["task"]
            })

        ranked_groups.sort(key=lambda x: x["score"], reverse=True)
        return ranked_groups
    

    def _select_diverse_tags(self, ranked_groups: List[Dict], top_k: int) -> List[Dict]:
        selected = []

        for candidate in ranked_groups:
            is_similar = any(
                self.tags_are_similar(candidate["tag"], s["tag"])
                for s in selected
            )

            if not is_similar:
                selected.append(candidate)

            if len(selected) == top_k:
                break

        return selected
    

    def _format_patterns(self, selected: List[Dict]) -> List[Dict]:
        return [
            {
                "tag": s["tag"],
                "score": round(s["score"], 4),
                "task": s["task"]
            }
            for s in selected
        ]


    def _compute_tag_features(self, items: List[Dict], chunks: List[Dict]) -> Dict:
        scores = [i["score"] for i in items]

        top_scores = sorted(scores, reverse=True)[:3]
        relevance = sum(top_scores) / len(top_scores)

        frequency = len(items)
        coverage = frequency / len(chunks) if chunks else 0

        return {
            "relevance": relevance,
            "frequency": frequency,
            "coverage": coverage,
            "freq_norm": math.log(1 + frequency)
        }

    def _compute_tag_score(self, f: Dict) -> float:
        return (
            f["relevance"] * 0.6 +
            f["freq_norm"] * 0.25 +
            f["coverage"] * 0.15
        )


    def normalize_tag(self, tag: str) -> str:
        tag = tag.lower()
        tag = tag.replace("_", " ")
        tag = re.sub(r'[^a-z0-9\s]', '', tag)
        return tag.strip()

    def tags_are_similar(self, tag1: str, tag2: str) -> bool:
        """
        Token-overlap similarity (more robust than simple overlap >= 1)
        """

        if tag1 in tag2 or tag2 in tag1:
            return True

        t1_words = set(tag1.split())
        t2_words = set(tag2.split())

        if not t1_words or not t2_words:
            return False

        overlap = len(t1_words & t2_words)
        min_len = min(len(t1_words), len(t2_words))

        similarity_ratio = overlap / min_len

        return similarity_ratio >= self.similarity_threshold