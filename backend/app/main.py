from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routes import router
from app.core.config import get_settings
from app.core.exceptions import LegalAIException

settings = get_settings()

app = FastAPI(
    title="Legal AI Assistant",
    description="AI-powered assistant for legal document analysis",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(LegalAIException)
async def legal_ai_exception_handler(request: Request, exc: LegalAIException):
    return JSONResponse(
        status_code=500,
        content={"error": type(exc).__name__, "detail": str(exc)},
    )


app.include_router(router)


@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "Legal AI Assistant"}
