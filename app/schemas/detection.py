from pydantic import BaseModel
from typing import List, Optional

class DetectionItem(BaseModel):
    class_name: str
    name_vn: str
    confidence: float
    bbox: List[int]

class DetectionResponse(BaseModel):
    success: bool = True
    detections: List[DetectionItem] = []
    processing_time_ms: Optional[float] = None
    audio_url: Optional[str] = None      # ← THÊM DÒNG NÀY
    error: Optional[str] = None