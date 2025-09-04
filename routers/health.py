# === routers/health.py ===
from datetime import datetime
from fastapi import APIRouter

router = APIRouter(tags=["Health"])

@router.get("/")
async def root():
    return {"message": "AI Task Manager API", "status": "running"}

@router.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now()}