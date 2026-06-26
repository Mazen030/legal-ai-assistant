import tempfile
from pathlib import Path
from typing import AsyncIterator

from app.services.document_parser import DocumentParserFactory
from app.services.vector_store import VectorStoreService
from app.services.session_manager import SessionManager, Session
from app.services.llm_service import LLMService
from app.models.schemas import UploadResponse, QueryResponse
from app.core.config import get_settings
from app.core.exceptions import FileTooLargeError


class DocumentQAService:
    """
    Facade that orchestrates the full document Q&A pipeline:
    Upload → Parse → Embed → Retrieve → Answer
    """

    def __init__(self):
        self._settings = get_settings()
        self._parser_factory = DocumentParserFactory()
        self._vector_store = VectorStoreService()
        self._session_manager = SessionManager()
        self._llm_service = LLMService()

    def upload_document(self, filename: str, file_bytes: bytes) -> UploadResponse:
        """Process an uploaded document and create a new session."""
        if len(file_bytes) > self._settings.max_file_size_bytes:
            raise FileTooLargeError(
                f"File exceeds the {self._settings.max_file_size_mb}MB limit."
            )

        # Save to temp file for parsing
        suffix = Path(filename).suffix
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
            tmp.write(file_bytes)
            tmp_path = Path(tmp.name)

        try:
            parser = self._parser_factory.get_parser(tmp_path)
            text, page_count = parser.parse(tmp_path)
        finally:
            tmp_path.unlink(missing_ok=True)

        # Create session and build vector store
        session = self._session_manager.create_session(filename)
        chunk_count = self._vector_store.build_store(session.session_id, text)

        return UploadResponse(
            session_id=session.session_id,
            filename=filename,
            page_count=page_count,
            chunk_count=chunk_count,
            message=f"Document processed successfully. Ready to answer questions.",
        )

    def query(self, session_id: str, question: str) -> QueryResponse:
        """Answer a question about the uploaded document (non-streaming)."""
        session = self._session_manager.get_session(session_id)
        context_docs = self._vector_store.get_relevant_chunks(session_id, question)
        history = session.get_history_for_llm()

        answer = self._llm_service.answer(question, context_docs, history)

        # Update conversation history
        session.add_message("user", question)
        session.add_message("assistant", answer)

        sources = [doc.page_content[:200] + "..." for doc in context_docs]

        return QueryResponse(
            session_id=session_id,
            question=question,
            answer=answer,
            sources=sources,
            history=session.history,
        )

    async def query_stream(
        self, session_id: str, question: str
    ) -> AsyncIterator[str]:
        """Answer a question with streaming response."""
        session = self._session_manager.get_session(session_id)
        context_docs = self._vector_store.get_relevant_chunks(session_id, question)
        history = session.get_history_for_llm()

        # Add user message to history before streaming
        session.add_message("user", question)

        full_answer = []
        async for chunk in self._llm_service.answer_stream(question, context_docs, history):
            full_answer.append(chunk)
            yield chunk

        # Save complete answer to history
        session.add_message("assistant", "".join(full_answer))

    def get_session(self, session_id: str) -> Session:
        return self._session_manager.get_session(session_id)

    def delete_session(self, session_id: str) -> None:
        self._session_manager.delete_session(session_id)
        self._vector_store.remove_store(session_id)

    def list_sessions(self) -> list[Session]:
        return self._session_manager.list_sessions()
