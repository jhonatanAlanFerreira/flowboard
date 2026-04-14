import json
from typing import Dict, List
from app.clients.local_llm import get_local_json_completion
from app.clients.groq import get_groq_json_completion
from app.observability.phoenix import get_tracer
from app.schemas.data_question import ScoredChunk, DataQuestionResponse
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

    def generate_final_answer(
        self, user_prompt: str, top_chunks: List[ScoredChunk]
    ) -> DataQuestionResponse:
        """
        Calls the LLM to generate the final response using the top-ranked context.
        """
        with tracer.start_as_current_span("agent.generate_answer") as span:
            span.set_attribute("input.query", user_prompt)
            span.set_attribute("input.context_count", len(top_chunks))

            # Format using dot notation for ScoredChunk objects
            tasks_context = ""
            for chunk in top_chunks:
                status = "Completed" if chunk.done else "Pending"
                tasks_context += (
                    f"Chunk ID: {chunk.chunk_id}\n"
                    f"Workspace: {getattr(chunk, 'workspace_name', 'N/A')}\n"
                    f"Content: {chunk.content}\n"
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
                    temperature=agent_config.temperature,
                )
            else:
                response = get_local_json_completion(
                    full_prompt,
                    max_tokens=agent_config.max_tokens,
                    temperature=agent_config.temperature,
                )

            # Safely handle JSON parsing
            try:
                if isinstance(response, str):
                    response_data = json.loads(response)
                else:
                    response_data = response

                # Use Pydantic to validate the LLM output
                final_result = DataQuestionResponse(**response_data)
            except Exception:
                final_result = DataQuestionResponse(
                    markdown_answer="I encountered an error formatting the response.",
                    citations=[],
                )

            span.set_attribute("output.citations", json.dumps(final_result.citations))

            return final_result
