import weaviate
import os

_client = None

def get_weaviate_client():
    global _client

    if _client is None:
        _client = weaviate.connect_to_custom(
            http_host=os.getenv("WEAVIATE_URL"),
            grpc_host=os.getenv("WEAVIATE_URL"),
            http_port=8080,                      
            grpc_port=50051,                     
            http_secure=False,                   
            grpc_secure=False,                   
        )

    return _client
