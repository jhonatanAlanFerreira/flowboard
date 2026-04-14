from pydantic import BaseModel
from typing import List


class Chunk(BaseModel):
    chunk_id: int
    score: float
    task_description: str
    tags: List[str]


class TaskListInput(BaseModel):
    tasklist_id: int
    score: float
    relevance: float
    volume: float
    concentration: float
    volume_norm: float
    chunks: List[Chunk]
