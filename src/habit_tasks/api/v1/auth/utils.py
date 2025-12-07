import uuid
from datetime import datetime, timedelta, timezone
from enum import Enum

import bcrypt
import jwt

from habit_tasks.config import settings
from habit_tasks.database.models import User
from habit_tasks.schemas.token import TokenInfo


class TokenType(str, Enum):
    ACCESS = "access"
    REFRESH = "refresh"


def hash_password(password: str) -> str:
    pwd_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(pwd_bytes, salt)
    return hashed_password.decode("utf-8")


def validate_password(password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(
        password.encode("utf-8"),
        hashed_password.encode("utf-8"),
    )


def encode_token(
    payload: dict,
    private_key: str = settings.auth.secret_key_path,
    algorithm: str = settings.auth.algorithm,
) -> str:
    to_encode = payload.copy()
    now = datetime.now(timezone.utc)

    if "exp" not in to_encode:
        expire = now + timedelta(minutes=15)
        to_encode.update(exp=expire)

    to_encode.update(iat=now, jti=str(uuid.uuid4()))

    return jwt.encode(to_encode, private_key, algorithm=algorithm)


def decode_token(
    token: str | bytes,
    public_key: str = settings.auth.public_key_path,
    algorithm: str = settings.auth.algorithm,
) -> dict:
    return jwt.decode(token, public_key, algorithms=[algorithm])


def generate_token_info(user: User) -> TokenInfo:
    now = datetime.now(timezone.utc)

    # Access Token
    access_payload = {
        "sub": user.username,
        "email": user.email,
        "type": TokenType.ACCESS,
        "exp": now + timedelta(minutes=settings.auth.access_token_expire_minutes),
    }
    access_token = encode_token(access_payload)

    # Refresh Token
    refresh_payload = {
        "sub": user.username,
        "type": TokenType.REFRESH,
        "exp": now + timedelta(days=settings.auth.refresh_token_expire_days),
    }
    refresh_token = encode_token(refresh_payload)

    return TokenInfo(
        access_token=access_token,
        refresh_token=refresh_token,
    )
