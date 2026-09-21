from fastapi import APIRouter

health_router = APIRouter()

@health_router.get("/health", tags=["health"])
def health():
    return {"status": "ok"}
