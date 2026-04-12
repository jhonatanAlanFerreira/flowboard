from app.celery_app import celery
from app.clients.backend_client import BackendClient
from app.observability.phoenix import get_tracer
import json
from typing import List
from pydantic.json import pydantic_encoder
from app.services.data_question.data_question_scoring_service import DataQuestionScoringService
from app.services.agents.data_question_reranker_agent import DataQuestionRerankerAgent
from app.services.agents.data_question_generator_agent import DataQuestionGeneratorAgent

tracer = get_tracer()
backend_client = BackendClient()
data_question_scoring_service = DataQuestionScoringService()
data_question_reranker_agent = DataQuestionRerankerAgent()
data_question_generator_agent = DataQuestionGeneratorAgent()

@celery.task
def rank_and_generate_task(user_prompt: str, job_id: str, chunks: List[dict]):
    with tracer.start_as_current_span("rank_and_generate_task") as span:

        span.set_attribute("job.id", job_id)
        span.set_attribute("input.prompt", user_prompt)
        span.set_attribute("input.first_20_chunks", json.dumps(chunks[:20], default=pydantic_encoder))
        
        top_candidates = data_question_scoring_service.score_and_rank_chunks(user_prompt, chunks)
        
        re_ranked_chunks = data_question_reranker_agent.rerank_tasks(user_prompt, top_candidates)
        
        final_context = re_ranked_chunks[:5]
        
        result = data_question_generator_agent.generate_final_answer(user_prompt, final_context)
        
        markdown_answer = result.get("markdown_answer")
        citations = result.get("citations", [])

        backend_client.complete_data_question(job_id, markdown_answer, citations)

        span.set_attribute("output.answer", markdown_answer)