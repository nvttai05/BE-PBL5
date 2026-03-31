from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.yolo_service import yolo_service
from app.services.history_service import history_service
from app.schemas.detection import DetectionResponse
import time

router = APIRouter(prefix="/api/v1",tags=["Detection"])

@router.post("/detect", response_model=DetectionResponse)
async def detect(file: UploadFile = File(...),
                 db: Session = Depends(get_db),
                 user_id: int =1 #tam thoi
                 ):
    try:
        image_bytes= await file.read()

        if len(image_bytes) ==0:
            raise HTTPException(status_code=400, detail="Empty image")

        result = yolo_service.detect(image_bytes)

        detections = result["detections"]
        processing_time = result["processing_time_ms"]

        if detections:
            for det in detections[:1]: #tam thoi lay 1 vat dau
                history_service.create_history(
                    db=db,
                    user_id=user_id,
                    object_name_en=det["class_name"],
                    object_name_vn=det["name_vn"],
                    confidence=det["confidence"],
                    duration_seconds=processing_time/1000
                )
        return DetectionResponse(
            success=True,
            detections=detections,
            proccessing_time_ms=processing_time
        )
    except Exception as e:
        return DetectionResponse(
            success=False,
            detections=[],
            error=str(e)
        )