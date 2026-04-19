import os
import json
import hashlib
import redis
from groq import Groq
from app.observability.phoenix import get_tracer

_groq_client = None
_redis_client = None
tracer = get_tracer()


def get_redis_client():
    """
    Initializes a Redis client using environment variables.
    """
    global _redis_client
    if _redis_client is None:
        _redis_client = redis.Redis(
            host="dev-redis",
            port=int(os.getenv("REDIS_PORT", 6379)),
            db=0,
            decode_responses=True
        )
    return _redis_client


def get_groq_client():
    global _groq_client
    if _groq_client is None:
        if os.getenv("LOAD_LLM", "0") == "1":
            api_key = os.getenv("GROQ_API_KEY")
            if not api_key:
                raise ValueError("GROQ_API_KEY environment variable is not set")
            _groq_client = Groq(api_key=api_key)
    return _groq_client


def get_groq_json_completion(
    full_prompt: str,
    model_name: str = "llama-3.3-70b-versatile",
    max_tokens: int = 1024,
    temperature: float = 0.1,
) -> dict:
    """
    Executes a Groq chat completion with Redis caching and Phoenix tracing.
    """
    client = get_groq_client()
    redis_client = get_redis_client()

    if client is None:
        raise RuntimeError("Groq client is not initialized in this container.")

    # Create a unique cache key based on model, temp, and prompt
    cache_input = f"{model_name}_{temperature}_{full_prompt}"
    cache_key = f"llm_cache:{hashlib.md5(cache_input.encode()).hexdigest()}"

    with tracer.start_as_current_span("groq_json_completion") as span:
        # Check Cache
        try:
            cached_res = redis_client.get(cache_key)
            if cached_res:
                span.set_attribute("llm.cache_hit", True)
                return json.loads(cached_res)
        except Exception as e:
            print(f"Redis error: {e}")

        # If not cached, proceed to LLM
        span.set_attribute("llm.cache_hit", False)
        span.set_attribute("llm.model_name", model_name)
        span.set_attribute("llm.input.prompt", full_prompt)
        span.set_attribute("llm.config.temperature", temperature)
        span.set_attribute("llm.config.max_tokens", max_tokens)

        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": full_prompt}],
            model=model_name,
            response_format={"type": "json_object"},
            max_tokens=max_tokens,
            temperature=temperature,
        )

        # Extract Usage Metrics
        usage = chat_completion.usage
        span.set_attribute("llm.token_count.prompt", usage.prompt_tokens)
        span.set_attribute("llm.token_count.completion", usage.completion_tokens)
        span.set_attribute("llm.token_count.total", usage.total_tokens)

        # Extract and Parse Content
        raw_content = chat_completion.choices[0].message.content
        data = extract_json_payload(raw_content)

        # Save to Cache (Expires in 24 hours)
        if data:
            try:
                redis_client.setex(cache_key, 86400, json.dumps(data))
            except Exception as e:
                print(f"Failed to write to Redis: {e}")

        span.set_attribute("llm.output.json", str(data))

        return data


def extract_json_payload(raw_text: str) -> dict:
    try:
        start = raw_text.find("{")
        end = raw_text.rfind("}") + 1
        if start == -1 or end == 0:
            raise ValueError("No JSON object found in response")
        return json.loads(raw_text[start:end])
    except (json.JSONDecodeError, ValueError) as e:
        print(f"Failed to parse LLM response: {e}")
        return {}
