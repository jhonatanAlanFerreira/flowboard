from typing import List
import weaviate.classes.query as wvc_query
from app.clients.weaviate_client import get_weaviate_client

client = get_weaviate_client()


class TaggingService:
    def __init__(self):
        self.client = client
        self.class_name = "Tag"
        self.collection = self.client.collections.get(self.class_name)

    def create_tag_if_not_exists(self, name: str):
        # Check if tag exists using filters
        response = self.collection.query.fetch_objects(
            filters=wvc_query.Filter.by_property("name").equal(name),
            limit=1,
            return_properties=["name"],
        )

        if response.objects:
            return response.objects[0].properties

        new_uuid = self.collection.data.insert(properties={"name": name})
        return {"uuid": new_uuid, "name": name}

    def create_tags_if_not_exists(self, names: List[str]):
        return [self.create_tag_if_not_exists(name) for name in names]

    def suggest_tags_for_text(self, text: str, limit: int = 5):
        response = self.collection.query.near_text(
            query=f"text: {text}",
            distance=0.8,
            limit=limit,
            return_metadata=wvc_query.MetadataQuery(distance=True),
            return_properties=["name"],
        )

        return [obj.properties["name"] for obj in response.objects]
