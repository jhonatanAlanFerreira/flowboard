from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class SearchStrategistRequest(BaseModel):
    user_id: int
    prompt: str
    ai_job_id: int
    
class HydratedChunk(BaseModel):
    chunk_id: str = Field(..., description="The unique Weaviate chunk ID")
    workspace_id: str = Field(..., description="The ID of the workspace")
    tasklist_id: Optional[str] = Field(None, description="The list ID (nullable)")
    content: str = Field(..., description="The task description or content")
    search_score: float = Field(..., description="The Weaviate search score")
    found_in_both: bool = Field(..., description="Whether it was found in both targeted and global searches")
    done: bool = Field(..., description="Whether the task is completed")
    created_at: datetime = Field(..., description="Task creation timestamp")
    workspace_name: str = Field(..., description="The human-readable name of the workspace")

class ProcessAnswerRequest(BaseModel):
    ai_job_id: int = Field(..., description="The Laravel AI Job ID to track the process")
    prompt: str = Field(..., description="User's question about its data")
    chunks: List[HydratedChunk] = Field(..., description="The array of hydrated chunks from Laravel")