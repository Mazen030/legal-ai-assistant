from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import StreamingResponse

from app.services.document_qa import DocumentQAService
from app.models.schemas import (
    UploadResponse, QueryRequest, QueryResponse, SessionInfo, ErrorResponse
)
from app.core.exceptions import (
    DocumentProcessingError, UnsupportedFileTypeError,
    FileTooLargeError, SessionNotFoundError, VectorStoreError,
)

router = APIRouter(prefix="/api/v1", tags=["documents"])


def get_qa_service() -> DocumentQAService:
    """Dependency injection for DocumentQAService (singleton via module-level instance)."""
    return _qa_service


# Module-level singleton (simple DI without a full IoC container)
_qa_service = DocumentQAService()


@router.post("/upload", response_model=UploadResponse)
async def upload_document(file: UploadFile = File(...)):
    """Upload a PDF or DOCX document to start a Q&A session."""
    try:
        contents = await file.read()
        return _qa_service.upload_document(file.filename, contents)
    except (UnsupportedFileTypeError, FileTooLargeError) as e:
        raise HTTPException(status_code=400, detail=str(e))
    except DocumentProcessingError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except VectorStoreError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/query", response_model=QueryResponse)
async def query_document(request: QueryRequest):
    """Ask a question about a previously uploaded document."""
    try:
        return _qa_service.query(request.session_id, request.question)
    except SessionNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except VectorStoreError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/query/stream")
async def query_document_stream(request: QueryRequest):
    """Ask a question with a streaming response (Server-Sent Events)."""
    try:
        # Validate session exists before starting stream
        _qa_service.get_session(request.session_id)
    except SessionNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

    async def event_generator():
        try:
            async for chunk in _qa_service.query_stream(request.session_id, request.question):
                # SSE format
                yield f"data: {chunk}\n\n"
        except Exception as e:
            yield f"data: [ERROR] {str(e)}\n\n"
        finally:
            yield "data: [DONE]\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/session/{session_id}", response_model=SessionInfo)
async def get_session_info(session_id: str):
    """Get metadata and message count for a session."""
    try:
        session = _qa_service.get_session(session_id)
        return SessionInfo(
            session_id=session.session_id,
            filename=session.filename,
            created_at=session.created_at,
            message_count=session.message_count,
        )
    except SessionNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/session/{session_id}")
async def delete_session(session_id: str):
    """Delete a session and free its resources."""
    try:
        _qa_service.delete_session(session_id)
        return {"message": f"Session {session_id} deleted successfully."}
    except SessionNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/sessions", response_model=list[SessionInfo])
async def list_sessions():
    """List all active sessions."""
    sessions = _qa_service.list_sessions()
    return [
        SessionInfo(
            session_id=s.session_id,
            filename=s.filename,
            created_at=s.created_at,
            message_count=s.message_count,
        )
        for s in sessions
    ]
