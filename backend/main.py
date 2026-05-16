from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import upload, chat, quiz
from core.config import settings
from core.logger import get_logger

logger = get_logger(__name__)

app = FastAPI(
    title="DocuChat AI",
    description="RAG-based PDF chatbot with AI-powered quiz generation",
    version="1.0.0"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Routers
app.include_router(upload.router, prefix="/api/upload", tags=["Upload"])
app.include_router(chat.router,   prefix="/api/chat",   tags=["Chat"])
app.include_router(quiz.router,   prefix="/api/quiz",   tags=["Quiz"])


@app.get("/")
async def root():
    return {"message": "DocuChat AI is running 🚀"}


@app.on_event("startup")
async def startup_event():
    logger.info("DocuChat AI started successfully.")