from app.celery_app import celery
from celery.utils.log import get_task_logger
from app.services.generate_workflow_service import GenerateWorkflowService

service = GenerateWorkflowService()  

logger = get_task_logger(__name__)

@celery.task
def generate_workflow_task(user_prompt: str):
    workspace_data = service.generate_workspace_llm(user_prompt)

    logger.info(workspace_data)