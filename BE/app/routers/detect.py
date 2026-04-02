from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.yolo_service import yolo_service
from app.services.history_service import history_service
from app.schemas.detection import DetectionResponse
import time
from fastapi import Request
from app.services.tts_service import tts_service

router = APIRouter(prefix="/api/v1", tags=["Detection"])


@router.post("/detect", response_model=DetectionResponse)
async def detect_object(
    request: Request,
    file: UploadFile = File(None),
    db: Session = Depends(get_db),
    user_id: int = 1
):
    """Nhận ảnh từ ESP32-CAM và trả về cả detections + audio_url"""
    try:
        start_time = time.time()

        # Xử lý ảnh (hỗ trợ cả multipart và raw)
        if file and file.filename:
            image_bytes = await file.read()
        else:
            image_bytes = await request.body()

        if not image_bytes or len(image_bytes) == 0:
            raise HTTPException(status_code=400, detail="Empty image received")

        # === YOLO Detect ===
        result = yolo_service.detect_objects(image_bytes)
        detections = result.get("detections", [])
        processing_time = result.get("processing_time_ms", 0)

        # === TTS - Tạo audio nếu detect được vật ===
        audio_url = None
        if detections:
            # Lấy vật đầu tiên để đọc
            first_obj = detections[0]
            text_to_speak = f"This is a {first_obj['class_name']}"

            try:
                tts_result = tts_service.generate_audio(text=text_to_speak)
                audio_url = tts_result["audio_url"]
                print(f"🎤 Generated audio for: {first_obj['class_name']}")
            except Exception as tts_err:
                print(f"⚠️ TTS failed: {tts_err}")
                audio_url = None

            # Lưu lịch sử
            history_service.create_history(
                db=db,
                user_id=user_id,
                object_name_en=first_obj["class_name"],
                object_name_vn=first_obj.get("name_vn", first_obj["class_name"]),
                confidence=first_obj["confidence"],
                duration_seconds=processing_time / 1000
            )

        return DetectionResponse(
            success=True,
            detections=detections,
            processing_time_ms=processing_time,
            audio_url=audio_url  # ← THÊM DÒNG NÀY
        )

    except Exception as e:
        print(f"Detect error: {str(e)}")
        return DetectionResponse(
            success=False,
            detections=[],
            processing_time_ms=None,
            audio_url=None,
            error=str(e)
        )