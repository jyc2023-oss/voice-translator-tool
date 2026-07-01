from __future__ import annotations

from app.db.session import SessionLocal
from app.models.job import GenerationJob
from app.services.encryption_service import encrypt_text, is_encrypted_value, is_encryption_enabled


def main() -> None:
    if not is_encryption_enabled():
        raise RuntimeError("请先在 `backend/.env` 中配置 `FIELD_ENCRYPTION_KEY`，再执行迁移。")

    db = SessionLocal()
    try:
        jobs = db.query(GenerationJob).all()
        migrated_count = 0

        for job in jobs:
            changed = False

            if job.source_text and not is_encrypted_value(job.source_text):
                job.source_text = encrypt_text(job.source_text) or job.source_text
                changed = True
            if job.translated_text and not is_encrypted_value(job.translated_text):
                job.translated_text = encrypt_text(job.translated_text)
                changed = True
            if job.error_message and not is_encrypted_value(job.error_message):
                job.error_message = encrypt_text(job.error_message)
                changed = True

            for output in job.outputs:
                if output.error_message and not is_encrypted_value(output.error_message):
                    output.error_message = encrypt_text(output.error_message)
                    changed = True

            if changed:
                migrated_count += 1

        db.commit()
        print(f"已完成加密迁移，共处理 {migrated_count} 条任务记录。")
    finally:
        db.close()


if __name__ == "__main__":
    main()
