from typing import List, Dict
import json
from app.llm import get_llm
from app.observability.phoenix import get_tracer
from sentence_transformers import SentenceTransformer
from app.clients.weaviate_client import get_weaviate_client

tracer = get_tracer()
client = get_weaviate_client()

class TaggingService:
    """
    LLM-based tagging service.
    Returns structured tags:
    - tags: list of tags
    """

    def __init__(self):
        self.llm = get_llm()
        self.client = client
        self.class_name = "Tag"
        self.model = SentenceTransformer("all-MiniLM-L6-v2")

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
            
    def create_tag_if_not_exists(self, name: str):
            # Check if tag exists
            existing = (
                self.client.query
                .get(self.class_name, ["name"])
                .with_where({"path": ["name"], "operator": "Equal", "valueText": name})
                .with_limit(1)
                .do()
            )
            hits = existing.get("data", {}).get("Get", {}).get(self.class_name, [])
            if hits:
                return hits[0]

            # Create vector for offline embedding
            vector = self.model.encode(name).tolist()

            return self.client.data_object.create(
                data_object={"name": name},
                class_name=self.class_name,
                vector=vector
            )

    def create_tags_if_not_exists(self, names: List[str]):
        return [self.create_tag_if_not_exists(name) for name in names]
    

    def suggest_tags_for_text(self, text: str, limit: int = 5):
        text_vector = self.model.encode(f"text: {text}").tolist()

        response = (
            self.client.query
            .get(self.class_name, ["name"])
            .with_near_vector({
                "vector": text_vector,
                "distance": 0.6
            })
            .with_additional(["distance"])
            .with_limit(limit)
            .do()
        )

        hits = response.get("data", {}).get("Get", {}).get(self.class_name, [])

        return [hit["name"] for hit in hits]