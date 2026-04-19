from pydantic import BaseModel


class RetrievalWorkflowRequest(BaseModel):
    query: str
    user_id: int
    workspace_ids: list[int] | None = None
