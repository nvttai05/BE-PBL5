from pydantic import BaseModel
from typing import Optional

class SpeakRequest(BaseModel):
    text : str
    accent: str="en-uk"  #en-uk or en-us
    speed: float =1.0
    volume: float =0.9

class SpeakResponse(BaseModel):
    success: bool = True
    audio_url: str #Optional[]
    duration_seconds: Optional[float]= None
    error: Optional[str]= None