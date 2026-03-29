from app.celery_app import celery
from app.services.tagging_service import TaggingService
from app.clients.backend_client import BackendClient
from app.schemas.chunk import UpdateTagsPayload
import json
from app.observability.phoenix import get_tracer
from app.services.agents.tagging_agent import TaggingAgent

tracer = get_tracer()
service = TaggingService()
tag_agent = TaggingAgent()
backend_client = BackendClient()

@celery.task
def generate_tags_task(chunk_id, text):
    with tracer.start_as_current_span("tagging") as span:
        
        # Fetch known tags semantically related to the text
        known_tags = service.suggest_tags_for_text(text, limit=5)

        span.set_attribute("chunk.id", chunk_id)
        span.set_attribute("input.text", text)
        span.set_attribute("input.known_tags", known_tags)

        # Generate tags using LLM or other logic
        data = tag_agent.generate_tags(text, known_tags)

        if isinstance(data, str):
            data = json.loads(data)

        # Insert new tags into Weaviate Tag class
        new_tags = data.get("tags", [])
        span.set_attribute("output.tags", new_tags)

        for tag_name in new_tags:
            service.create_tag_if_not_exists(tag_name)

        # Update backend with new tags for the chunk
        payload = UpdateTagsPayload(
            tags=new_tags,
        )
        backend_client.put_update_tags(payload, chunk_id)