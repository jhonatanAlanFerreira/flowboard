from pydantic import BaseModel, Field
from typing import List, Optional


class UpdateTagsPayload(BaseModel):
    tags: List[str]


class TaskListChunk(BaseModel):
    chunk_id: str
    score: float


class TaskListResult(BaseModel):
    tasklist_id: str
    scores: List[float] = Field(default_factory=list)
    chunks: List[TaskListChunk] = Field(default_factory=list)


class TaskListFeatures(BaseModel):
    relevance: float
    volume: int
    concentration: float
    volume_norm: float


class ScoredTaskList(TaskListResult):
    score: float = 0.0
    features: Optional[TaskListFeatures] = None
