from typing import AsyncIterator
import anthropic

from app.core.config import get_settings
from langchain.schema import Document


SYSTEM_PROMPT = """You are an expert legal document analyst assistant working for a legal-tech company.
Your role is to help users understand legal agreements, contracts, and policy documents accurately and clearly.

Guidelines:
- Answer ONLY based on the provided document context. Do not use outside knowledge.
- If the answer is not found in the context, clearly state: "I could not find information about this in the document."
- Be precise and cite relevant sections or clauses when possible.
- Use plain language to explain complex legal terms when appropriate.
- Maintain a professional, neutral tone.
- Keep conversation history in mind when answering follow-up questions.
"""


class LLMService:
    """
    Handles all interactions with the Anthropic Claude API.
    Supports both standard and streaming responses.
    """

    def __init__(self):
        self._settings = get_settings()
        self._client = anthropic.Anthropic(api_key=self._settings.anthropic_api_key)
        self._async_client = anthropic.AsyncAnthropic(api_key=self._settings.anthropic_api_key)

    def _build_user_message(self, question: str, context_docs: list[Document]) -> str:
        context = "\n\n---\n\n".join(
            f"[Chunk {i+1}]:\n{doc.page_content}"
            for i, doc in enumerate(context_docs)
        )
        return (
            f"Document Context:\n{context}\n\n"
            f"---\n\n"
            f"Question: {question}"
        )

    def answer(
        self,
        question: str,
        context_docs: list[Document],
        history: list[dict],
    ) -> str:
        """Generate a complete answer (non-streaming)."""
        user_message = self._build_user_message(question, context_docs)

        messages = history + [{"role": "user", "content": user_message}]

        response = self._client.messages.create(
            model=self._settings.model_name,
            max_tokens=self._settings.max_tokens,
            system=SYSTEM_PROMPT,
            messages=messages,
        )
        return response.content[0].text

    async def answer_stream(
        self,
        question: str,
        context_docs: list[Document],
        history: list[dict],
    ) -> AsyncIterator[str]:
        """Generate a streaming answer, yielding text chunks."""
        user_message = self._build_user_message(question, context_docs)
        messages = history + [{"role": "user", "content": user_message}]

        async with self._async_client.messages.stream(
            model=self._settings.model_name,
            max_tokens=self._settings.max_tokens,
            system=SYSTEM_PROMPT,
            messages=messages,
        ) as stream:
            async for text in stream.text_stream:
                yield text
