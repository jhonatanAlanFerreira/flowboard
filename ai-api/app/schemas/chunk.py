from pydantic import BaseModel
from typing import List

class UpdateTagsPayload(BaseModel):
    tags: List[str]