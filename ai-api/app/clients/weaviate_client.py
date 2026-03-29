import weaviate

_client = None

def get_weaviate_client():
    global _client

    if _client is None:
        _client = weaviate.Client(
            url="http://dev-weaviate:8080",
            startup_period=30
        )

    return _client