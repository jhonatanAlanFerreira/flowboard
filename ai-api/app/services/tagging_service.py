from typing import List, Dict
import json
from app.llm import get_llm

class TaggingService:
    """
    LLM-based tagging service.
    Returns structured tags:
    - known_tags: subset of provided known tags
    - new_tags: optional new suggestions (can be empty)
    """

    def __init__(self):
        self.llm = get_llm()

    def generate_tags(
        self, text: str, known_tags: List[str] = None
    ) -> Dict[str, List[str]]:
        known_tags = known_tags or []

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

        result = self.llm(
            full_prompt,
            max_tokens=80,
            temperature=0.3
        )

        raw_output = result["choices"][0]["text"].strip()

        # Safe parsing
        try:
            data = json.loads(raw_output)

            if not isinstance(data, dict):
                raise ValueError("Invalid format")

            tags = data.get("tags", [])

            return {
                "tags": tags
            }

        except (json.JSONDecodeError, ValueError):
            return {
                "tags": [],
            }