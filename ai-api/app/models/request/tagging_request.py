from pydantic import BaseModel


class TaggingRequest(BaseModel):
    text: str
    content: str
    chunk_id: int