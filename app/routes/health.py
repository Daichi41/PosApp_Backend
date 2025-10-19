from fastapi import APIRouter

router = APIRouter(tags=["system"])


@router.get("/healthz", summary="Health check")
def healthz() -> dict[str, str]:
    """Return service health."""

    return {"status": "ok"}
