from fastapi.middleware.cors import CORSMiddleware
from core.config import settings


def add_cors_middleware(app):
    """
    Registers CORSMiddleware on the FastAPI app.
    Allowed origins are pulled from settings.
    """
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
