from fastapi import APIRouter

from . import auth, tasks, users

router = APIRouter(prefix="/v1")

for subrouter in (auth.router, users.router, tasks.router):
    router.include_router(router=subrouter)
