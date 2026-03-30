from pydantic import BaseModel
from typing import List


class Task(BaseModel):
    description: str


class TaskList(BaseModel):
    name: str
    tasks: List[Task]


class Workflow(BaseModel):
    name: str
    lists: List[TaskList]


class AIWorkspacePayload(BaseModel):
    job_id: int
    workflow: Workflow