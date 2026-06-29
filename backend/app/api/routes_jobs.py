from __future__ import annotations

import asyncio

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.db.session import SessionLocal, get_db
from app.models.job import GenerationJob, VoiceOutput
from app.schemas.job_schema import CreateJobRequest, JobResponse, VoiceSelection, VoiceOutputResponse
from app.services.elevenlabs_service import synthesize_speech
from app.services.sentence_align_service import estimate_alignment
from app.services.storage_service import build_audio_path, build_audio_url
from app.services.translation_service import translate_text
from app.utils.file_utils import remove_file_if_exists
from app.utils.text_utils import validate_source_text
from app.core.config import settings
from app.core.errors import AppError


router = APIRouter(prefix="/api/jobs", tags=["jobs"])


def normalize_voices(payload: CreateJobRequest) -> list[VoiceSelection]:
    voices = payload.voices or []
    if payload.voice_ids:
        voices.extend(
            VoiceSelection(voice_id=voice_id, voice_name=f"Voice {index + 1}")
            for index, voice_id in enumerate(payload.voice_ids)
        )

    deduped: list[VoiceSelection] = []
    seen: set[str] = set()
    for voice in voices:
        voice_id = voice.voice_id.strip()
        if not voice_id or voice_id in seen:
            continue
        seen.add(voice_id)
        deduped.append(VoiceSelection(voice_id=voice_id, voice_name=voice.voice_name or voice_id))

    if not deduped and settings.elevenlabs_default_voice_id:
        deduped.append(
            VoiceSelection(
                voice_id=settings.elevenlabs_default_voice_id,
                voice_name="Default Voice",
            )
        )

    if not deduped:
        raise AppError("请至少提供一个音色 ID，或在 `.env` 中配置默认音色。")
    if len(deduped) > settings.max_voice_count:
        raise AppError(f"单次最多支持 {settings.max_voice_count} 个音色。")
    return deduped


def serialize_output(output: VoiceOutput) -> VoiceOutputResponse:
    return VoiceOutputResponse(
        output_id=output.id,
        voice_id=output.voice_id,
        voice_name=output.voice_name,
        status=output.status,
        audio_url=output.audio_url,
        duration_seconds=output.duration_seconds,
        alignment=output.alignment_json or [],
        error_message=output.error_message,
    )


def serialize_job(job: GenerationJob) -> JobResponse:
    return JobResponse(
        job_id=job.id,
        status=job.status,
        source_text=job.source_text,
        translated_text=job.translated_text,
        error_message=job.error_message,
        created_at=job.created_at,
        updated_at=job.updated_at,
        outputs=[serialize_output(output) for output in job.outputs],
    )


async def process_single_voice(job_id: str, translated_text: str, voice_id: str, voice_name: str) -> dict:
    target_path = build_audio_path(job_id, voice_name)
    try:
        duration = await synthesize_speech(translated_text, voice_id, target_path)
        return {
            "voice_id": voice_id,
            "status": "completed",
            "voice_name": voice_name,
            "audio_path": str(target_path),
            "audio_url": build_audio_url(target_path),
            "duration_seconds": duration,
            "alignment_json": estimate_alignment(translated_text, duration),
            "error_message": None,
        }
    except Exception as exc:
        remove_file_if_exists(str(target_path))
        return {
            "voice_id": voice_id,
            "status": "failed",
            "voice_name": voice_name,
            "audio_path": None,
            "audio_url": None,
            "duration_seconds": None,
            "alignment_json": [],
            "error_message": str(exc),
        }


async def process_single_voice_with_limit(
    semaphore: asyncio.Semaphore,
    job_id: str,
    translated_text: str,
    voice_id: str,
    voice_name: str,
) -> dict:
    async with semaphore:
        return await process_single_voice(job_id, translated_text, voice_id, voice_name)


async def run_job_pipeline(job_id: str) -> None:
    db = SessionLocal()
    try:
        job = (
            db.execute(
                select(GenerationJob)
                .options(selectinload(GenerationJob.outputs))
                .where(GenerationJob.id == job_id)
            )
            .scalars()
            .first()
        )
        if not job:
            return

        job.status = "translating"
        db.commit()

        translated_text = await translate_text(job.source_text)
        job.translated_text = translated_text
        job.status = "synthesizing"
        for output in job.outputs:
            output.status = "synthesizing"
            output.error_message = None
        db.commit()

        semaphore = asyncio.Semaphore(max(settings.elevenlabs_max_concurrency, 1))
        tasks = [
            process_single_voice_with_limit(
                semaphore,
                job.id,
                translated_text,
                output.voice_id,
                output.voice_name,
            )
            for output in job.outputs
        ]
        results = await asyncio.gather(*tasks)

        success_count = 0
        for output in job.outputs:
            result = next(item for item in results if item["voice_id"] == output.voice_id)
            output.status = result["status"]
            output.audio_path = result["audio_path"]
            output.audio_url = result["audio_url"]
            output.duration_seconds = result["duration_seconds"]
            output.alignment_json = result["alignment_json"]
            output.error_message = result["error_message"]
            if output.status == "completed":
                success_count += 1

        if success_count:
            job.status = "completed"
            job.error_message = None if success_count == len(job.outputs) else "部分音色生成失败。"
        else:
            job.status = "failed"
            job.error_message = "所有音色都生成失败，请检查配置后重试。"
        db.commit()
    except Exception as exc:
        db.rollback()
        failed_job = (
            db.execute(
                select(GenerationJob)
                .options(selectinload(GenerationJob.outputs))
                .where(GenerationJob.id == job_id)
            )
            .scalars()
            .first()
        )
        if failed_job:
            failed_job.status = "failed"
            failed_job.error_message = str(exc)
            for output in failed_job.outputs:
                if output.status != "completed":
                    output.status = "failed"
                    output.error_message = str(exc)
            db.commit()
    finally:
        db.close()


@router.post("", response_model=JobResponse, status_code=202)
async def create_job(
    payload: CreateJobRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
) -> JobResponse:
    try:
        source_text = validate_source_text(payload.source_text, settings.max_source_chars)
        voices = normalize_voices(payload)
    except AppError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    job = GenerationJob(source_text=source_text, status="pending")
    job.outputs = [
        VoiceOutput(voice_id=voice.voice_id, voice_name=voice.voice_name or voice.voice_id, status="pending")
        for voice in voices
    ]
    db.add(job)
    db.commit()
    db.refresh(job)

    background_tasks.add_task(run_job_pipeline, job.id)

    db.refresh(job)
    return serialize_job(job)


@router.get("/{job_id}", response_model=JobResponse)
def get_job(job_id: str, db: Session = Depends(get_db)) -> JobResponse:
    job = (
        db.execute(
            select(GenerationJob)
            .options(selectinload(GenerationJob.outputs))
            .where(GenerationJob.id == job_id)
        )
        .scalars()
        .first()
    )
    if not job:
        raise HTTPException(status_code=404, detail="任务不存在。")
    return serialize_job(job)
