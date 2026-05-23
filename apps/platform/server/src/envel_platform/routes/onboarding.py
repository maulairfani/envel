from fastapi import APIRouter, Depends

from envel_platform.auth import require_user
from envel_platform.db import (
    get_onboarding_status,
    get_setup_progress,
    mark_onboarding_complete,
    maybe_sync_onboarding_completion,
)

router = APIRouter()


@router.get("/status")
async def onboarding_status(username: str = Depends(require_user)):
    maybe_sync_onboarding_completion(username)
    return get_onboarding_status(username)


@router.get("/readiness")
async def onboarding_readiness(username: str = Depends(require_user)):
    maybe_sync_onboarding_completion(username)
    status = get_onboarding_status(username)
    return {
        "ready": status["is_complete"],
        **get_setup_progress(username),
    }


@router.post("/complete")
async def onboarding_complete(username: str = Depends(require_user)):
    mark = mark_onboarding_complete(username)
    status = get_onboarding_status(username)
    return {
        "ok": True,
        **mark,
        "status": status,
        **get_setup_progress(username),
    }
