from app.celery_app import celery
from app.services.tagging_service import TaggingService
from app.clients.backend_client import BackendClient
from app.schemas.chunk import UpdateTagsPayload
import json
from app.observability.phoenix import get_tracer
from app.services.agents.tagging_agent import TaggingAgent
from app.services.chunk_service import ChunkService
from app.enums.chunk_type import ChunkType
import re

tracer = get_tracer()
tagging_service = TaggingService()
chunk_service = ChunkService()
tag_agent = TaggingAgent()
backend_client = BackendClient()

@celery.task
def generate_tags_task(chunk_id: int, text: str, content: str, tasklist_id: int, workspace_id: int, user_id: int):
    with tracer.start_as_current_span("tagging") as span:
        
        # Fetch known tags semantically related to the text
        known_tags = tagging_service.suggest_tags_for_text(text, limit=5)

        span.set_attribute("chunk.id", chunk_id)
        span.set_attribute("chunk.tasklist_id", tasklist_id)
        span.set_attribute("chunk.workspace_id", workspace_id)
        span.set_attribute("input.text", text)
        span.set_attribute("input.known_tags", known_tags)
        span.set_attribute("input.user_id", user_id)

        # Generate tags using LLM
        data = tag_agent.generate_tags(text, known_tags)

        if isinstance(data, str):
            data = json.loads(data)

        new_tags = data.get("tags", [])
        normalized_tags = [normalize_tag(tag) for tag in new_tags]

        span.set_attribute("output.tags", new_tags)
        span.set_attribute("output.normalized_tags", normalized_tags)

        for tag_name in normalized_tags:
            tagging_service.create_tag_if_not_exists(tag_name)

        payload = UpdateTagsPayload(
            tags=normalized_tags,
        )

        #Insert new tags into Weaviate Tag class
        chunking_res = chunk_service.create_or_update_chunk(chunk_id, content, tasklist_id, workspace_id, user_id, ChunkType.TASK.value)

        span.set_attribute("output.chunking", json.dumps(chunking_res))
        
        # Update backend with new tags for the chunk
        backend_client.put_update_tags(payload, chunk_id)


def normalize_tag(tag: str) -> str:
    tag = tag.strip().lower()
    tag = re.sub(r"[^\w\s-]", "", tag)  # remove special chars
    tag = re.sub(r"[\s-]+", "_", tag)   # spaces/dashes -> underscore
    return tag