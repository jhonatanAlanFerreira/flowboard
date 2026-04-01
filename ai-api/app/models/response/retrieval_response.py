from pydantic import BaseModel
from typing import List


class WorkspaceResult(BaseModel):
    workspace_id: str
    score: float


class RetrievalResponse(BaseModel):
    results: List[WorkspaceResult]