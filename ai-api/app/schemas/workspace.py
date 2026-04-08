from pydantic import BaseModel
from typing import List, Optional


class Task(BaseModel):
    description: str


class TaskList(BaseModel):
    name: str
    tasks: Optional[List[Task]]


class Workspace(BaseModel):
    name: str
    lists: List[TaskList]


class AIWorkspacePayload(BaseModel):
    job_id: int
    workspace: Workspace