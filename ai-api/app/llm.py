from llama_cpp import Llama
import os

_llm = None  # singleton instance


def get_llm():
    global _llm

    if _llm is None:
        _llm = Llama(
            model_path=os.getenv(
                "MODEL_PATH"
            ),
            n_ctx=1024,
            n_threads=8,
            n_batch=512,
            use_mmap=True,
            use_mlock=True
        )

    return _llm