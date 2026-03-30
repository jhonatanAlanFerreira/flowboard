from typing import List
from sentence_transformers import SentenceTransformer
from app.clients.weaviate_client import get_weaviate_client

client = get_weaviate_client()

class TaggingService:
    def __init__(self):
        self.client = client
        self.class_name = "Tag"
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
            
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
                "distance": 0.8
            })
            .with_additional(["distance"])
            .with_limit(limit)
            .do()
        )

        hits = response.get("data", {}).get("Get", {}).get(self.class_name, [])

        return [hit["name"] for hit in hits]