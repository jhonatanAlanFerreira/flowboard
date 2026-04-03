from typing import List, Dict
import math
from app.observability.phoenix import get_tracer

tracer = get_tracer()

class ScoringWorkflowService:

    def rank_workspaces(self, workspace_chunks: Dict) -> List[Dict]:
        with tracer.start_as_current_span("service.scoring.workspaces") as span:
            span.set_attribute("input.workspace_count", len(workspace_chunks))
            
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

            # Trace top results summary (IDs and Scores only)
            span.set_attribute("output.ranked_count", len(results))
            if results:
                span.set_attribute("output.top_score", results[0]["score"])
            
            return results
    