from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.tts_service import tts_service
from app.schemas.speak import SpeakRequest, SpeakResponse

router = APIRouter(prefix="/api/v1", tags=["Speech"])


@router.post("/speak", response_model=SpeakResponse)
async def speak_text(request: SpeakRequest):
    """Chuyển text thành giọng nói và trả về đường dẫn audio"""
    try:
        result = tts_service.generate_audio(
            text=request.text,
            accent=request.accent
        )

        return SpeakResponse(
            success=True,
            audio_url=result["audio_url"],
            duration_seconds=result["duration_seconds"]
        )

    except Exception as e:
        return SpeakResponse(
            success=False,
            audio_url="",
            error=str(e)
        )