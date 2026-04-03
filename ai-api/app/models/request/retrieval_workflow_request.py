from pydantic import BaseModel

class RetrievalWorkflowRequest(BaseModel):
    query: str
    user_id: int