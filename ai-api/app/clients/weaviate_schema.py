import weaviate.classes.config as wvc
from app.clients.weaviate_client import get_weaviate_client

def create_weaviate_schema():
    client = get_weaviate_client()

    if not client.collections.exists("Workspace"):
        client.collections.create(
            name="Workspace",
            description="To find workspace IDs from names",
            vectorizer_config=wvc.Configure.Vectorizer.text2vec_transformers(),
            properties=[
                wvc.Property(name="chunk_id", data_type=wvc.DataType.TEXT, skip_vectorization=True),
                wvc.Property(name="name", data_type=wvc.DataType.TEXT), 
                wvc.Property(name="workspace_id", data_type=wvc.DataType.TEXT, skip_vectorization=True),
                wvc.Property(
                    name="user_id", data_type=wvc.DataType.TEXT, index_filterable=True, skip_vectorization=True
                ),
            ],
        )

    if not client.collections.exists("Chunk"):
        client.collections.create(
            name="Chunk",
            description="Chunks for semantic search",
            vectorizer_config=wvc.Configure.Vectorizer.text2vec_transformers(),
            properties=[
                wvc.Property(name="chunk_id", data_type=wvc.DataType.TEXT, skip_vectorization=True),
                wvc.Property(name="content", data_type=wvc.DataType.TEXT), 
                wvc.Property(
                    name="tasklist_id",
                    data_type=wvc.DataType.TEXT,
                    index_filterable=True,
                    skip_vectorization=True
                ),
                wvc.Property(
                    name="workspace_id",
                    data_type=wvc.DataType.TEXT,
                    index_filterable=True,
                    skip_vectorization=True
                ),
                wvc.Property(
                    name="user_id", data_type=wvc.DataType.TEXT, index_filterable=True, skip_vectorization=True
                ),
                wvc.Property(
                    name="type", data_type=wvc.DataType.TEXT, index_filterable=True, skip_vectorization=True
                ),
            ],
        )

    if not client.collections.exists("Tag"):
        client.collections.create(
            name="Tag",
            description="Tags for semantic search",
            vectorizer_config=wvc.Configure.Vectorizer.text2vec_transformers(),
            properties=[
                wvc.Property(name="name", data_type=wvc.DataType.TEXT),
            ],
        )
