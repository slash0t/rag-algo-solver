from fastapi import APIRouter

router = APIRouter(tags=["ping"])


@router.get("/ping")
async def ping() -> str:
    return "pong"
