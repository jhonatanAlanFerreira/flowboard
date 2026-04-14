import json
from typing import Dict, List
from app.clients.local_llm import get_local_json_completion
from app.clients.groq import get_groq_json_completion
from app.observability.phoenix import get_tracer
from app.config import settings
from app.schemas.data_question import ScoredChunk

tracer = get_tracer()


class DataQuestionRerankerAgent:
    """
    Acts as a judge to evaluate how relevant retrieved tasks are to the user's question.
    """

    SYSTEM_PROMPT = """
    You are an expert Information Retrieval Judge. Your job is to read a user's question and a list of tasks, then score each task from 1 to 10 based on how helpful it is to answer the question.

    SCORING CRITERIA:
    - 10: The task contains the exact answer or highly critical information for the user's question.
    - 5-7: The task is topically related but might not fully answer the question.
    - 1: The task is completely irrelevant or noise.

    STRICT RULES:
    - You must evaluate every task provided in the list.
    - Output MUST strictly adhere to the requested JSON schema. Return ONLY valid JSON.
    """

    def rerank_tasks(
        self, user_prompt: str, candidate_chunks: List[ScoredChunk]
    ) -> List[ScoredChunk]:
        """
        Calls the LLM to score candidate tasks and sorts them by LLM relevance.
        """
        with tracer.start_as_current_span("agent.llm_rerank") as span:
            span.set_attribute("input.query", user_prompt)
            span.set_attribute("input.candidate_count", len(candidate_chunks))

            tasks_input = ""
            for idx, chunk in enumerate(candidate_chunks):
                tasks_input += (
                    f"Index: {idx} | ID: {chunk.chunk_id} | Task: {chunk.content}\n"
                )

            full_prompt = f"""
            {self.SYSTEM_PROMPT}

            USER QUESTION: 
            "{user_prompt}"

            TASKS TO EVALUATE:
            {tasks_input}

            JSON SCHEMA EXPECTED:
            {{
                "evaluations": [
                    {{
                        "chunk_id": "string",
                        "score": integer,
                        "reasoning": "string"
                    }}
                ]
            }}
            """

            span.set_attribute("llm.prompt", full_prompt)

            # Using the same agent config fallback pattern you have
            agent_config = settings.data_question_reranker_agent

            if agent_config.provider == "groq":
                response = get_groq_json_completion(
                    full_prompt,
                    model_name=agent_config.model_name,
                    max_tokens=agent_config.max_tokens,
                    temperature=agent_config.temperature,
                )
            else:
                response = get_local_json_completion(
                    full_prompt,
                    max_tokens=agent_config.max_tokens,
                    temperature=agent_config.temperature,
                )

            # Safely handle JSON parsing
            if isinstance(response, str):
                try:
                    response = json.loads(response)
                except Exception:
                    response = {"evaluations": []}

            evaluations = response.get("evaluations", [])
            score_map = {
                str(ev.get("chunk_id")): ev.get("score", 0) for ev in evaluations
            }

            for chunk in candidate_chunks:
                chunk.llm_relevance_score = score_map.get(str(chunk.chunk_id), 1)

            # Sort the objects by attribute
            reranked_chunks = sorted(
                candidate_chunks, key=lambda x: x.llm_relevance_score, reverse=True
            )

            span.set_attribute(
                "output.top_score",
                reranked_chunks[0].llm_relevance_score if reranked_chunks else 0,
            )

            return reranked_chunks
