from pydantic import BaseModel
from typing import Optional

class ObjectDetailResponse(BaseModel):
    success: bool=True
    class_name_en: str
    class_name_vn: str
    example_sentence_en: Optional[str] = None
    pronunciation_en: Optional[str] = None
    audio_url: Optional[str] = None
    error: Optional[str] = None