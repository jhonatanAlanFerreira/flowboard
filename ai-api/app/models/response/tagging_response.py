from pydantic import BaseModel


class TaggingResponse(BaseModel):
    status: str
