from app.celery_app import celery
from app.services.tagging_service import TaggingService
from app.clients.backend_client import BackendClient
from app.schemas.chunk import UpdateTagsPayload
import json

service = TaggingService()  
backend_client = BackendClient()

@celery.task
def generate_tags_task(chunk_id, text, known_tags):
    data = service.generate_tags(text, known_tags)

    if isinstance(data, str):
        data = json.loads(data)

    payload = UpdateTagsPayload(
        tags = data["tags"],
    )

    backend_client.put_update_tags(payload, chunk_id)