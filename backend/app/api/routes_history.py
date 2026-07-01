from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.api.routes_jobs import serialize_job
from app.db.session import get_db
from app.models.job import GenerationJob
from app.schemas.job_schema import DeleteResponse, HistoryResponse
from app.services.encryption_service import decrypt_text
from app.utils.file_utils import remove_file_if_exists


router = APIRouter(prefix="/api/history", tags=["history"])


@router.get("", response_model=HistoryResponse)
def list_history(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=50),
    keyword: str | None = Query(default=None),
    db: Session = Depends(get_db),
) -> HistoryResponse:
    query = (
        select(GenerationJob)
        .options(selectinload(GenerationJob.outputs))
        .order_by(GenerationJob.created_at.desc())
    )
    jobs = db.execute(query).scalars().all()

    if keyword and keyword.strip():
        normalized_keyword = keyword.strip().lower()
        jobs = [
            job
            for job in jobs
            if normalized_keyword in (decrypt_text(job.source_text) or "").lower()
            or normalized_keyword in (decrypt_text(job.translated_text) or "").lower()
        ]

    total = len(jobs)
    paged_jobs = jobs[(page - 1) * page_size : page * page_size]

    return HistoryResponse(
        items=[serialize_job(job) for job in paged_jobs],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.delete("/{job_id}", response_model=DeleteResponse)
def delete_history(job_id: str, db: Session = Depends(get_db)) -> DeleteResponse:
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

    for output in job.outputs:
        remove_file_if_exists(output.audio_path)

    db.delete(job)
    db.commit()
    return DeleteResponse(success=True)
