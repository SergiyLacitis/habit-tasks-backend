from typing import Annotated

from fastapi import APIRouter, Depends

from habit_tasks.api.v1.auth.dependencies import get_auth_user_from_access_token
from habit_tasks.database import AsyncDBSessionDep
from habit_tasks.database.models import User
from habit_tasks.schemas.sync import SyncPayload, SyncResponse

from .dependencies import sync_data_logic

router = APIRouter(prefix="/sync", tags=["Synchronization"])

CurrentUser = Annotated[User, Depends(get_auth_user_from_access_token)]


@router.post("/", response_model=SyncResponse)
async def sync_data(
    payload: SyncPayload,
    session: AsyncDBSessionDep,
    user: CurrentUser,
):
    return await sync_data_logic(session, user, payload)
