from app.celery_app import celery
from app.clients.backend_client import BackendClient
from app.observability.phoenix import get_tracer
from app.services.workspace_chunk_service import WorkspaceService
from app.services.agents.workspace_predictor_agent import WorkspacePredictorAgent
from app.services.data_question.data_question_retrieval_service import DataQuestionRetrievalService
import json

tracer = get_tracer()
backend_client = BackendClient()
workspace_service = WorkspaceService()
workspace_predictor_agent = WorkspacePredictorAgent()
data_question_retrieval_service = DataQuestionRetrievalService()

@celery.task
def search_strategist_task(prompt: str, user_id: int):
    with tracer.start_as_current_span("search_strategist") as span:
        
        span.set_attribute("input.prompt", prompt)
        span.set_attribute("input.user_id", str(user_id))

        try:
            user_workspaces = workspace_service.get_workspace_candidates(user_id, prompt)
            
            span.set_attribute("service.workspaces_source", json.dumps(user_workspaces))

            prediction_result = workspace_predictor_agent.predict_workspace_intent(
                prompt, 
                user_workspaces
            )

            span.set_attribute("agent.output_prediction", json.dumps(prediction_result))

            chunks = data_question_retrieval_service.retrieve_chunks_for_question(prompt, user_id, prediction_result)
             
        except Exception as e:
            span.set_attribute("error", True)
            span.set_attribute("error.message", str(e))
            raise e
