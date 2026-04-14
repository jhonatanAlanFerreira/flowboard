from pydantic import BaseModel, Field
from typing import Optional, List
from app.models.request.search_strategist_request import HydratedChunk


class RetrievedChunk(BaseModel):
    chunk_id: str = Field(...)
    workspace_id: str = Field(...)
    tasklist_id: Optional[str] = Field(None)
    content: str = Field(...)
    search_score: float = Field(...)
    found_in_both: bool = Field(False)


class ChunkWeights(BaseModel):
    base: float
    status: float
    overlap: float
    recency: float


class ScoredChunk(HydratedChunk):
    final_calculated_score: float = 0.0
    weights: Optional[ChunkWeights] = None
    llm_relevance_score: int = 0


class DataQuestionResponse(BaseModel):
    markdown_answer: str
    citations: List[str]
