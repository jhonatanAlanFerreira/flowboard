from app.celery_app import celery
from app.services.tagging_service import TaggingService
from celery.utils.log import get_task_logger

service = TaggingService()  

logger = get_task_logger(__name__)

@celery.task
def generate_tags_task(chunk_id, text, known_tags):
    tags = service.generate_tags(text, known_tags)

    logger.info(tags)
    logger.info(f"Tags for chunk id: {chunk_id}")