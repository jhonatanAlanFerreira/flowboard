from pydantic import BaseModel
from typing import List


class WorkspaceResult(BaseModel):
    workspace_id: str
    score: float
    max_score: float
    match_count: int
    chunk_id: str
    final_score: float


class RetrievalWorkflowResponse(BaseModel):
    workspaces: List[WorkspaceResult]