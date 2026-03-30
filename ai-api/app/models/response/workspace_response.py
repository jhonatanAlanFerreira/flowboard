from pydantic import BaseModel

class WorkflowResponse(BaseModel):
    status: str