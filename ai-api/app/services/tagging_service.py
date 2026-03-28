from typing import List, Dict
import json
from app.llm import get_llm
from app.observability.phoenix import get_tracer

tracer = get_tracer()


class TaggingService:
    """
    LLM-based tagging service.
    Returns structured tags:
    - tags: list of tags
    """

    def __init__(self):
        self.llm = get_llm()

    def generate_tags(
        self, text: str, known_tags: List[str] = None
    ) -> Dict[str, List[str]]:
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

            with tracer.start_as_current_span("llm.call") as llm_span:
                llm_span.set_attribute("llm.model", "local-llm")

                result = self.llm(
                    full_prompt,
                    max_tokens=80,
                    temperature=0.3
                )

                raw_output = result["choices"][0]["text"].strip()

                llm_span.set_attribute("llm.raw_output", raw_output)

            with tracer.start_as_current_span("parse.response") as parse_span:
                try:
                    data = json.loads(raw_output)

                    if not isinstance(data, dict):
                        raise ValueError("Invalid format")

                    tags = data.get("tags", [])

                    parse_span.set_attribute("parse.success", True)
                    parse_span.set_attribute("output.tags", tags)

                    return {
                        "tags": tags
                    }

                except (json.JSONDecodeError, ValueError) as e:
                    parse_span.set_attribute("parse.success", False)
                    parse_span.set_attribute("parse.error", str(e))
                    parse_span.set_attribute("llm.bad_output", raw_output)

                    return {
                        "tags": [],
                    }