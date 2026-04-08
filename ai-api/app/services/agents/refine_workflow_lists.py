from app.clients.local_llm import get_local_json_completion
from app.clients.groq import get_groq_json_completion
from typing import List, Dict
from app.observability.phoenix import get_tracer
from app.config import settings
import json

tracer = get_tracer()

class WorkflowRefinerAgent:
    """
    LLM-based agent to refine workflow lists.
    - Removes semantic duplicates.
    - Filters lists irrelevant to the user prompt.
    - Organizes lists into a logical sequence.
    """

    def refine_workflow_lists(self, user_prompt: str, candidate_lists: List[str]) -> Dict[str, List[str]]:
        with tracer.start_as_current_span("service.refine_workflow_lists") as span:
            span.set_attribute("input.user_prompt", user_prompt)
            span.set_attribute("input.candidate_lists", candidate_lists)

            system_prompt = """
            You are a Workflow Architect backend service.
            
            Your task:
            1. Analyze the User Request and the Candidate Workflow Lists.
            2. Filter: Remove any lists that are irrelevant to the specific User Request.
            3. Deduplicate: Merge semantic duplicates (e.g., if 'To Do' and 'Tasks' both exist, keep one).
            4. Sequence: Arrange the remaining lists in a logical start-to-finish order.

            Rules:
            - Keep only the most relevant lists (usually 3-7 lists).
            - Output must be valid JSON only.
            - Do not invent new lists unless the candidates are completely empty or insufficient.

            JSON schema:
            {
              "refined_lists": string[]
            }
            """

            prompt_content = f"""
            User Request: "{user_prompt}"
            Candidate Lists: {candidate_lists}
            """

            full_prompt = f"{system_prompt}\n\n{prompt_content}\nJSON:"
            span.set_attribute("llm.prompt", full_prompt)

            agent_config = settings.workflow_refiner_agent
            
            if agent_config.provider == "groq":
                response = get_groq_json_completion(
                    full_prompt,
                    model_name=agent_config.model_name,
                    max_tokens=agent_config.max_tokens,
                    temperature=agent_config.temperature
                )
            else:
                response = get_local_json_completion(
                    full_prompt,
                    max_tokens=agent_config.max_tokens,
                    temperature=agent_config.temperature
                )

            refined_lists = response.get('refined_lists', [])

            try:
                span.set_attribute("output.refined_lists", refined_lists)
                return {
                    "refined_lists": refined_lists
                }

            except Exception as e:
                span.record_exception(e)
                span.set_attribute("parse.success", False)
                return {
                    "refined_lists": []
                }
