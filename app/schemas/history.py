from pydantic import BaseModel
from typing import Optional,List
from datetime import datetime

class HistoryItem(BaseModel):
    history_id: int
    object_name_en:str
    object_name_vn:str
    confidence : float
    timestamp: datetime
    repeat_count: int

class HistoryResponse(BaseModel):
    success: bool=True
    history: List[HistoryItem]
    total_count: int
