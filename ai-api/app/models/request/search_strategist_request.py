from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class SearchStrategistRequest(BaseModel):
    user_id: int
    prompt: str
    ai_job_id: int
    
class HydratedChunk(BaseModel):
    chunk_id: str = Field(...)
    workspace_id: str = Field(...)
    tasklist_id: Optional[str] = Field(None)
    content: str = Field(...)
    search_score: float = Field(...)
    found_in_both: bool = Field(...)
    done: bool = Field(...)
    created_at: datetime = Field(...)
    workspace_name: str = Field(...)

class ProcessAnswerRequest(BaseModel):
    ai_job_id: int = Field(...)
    prompt: str = Field(...)
    chunks: List[HydratedChunk] = Field(...)