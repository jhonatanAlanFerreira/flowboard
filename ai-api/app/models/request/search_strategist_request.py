from pydantic import BaseModel


class SearchStrategistRequest(BaseModel):
    user_id: int
    prompt: str