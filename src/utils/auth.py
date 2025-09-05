import uuid
from datetime import UTC, datetime, timedelta

import bcrypt
import jwt


def encode_token(
    payload: dict,
    private_key: str,
    algorithm: str,
    expire_minutes: int,
    expire_timedelta: timedelta | None = None,
):
    to_encode = payload.copy()
    now = datetime.now(UTC)

    expire = now + (
        expire_timedelta if expire_timedelta else timedelta(minutes=expire_minutes)
    )
    to_encode.update(exp=expire, iat=now, jti=str(uuid.uuid4()))

    return jwt.encode(to_encode, private_key, algorithm)


def decode_token(token: str | bytes, public_key: str, algorithm: str):
    return jwt.decode(token, public_key, algorithms=[algorithm])


def hash_password(password: str):
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())


def validate_password(password: str, hashed_password: bytes) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), hashed_password)
