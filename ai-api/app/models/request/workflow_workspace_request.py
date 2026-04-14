from pydantic import BaseModel
from typing import List


class WorkflowLists(BaseModel):
    workspace_id: int
    lists: List[str]


class WorkflowWorkspaceRequest(BaseModel):
    job_id: int
    prompt: str
    workflowLists: List[WorkflowLists]
    average_lists_per_workspace: int
