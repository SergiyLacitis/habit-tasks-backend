from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

import utils
from config import settings
from database import database_helper
from database.models import User
from schemas.jwt import TokenInfo

from .dependencies import validate_user

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=TokenInfo)
async def login(
    user: Annotated[User, Depends(validate_user)],
):
    payload = {"sub": user.username}

    token = utils.auth.encode_token(
        payload=payload,
        private_key=settings.auth.secret_key_path,
        algorithm=settings.auth.algorithm,
        expire_minutes=settings.auth.access_token_expire_minutes,
    )
    return TokenInfo(access_token=token, token_type="Bearer")


@router.post("/register")
async def register(
    session: Annotated[AsyncSession, Depends(database_helper.session_getter)],
): ...
