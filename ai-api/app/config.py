from typing import Literal, Union
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings

class BaseLLMConfig(BaseModel):
    """Common fields for all LLM calls"""
    max_tokens: int = 1024
    temperature: float = 0.1

class LocalLLMConfig(BaseLLMConfig):
    provider: Literal["local"] = "local"
    n_ctx: int = 1024
    n_threads: int = 8

class GroqLLMConfig(BaseLLMConfig):
    provider: Literal["groq"] = "groq"
    model_name: str 

LLMConfig = Union[LocalLLMConfig, GroqLLMConfig]


# Agents config
class Settings(BaseSettings):

    tagging_agent: LLMConfig = LocalLLMConfig(
        max_tokens=80,
        temperature=0.3
    )

    collection_workspace_agent: LLMConfig = GroqLLMConfig(
        model_name="llama-3.3-70b-versatile", 
        max_tokens=2048,
        temperature=0.1
    )
    
    workflow_workspace_agent: LLMConfig = GroqLLMConfig(
        model_name="llama-3.3-70b-versatile", 
        max_tokens=2048,
        temperature=0.1
    )


    workflow_refiner_agent: LLMConfig = GroqLLMConfig(
        model_name="llama-3.3-70b-versatile",
        max_tokens=400,
        temperature=0.0 
    )
    
    workspace_predictor_agent: LLMConfig = LocalLLMConfig(
        max_tokens=300,
        temperature=0.0
    )

settings = Settings()