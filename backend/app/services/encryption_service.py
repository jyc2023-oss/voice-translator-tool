from __future__ import annotations

from cryptography.fernet import Fernet, InvalidToken

from app.core.config import settings
from app.core.errors import ExternalServiceError


ENCRYPTION_PREFIX = "enc::"


def is_encryption_enabled() -> bool:
    return bool(settings.field_encryption_key)


def _get_fernet() -> Fernet:
    if not settings.field_encryption_key:
        raise ExternalServiceError("缺少 `FIELD_ENCRYPTION_KEY`，无法启用数据库字段加密。", status_code=500)
    try:
        return Fernet(settings.field_encryption_key.encode("utf-8"))
    except Exception as exc:
        raise ExternalServiceError("`FIELD_ENCRYPTION_KEY` 格式无效，请使用 Fernet 密钥。", status_code=500) from exc


def is_encrypted_value(value: str | None) -> bool:
    return bool(value and value.startswith(ENCRYPTION_PREFIX))


def encrypt_text(plaintext: str | None) -> str | None:
    if plaintext is None:
        return None
    if plaintext == "":
        return plaintext
    if not is_encryption_enabled():
        return plaintext
    if is_encrypted_value(plaintext):
        return plaintext
    token = _get_fernet().encrypt(plaintext.encode("utf-8")).decode("utf-8")
    return f"{ENCRYPTION_PREFIX}{token}"


def decrypt_text(ciphertext: str | None) -> str | None:
    if ciphertext is None:
        return None
    if ciphertext == "":
        return ciphertext
    if not is_encryption_enabled():
        return ciphertext
    if not is_encrypted_value(ciphertext):
        return ciphertext

    token = ciphertext[len(ENCRYPTION_PREFIX) :]
    try:
        return _get_fernet().decrypt(token.encode("utf-8")).decode("utf-8")
    except InvalidToken:
        return ciphertext
