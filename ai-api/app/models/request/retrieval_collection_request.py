from pydantic import BaseModel

class RetrievalCollectionRequest(BaseModel):
    query: str
    user_id: int