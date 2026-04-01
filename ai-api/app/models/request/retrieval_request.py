from pydantic import BaseModel


class RetrievalRequest(BaseModel):
    query: str
    user_id: int