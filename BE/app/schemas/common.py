from pydantic import BaseModel
from typing import Optional,Any

class ErrorResponse(BaseModel):
    success: bool = False
    error: str
    code: Optional[str] = None
    detail: Optional[Any] = None

class StatusResponse(BaseModel):
    success: bool = True
    status: str="ok"
    model_loaded:bool
    latency_avg_ms: Optional[float]= None

