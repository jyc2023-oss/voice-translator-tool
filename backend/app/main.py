from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.routes_audio import router as audio_router
from app.api.routes_history import router as history_router
from app.api.routes_jobs import router as jobs_router
from app.core.config import settings
from app.db.base import Base
from app.db.session import engine
from app.services.storage_service import ensure_audio_dir


def create_app() -> FastAPI:
    Base.metadata.create_all(bind=engine)
    ensure_audio_dir()

    app = FastAPI(title=settings.app_name)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[settings.frontend_url, "http://127.0.0.1:5173"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(jobs_router)
    app.include_router(history_router)
    app.include_router(audio_router)
    app.mount("/audio", StaticFiles(directory=settings.audio_dir), name="audio")

    @app.get("/api/health")
    def healthcheck() -> dict:
        return {"status": "ok"}

    return app


app = create_app()

