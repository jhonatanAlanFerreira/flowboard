import json
from typing import Dict, List
from app.clients.local_llm import get_local_json_completion
from app.clients.groq import get_groq_json_completion
from app.observability.phoenix import get_tracer
from app.config import settings

tracer = get_tracer()

class DataQuestionGeneratorAgent:
    """
    Synthesizes the final answer for the user based on the top retrieved tasks.
    """

    SYSTEM_PROMPT = """
    You are a helpful and highly accurate virtual assistant for a task management app. 
    Your job is to answer the user's question using ONLY the provided tasks.

    STRICT RULES:
    1. Base your answer strictly on the provided context. If the tasks do not contain the answer, state that you cannot find the information.
    2. Do NOT hallucinate or assume details not present in the text.
    3. Whenever you reference a task, you MUST state which Workspace it belongs to and use its natural text description or summary.
    4. Provide your response in a clean, readable Markdown format.
    5. Return your result strictly according to the requested JSON schema.

    VISIBILITY RULES REGARDING IDs:
    - You must NOT include, mention, or print any chunk IDs or task IDs (e.g., "1803") in your `markdown_answer`.
    - Treat IDs as strictly hidden system fields. If you need to cite or point to a task in the `markdown_answer`, use its text description.
    - Return the actual string IDs ONLY inside the `citations` list in the JSON payload.
    """

    def generate_final_answer(self, user_prompt: str, top_chunks: List[Dict]) -> Dict:
        """
        Calls the LLM to generate the final response using the top-ranked context.
        """
        with tracer.start_as_current_span("agent.generate_answer") as span:
            span.set_attribute("input.query", user_prompt)
            span.set_attribute("input.context_count", len(top_chunks))

            # Format the tasks into a clear structure for the generator LLM
            tasks_context = ""
            for chunk in top_chunks:
                status = "Completed" if chunk.get("done") else "Pending"
                tasks_context += (
                    f"Chunk ID: {chunk.get('chunk_id')}\n"
                    f"Workspace: {chunk.get('workspace_name')}\n"
                    f"Content: {chunk.get('content')}\n"
                    f"Status: {status}\n"
                    "-----------------\n"
                )

            full_prompt = f"""
            {self.SYSTEM_PROMPT}

            RELEVANT TASKS:
            {tasks_context}

            USER QUESTION: 
            "{user_prompt}"

            JSON SCHEMA EXPECTED:
            {{
                "markdown_answer": "string",
                "citations": ["string"]
            }}
            
            NOTE: In the citations list, return the string Chunk IDs of the tasks you actually used to answer the question.
            """

            span.set_attribute("llm.prompt", full_prompt)
            
            agent_config = settings.data_question_generator_agent
            
            if agent_config.provider == "groq":
                response = get_groq_json_completion(
                    full_prompt,
                    model_name=agent_config.model_name,
                    max_tokens=agent_config.max_tokens,
                    temperature=agent_config.temperature
                )
            else:
                response = get_local_json_completion(
                    full_prompt,
                    max_tokens=agent_config.max_tokens,
                    temperature=agent_config.temperature
                )

            # Safely handle JSON parsing
            if isinstance(response, str):
                try:
                    response = json.loads(response)
                except Exception:
                    response = {
                        "markdown_answer": "I encountered an error formatting the response.",
                        "citations": []
                    }

            span.set_attribute("output.citations", json.dumps(response.get("citations")))
            
            return response
