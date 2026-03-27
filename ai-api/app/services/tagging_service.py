from typing import List
import json
from app.llm import get_llm

class TaggingService:
    """
    LLM-based tagging service.
    Accepts a list of known tags from Laravel, can suggest new ones.
    """

    def __init__(self):
        self.llm = get_llm()

    def generate_tags(self, text: str, known_tags: List[str] = None) -> List[str]:
        """
        text: task description
        known_tags: tags Laravel already uses
        returns: suggested tags (subset of known_tags + optionally 1 new tag)
        """
        known_tags = known_tags or []

        system_prompt = (
            "You are a tagging assistant. "
            "You MUST return a JSON list of tags. "
            "Use only the tags provided, but if a new useful tag is obvious, include one extra tag. "
            "Do not include duplicates. Return only JSON."
            "Return ONLY a valid JSON array of strings."
            "Create a maximum of 3 tags"

            "DO NOT explain."
            "DO NOT add text."
            "DO NOT add code."
            "DO NOT add markdown."
        )

        user_prompt = f"""
            Task description: "{text}"

            Known tags: {known_tags}

            Return a JSON list of tags.
        """

        full_prompt = f"{system_prompt}\n\n{user_prompt}\nJSON:"
        
        result = self.llm(
            full_prompt,
            max_tokens=64,
            temperature=0.2
        )

        raw_output = result["choices"][0]["text"].strip()
        
        # Parse JSON safely
        try:
            tags = json.loads(raw_output)
            if not isinstance(tags, list):
                tags = []
        except json.JSONDecodeError:
            # fallback to empty list if LLM output fails
            tags = []

        return tags