from app.clients.weaviate_client import get_weaviate_client

def create_weaviate_schema():
    client = get_weaviate_client()

    tag_class = {
        "class": "Tag",
        "description": "Tags for semantic search",
        "vectorizer": "none",  # We'll provide vectors manually
        "properties": [
            {"name": "name", "dataType": ["text"]}
        ]
    }

    chunk_class = {
        "class": "Chunk",
        "description": "Chunks for semantic search",
        "vectorizer": "none",  # We'll provide vectors manually
        "properties": [
            {"name": "chunk_id", "dataType": ["string"]},
            {"name": "content", "dataType": ["string"]},
            {"name": "tasklist_id", "dataType": ["string"], "indexFilterable": True},
            {"name": "workspace_id", "dataType": ["string"], "indexFilterable": True},
            {"name": "user_id", "dataType": ["string"], "indexFilterable": True},
            {"name": "type", "dataType": ["string"], "indexFilterable": True},
        ]
    }
    
    workspace_class = {
    "class": "Workspace",
    "description": "To find workspace IDs from names",
    "vectorizer": "none", # We'll provide vectors manually
    "properties": [
        {"name": "chunk_id", "dataType": ["string"]},
        {"name": "name", "dataType": ["text"]},
        {"name": "workspace_id", "dataType": ["string"]},
        {"name": "user_id", "dataType": ["string"], "indexFilterable": True},
    ]
}
    
    if not client.schema.exists("Workspace"):
        client.schema.create_class(workspace_class)

    if not client.schema.exists("Chunk"):
        client.schema.create_class(chunk_class)

    if not client.schema.exists("Tag"):
        client.schema.create_class(tag_class)