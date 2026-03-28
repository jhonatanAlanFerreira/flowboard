from pydantic import BaseModel
from typing import List


class TaggingRequest(BaseModel):
    text: str
    known_tags: List[str]
    chunk_id: int