from typing import Annotated

from fastapi import APIRouter, Depends

from api.v1.users.dependencies import add_user
from database.models import User
from schemas.jwt import TokenInfo

from .dependencies import validate_user
from .utils import generate_token_info

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=TokenInfo)
async def login(
    user: Annotated[User, Depends(validate_user)],
):
    return generate_token_info(user)


@router.post("/register", response_model=TokenInfo)
async def register(user: Annotated[User, Depends(add_user)]):
    return generate_token_info(user)
