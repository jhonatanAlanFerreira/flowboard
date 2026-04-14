import os
from phoenix.otel import register

_tracer = None


def get_tracer():
    global _tracer

    if _tracer is None:
        endpoint = os.getenv("PHOENIX_ENDPOINT")

        tracer_provider = register(project_name="default", endpoint=endpoint)

        _tracer = tracer_provider.get_tracer(__name__)

    return _tracer
