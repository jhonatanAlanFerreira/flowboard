from pydantic import BaseModel


class TaggingRequest(BaseModel):
    text: str
    chunk_id: int