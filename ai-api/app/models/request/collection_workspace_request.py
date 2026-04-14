from pydantic import BaseModel
from typing import List


class TaskList(BaseModel):
    name: str
    tasks: List[str]


class CollectionWorkspaceRequest(BaseModel):
    job_id: int
    prompt: str
    lists: List[TaskList]
    average_tasks_per_list: int
    average_lists_per_workspace: int
