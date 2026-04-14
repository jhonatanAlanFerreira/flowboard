from pydantic import BaseModel
from typing import List


class Pattern(BaseModel):
    tag: str
    score: float
    task: str


class TaskListPatterns(BaseModel):
    tasklist_id: int
    patterns: List[Pattern]


class ExtractPatternsResponse(BaseModel):
    results: List[TaskListPatterns]
