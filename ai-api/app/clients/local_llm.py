import os
import json
from llama_cpp import Llama
from app.observability.phoenix import get_tracer

_llm = None  # singleton instance
tracer = get_tracer()

def get_local_llm():
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
            _llm = None

    return _llm

def get_local_json_completion(full_prompt: str, max_tokens: int = 1024, temperature: float = 0.1):
    """
    Executes a local Llama completion with configurable params.
    """
    llm = get_local_llm()
    
    if llm is None:
        raise RuntimeError("Local LLM is not initialized in this container.")
    
    with tracer.start_as_current_span("local_llm_json_completion") as span:
        model_name = os.path.basename(os.getenv("MODEL_PATH", "local_model"))
        span.set_attribute("llm.model_name", model_name)
        span.set_attribute("llm.input.prompt", full_prompt)
        span.set_attribute("llm.config.temperature", temperature)
        span.set_attribute("llm.config.max_tokens", max_tokens)

        # Pass your dynamic params here
        response = llm.create_chat_completion(
            messages=[{"role": "user", "content": full_prompt}],
            response_format={"type": "json_object"},
            max_tokens=max_tokens,
            temperature=temperature
        )

        usage = response["usage"]
        span.set_attribute("llm.token_count.prompt", usage["prompt_tokens"])
        span.set_attribute("llm.token_count.completion", usage["completion_tokens"])
        span.set_attribute("llm.token_count.total", usage["total_tokens"])

        raw_content = response["choices"][0]["message"]["content"]
        data = extract_json_payload(raw_content)
        span.set_attribute("llm.output.json", str(data))

        return data

def extract_json_payload(raw_text: str) -> dict:
    """
    Extracts and parses the first JSON object found in a raw string.
    """
    try:
        start = raw_text.find("{")
        end = raw_text.rfind("}") + 1
        
        if start == -1 or end == 0:
            raise ValueError("No JSON object found in response")
            
        json_str = raw_text[start:end]
        return json.loads(json_str)
        
    except (json.JSONDecodeError, ValueError) as e:
        print(f"Failed to parse Local LLM response: {e}")
        return {}
