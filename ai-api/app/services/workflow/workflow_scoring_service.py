from typing import List, Dict
import math
from app.observability.phoenix import get_tracer
from app.schemas.workspace import WorkspaceResult
from app.config import settings

tracer = get_tracer()

class WorkflowScoringService:
    def __init__(self, config=None):
        self.config = config or settings.workflow_scoring

    def rank_workspaces(self, workspace_chunks: Dict) -> List[WorkspaceResult]:
        """
        Ranks workflow workspaces using a density-boosted max score.
        """
        with tracer.start_as_current_span("service.scoring.workspaces") as span:
            span.set_attribute("input.workspace_count", len(workspace_chunks))
            
            ranked_workspaces: List[WorkspaceResult] = []

            for wid, results in workspace_chunks.items():
                scores = [r["score"] for r in results]
                max_score = max(scores)
                count = len(scores)

                final_score = max_score + self.config.workspace_log_weight * math.log(1 + count)

                best_result = max(results, key=lambda x: x["score"])

                workspace_info = WorkspaceResult(
                    workspace_id=wid,
                    score=round(final_score, 4),
                    max_score=max_score,
                    match_count=count,
                    chunk_id=best_result["chunk_id"],
                    final_score=round(final_score, 4)
                )
                ranked_workspaces.append(workspace_info)

            # Sort objects by score attribute
            ranked_workspaces.sort(key=lambda x: x.score, reverse=True)

            span.set_attribute("output.ranked_count", len(ranked_workspaces))
            if ranked_workspaces:
                span.set_attribute("output.top_score", ranked_workspaces[0].score)
            
            return ranked_workspaces
