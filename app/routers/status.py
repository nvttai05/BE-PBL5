from fastapi import APIRouter
from fastapi.params import Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.common import StatusResponse
from app.services.yolo_service import yolo_service

router = APIRouter(prefix="/api/v1", tags=["Status"])

@router.get("/status", response_model=StatusResponse)
async def get_status(db: Session=Depends(get_db)):
    """kiem tra trang thai server"""
    return{
        "success": True,
        "status": "ok",
        "model_loaded": yolo_service.model is not None,
        "latency_avg_ms": None # Tinh sau
    }