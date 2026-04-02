from pydantic import BaseModel
from typing import List


class ChunkResult(BaseModel):
    chunk_id: str
    score: float

class TaskListResult(BaseModel):
    tasklist_id: str
    score: float
    relevance: float
    volume: int
    concentration: float
    volume_norm: float
    chunks: List[ChunkResult]

class RetrievalResponse(BaseModel):
    lists: List[TaskListResult]