from fastapi import APIRouter

from . import auth, users

router = APIRouter(prefix="/v1")

for router in (auth.router, users.router):
    router.include_router(router=router)
