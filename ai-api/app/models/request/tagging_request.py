from pydantic import BaseModel


class TaggingRequest(BaseModel):
    text: str
    content: str
    chunk_id: int
    tasklist_id: int
    workspace_id: int
    user_id: int
