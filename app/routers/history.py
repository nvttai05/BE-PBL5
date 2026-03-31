from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.history_service import history_service
from app.schemas.history import HistoryResponse

router = APIRouter(prefix="/api/v1", tags=["History"])


@router.get("/history", response_model=HistoryResponse)
async def get_learning_history(
        db: Session = Depends(get_db),
        user_id: int = 1,
        limit: int = Query(50, ge=1, le=100),
        skip: int = Query(0, ge=0)
):
    """Lấy lịch sử học tập"""
    history_list = history_service.get_history(db, user_id, limit, skip)
    total = history_service.get_total_count(db, user_id)

    return HistoryResponse(
        success=True,
        history=history_list,
        total_count=total
    )