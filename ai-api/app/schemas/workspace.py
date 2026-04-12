from pydantic import BaseModel, Field
from typing import List, Optional


class Task(BaseModel):
    description: str


class TaskList(BaseModel):
    name: str
    tasks: Optional[List[Task]] = Field(default_factory=list)


class Workspace(BaseModel):
    name: str
    lists: List[TaskList]


class AIWorkspacePayload(BaseModel):
    job_id: int
    workspace: Workspace
    source_workspace_ids: Optional[List[int]] = None