from app.clients.local_llm import get_local_json_completion
from app.clients.groq import get_groq_json_completion
from typing import List, Dict
from app.observability.phoenix import get_tracer
from app.config import settings
import json

tracer = get_tracer()

class TaggingAgent:
    """
    LLM-based tagging service.
    Returns structured tags:
    - tags: list of tags
    """

    def generate_tags(
    self, text: str, known_tags: List[str] = None) -> Dict[str, List[str]]:
        known_tags = known_tags or []

        with tracer.start_as_current_span("service.generate_tags") as span:

            span.set_attribute("input.text", text)
            span.set_attribute("input.known_tags", known_tags)

            system_prompt = """
            You are a backend service that generates structured data.

            Your task:
            - Read the task description.
            - Select one or more relevant tags from the provided "Known tags".
            - If none of the known tags are suitable, create one or more new tags.

            Rules:
            - Tags must be concise (1-3 words).
            - Avoid duplicates or synonyms of existing tags.
            - Prefer existing tags whenever possible.
            - Output must be valid JSON only (no explanations, no extra text).

            JSON schema (must match exactly):
            {
            "tags": string[]
            }
            """

            user_prompt = f"""
            Task description: "{text}"

            Known tags: {known_tags}
            """

            full_prompt = f"{system_prompt}\n\n{user_prompt}\nJSON:"

            span.set_attribute("llm.prompt", full_prompt)

            if settings.tagging_agent.provider == "groq":
                tags = get_groq_json_completion(
                    full_prompt,
                    settings.tagging_agent.model_name,
                    settings.tagging_agent.max_tokens,
                    settings.tagging_agent.temperature,
                    ).get('tags')
            else:
                tags = get_local_json_completion(
                    full_prompt, 
                    settings.tagging_agent.max_tokens,
                    settings.tagging_agent.temperature,
                ).get('tags')

            try:
                span.set_attribute("output.tags", tags)

                return {
                    "tags": tags
                }

            except (json.JSONDecodeError, ValueError) as e:
                span.set_attribute("parse.success", False)
                span.set_attribute("parse.error", str(e))

                return {
                    "tags": [],
                }