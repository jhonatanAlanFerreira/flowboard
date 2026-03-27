from pydantic import BaseModel
from typing import List, Dict


class TaggingRequest(BaseModel):
    text: str
    known_tags: List[Dict]
    chunk_id: int