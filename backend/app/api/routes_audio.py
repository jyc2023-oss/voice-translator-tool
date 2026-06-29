from fastapi import APIRouter, HTTPException

from app.core.errors import AppError
from app.schemas.job_schema import VoiceCatalogResponse
from app.services.elevenlabs_service import list_voices


router = APIRouter(prefix="/api/audio", tags=["audio"])


@router.get("/health")
def audio_health() -> dict:
    return {"ok": True}


@router.get("/voices", response_model=VoiceCatalogResponse)
async def audio_voices() -> VoiceCatalogResponse:
    try:
        items = await list_voices()
    except AppError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc
    return VoiceCatalogResponse(items=items)
