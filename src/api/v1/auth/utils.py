import uuid
from datetime import UTC, datetime, timedelta
from enum import Enum

import bcrypt
import jwt

from config import settings
from database.models import User
from schemas.jwt import TokenInfo


class TokenType(str, Enum):
    ACCESS = "access"
    REFRESH = "refresh"


def encode_token(
    payload: dict,
    expire_minutes: int,
    private_key: str = settings.auth.secret_key_path,
    algorithm: str = settings.auth.algorithm,
):
    to_encode = payload.copy()
    now = datetime.now(UTC)

    expire = now + timedelta(minutes=expire_minutes)

    to_encode.update(exp=expire, iat=now, jti=str(uuid.uuid4()))

    return jwt.encode(to_encode, private_key, algorithm)


def decode_token(token: str | bytes, public_key: str, algorithm: str):
    return jwt.decode(token, public_key, algorithms=[algorithm])


def hash_password(password: str):
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())


def validate_password(password: str, hashed_password: bytes) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), hashed_password)


def generate_token(
    user: User,
    expire_minutes: int,
    token_type: TokenType,
) -> str:
    payload = {"sub": user.username, "type": token_type}

    token = encode_token(
        expire_minutes=expire_minutes,
        payload=payload,
    )

    return token


def generate_token_info(user: User) -> TokenInfo:
    return TokenInfo(
        access_token=generate_token(
            user=user,
            expire_minutes=settings.auth.access_token_expire_minutes,
            token_type=TokenType.ACCESS,
        ),
        refresh_token=generate_token(
            user=user,
            expire_minutes=settings.auth.refresh_token_expire_days * 24 * 60,
            token_type=TokenType.REFRESH,
        ),
    )
