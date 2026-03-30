import weaviate
import os

_client = None

def get_weaviate_client():
    global _client

    if _client is None:
        _client = weaviate.Client(
            url=os.getenv("WEAVIATE_URL"),
            startup_period=30
        )

    return _client