from app.celery_app import celery
from app.clients.backend_client import BackendClient
from app.observability.phoenix import get_tracer
import json
from typing import List
from pydantic.json import pydantic_encoder

tracer = get_tracer()
backend_client = BackendClient()

@celery.task
def rank_and_generate_task(user_prompt: str, job_id: str, chunks: List[dict]):
    with tracer.start_as_current_span("rank_and_generate_task") as span:

        span.set_attribute("job.id", job_id)
        span.set_attribute("input.prompt", user_prompt)
        span.set_attribute("input.chunks", json.dumps(chunks, default=pydantic_encoder))