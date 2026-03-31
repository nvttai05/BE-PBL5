from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.quiz_service import quiz_service
from app.schemas.quiz import QuizRequest, QuizResponse

router = APIRouter(prefix="/api/v1", tags=["Quiz"])


@router.post("/quiz", response_model=QuizResponse)
async def generate_quiz(request: QuizRequest, db: Session = Depends(get_db), user_id: int = 1):
    """Tạo quiz học từ vựng"""
    questions = quiz_service.generate_quiz(
        db=db,
        user_id=user_id,
        limit=request.limit,
        objects=request.objects
    )

    return QuizResponse(
        success=True,
        questions=questions
    )