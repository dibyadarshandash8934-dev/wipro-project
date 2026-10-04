from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
async def health_check() -> dict:
    """Health check endpoint to verify the backend is running."""
    return {"status": "ok"}
