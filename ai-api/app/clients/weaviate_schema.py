from app.clients.weaviate_client import get_weaviate_client

def create_weaviate_schema():
    client = get_weaviate_client()

    # Tag class
    tag_class = {
        "class": "Tag",
        "description": "Tags for semantic search",
        "vectorizer": "none",  # We'll provide vectors manually
        "properties": [
            {"name": "name", "dataType": ["text"]}
        ]
    }

    # Chunk class
    chunk_class = {
        "class": "Chunk",
        "description": "Chunks for semantic search",
        "vectorizer": "none",  # We'll provide vectors manually
        "properties": [
            {"name": "chunk_id", "dataType": ["string"]},       
            {"name": "tasklist_id", "dataType": ["string"]},   
            {"name": "workspace_id", "dataType": ["string"]}   
        ]
    }

    if not client.schema.exists("Chunk"):
        client.schema.create_class(chunk_class)

    if not client.schema.exists("Tag"):
        client.schema.create_class(tag_class)