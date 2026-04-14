from typing import List
import weaviate.classes.query as wvc_query
from sentence_transformers import SentenceTransformer
from app.clients.weaviate_client import get_weaviate_client

client = get_weaviate_client()

class TaggingService:
    def __init__(self):
        self.client = client
        self.class_name = "Tag"
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        self.collection = self.client.collections.get(self.class_name)

    def create_tag_if_not_exists(self, name: str):
        # Check if tag exists using filters
        response = self.collection.query.fetch_objects(
            filters=wvc_query.Filter.by_property("name").equal(name),
            limit=1,
            return_properties=["name"]
        )
        
        if response.objects:
            return response.objects[0].properties

        # Create vector for offline embedding
        vector = self.model.encode(name).tolist()

        new_uuid = self.collection.data.insert(
            properties={"name": name},
            vector=vector
        )
        return {"uuid": new_uuid, "name": name}

    def create_tags_if_not_exists(self, names: List[str]):
        return [self.create_tag_if_not_exists(name) for name in names]

    def suggest_tags_for_text(self, text: str, limit: int = 5):
        text_vector = self.model.encode(f"text: {text}").tolist()

        response = self.collection.query.near_vector(
            near_vector=text_vector,
            distance=0.8,
            limit=limit,
            return_metadata=wvc_query.MetadataQuery(distance=True),
            return_properties=["name"]
        )

        return [obj.properties["name"] for obj in response.objects]
