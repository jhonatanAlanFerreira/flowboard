from pydantic import BaseModel
from typing import List

class WorkflowWorkspaceRequest(BaseModel):
    job_id: int
    prompt: str
    lists: List[str]
    average_lists_per_workspace: int