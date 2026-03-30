from llama_cpp import Llama
import os

_llm = None  # singleton instance


def get_llm():
    """
    Returns a singleton Llama instance.
    Loads the model only if LOAD_LLM=1.
    """

    global _llm

    if _llm is None:
        if os.getenv("LOAD_LLM", "0") == "1":
            model_path = os.getenv("MODEL_PATH")
            if not model_path:
                raise ValueError("MODEL_PATH environment variable is not set")

            _llm = Llama(
                model_path=model_path,
                n_ctx=1024,
                n_threads=8,
                n_batch=512,
                use_mmap=True,
                use_mlock=True,
            )
        else:
            # API container or other services won’t load the model
            _llm = None

    return _llm