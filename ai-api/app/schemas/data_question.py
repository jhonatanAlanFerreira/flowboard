from pydantic import BaseModel, Field
from typing import Optional

class RetrievedChunk(BaseModel):
    chunk_id: str = Field(..., description="The unique ID of the chunk mapped to MySQL task ID")
    workspace_id: str = Field(..., description="The workspace this chunk belongs to")
    tasklist_id: Optional[str] = Field(None, description="The list this chunk belongs to (nullable)")
    content: str = Field(..., description="The task description or content")
    search_score: float = Field(..., description="The score returned by Weaviate's hybrid search")
    found_in_both: bool = Field(False, description="Flag indicating if the chunk was found in both targeted and global search")
