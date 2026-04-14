from pydantic import BaseModel
from typing import List
from app.schemas.workspace import WorkspaceResult

class RetrievalWorkflowResponse(BaseModel):
    workspaces: List[WorkspaceResult]