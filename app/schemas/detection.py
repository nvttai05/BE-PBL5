from typing import List, Optional
from pydantic import BaseModel

class DetectionItem(BaseModel):
        class_name : str
        name_vn : str
        confidence : float
        bbox: List[int]  #[x1,y1,x2,y2]

class DetectionResponse(BaseModel):
        success : bool=True
        detections: List[DetectionItem] = [] #luu y khong nen dung list rong
        proccessing_time_ms: Optional[float] =None
        error: Optional[str]= None


