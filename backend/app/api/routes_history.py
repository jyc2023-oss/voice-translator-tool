from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, selectinload

from app.db.session import get_db
from app.models.job import GenerationJob
from app.schemas.job_schema import DeleteResponse, HistoryResponse
from app.api.routes_jobs import serialize_job
from app.utils.file_utils import remove_file_if_exists


router = APIRouter(prefix="/api/history", tags=["history"])


@router.get("", response_model=HistoryResponse)
def list_history(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=50),
    keyword: str | None = Query(default=None),
    db: Session = Depends(get_db),
) -> HistoryResponse:
    filters = []
    if keyword:
        query_keyword = f"%{keyword.strip()}%"
        filters.append(
            or_(
                GenerationJob.source_text.ilike(query_keyword),
                GenerationJob.translated_text.ilike(query_keyword),
            )
        )

    total = db.scalar(select(func.count()).select_from(GenerationJob).where(*filters)) or 0
    jobs = (
        db.execute(
            select(GenerationJob)
            .options(selectinload(GenerationJob.outputs))
            .where(*filters)
            .order_by(GenerationJob.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        .scalars()
        .all()
    )

    return HistoryResponse(
        items=[serialize_job(job) for job in jobs],
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

