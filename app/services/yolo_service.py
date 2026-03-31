import time
from ultralytics import YOLO
from PIL import Image
import io
from typing import List, Dict, Any
from app.core.config import settings

class YOLOService:
    def __init__(self):
        self.model = None
        self.confidence_threshold = settings.CONFIDENCE_THRESHOLD
        self.imgsz = settings.IMGSZ
        self._load_model()

    def _load_model(self):
        try:
            print("Loading YOLO model...")
            self.model = YOLO(settings.YOLO_MODEL_PATH)
            #warm up
            self.model.predict(source="0.jpg" if False else None, verbose=False)
            print(f"YOLO model loaded successfully! (Confidence threshold: {self.confidence_threshold})")
        except Exception as e:
            print(f"YOLO model NOTTTTT loaded successfully! (Error: {e})")
            self.model = None
            raise

    def detect_object(self, image_bytes:bytes) -> Dict[str, Any]:
        if not self.model:
            raise Exception("YOLO model not loaded!")

        start_time = time.time()

        try:
            #Chuyen byte thanh anh
            image = Image.open(io.BytesIO(image_bytes)).convert("RGB")

            results = self.model.predict(
                source=image,
                imgsz=self.imgsz,
                conf=self.confidence_threshold,
                verbose=False
            )
            detections=[]
            result=results[0]

            for box in result.boxes:
                class_id= int(box.cls[0])
                confidence= float(box.conf[0])
                bbox = box.xyxy[0].tolist()

                class_name_en = result.names[class_id]
                #TODO: map sang ten VN tu DB
                name_vn=self._get_vietnamese_name(class_name_en)

                detections.append({
                    "class_name": class_name_en,
                    "name_vn": name_vn,
                    "confidence": round(confidence,3),
                    "bbox": [int(x) for x in bbox],
                })
            proccessing_time = (time.time() - start_time) * 1000

            return {
                "detections": detections,
                "proccessing_time_ms": round(proccessing_time,2),
                "total_object": len(detections)
            }
        except Exception as e:
            raise Exception(f"YOLO detection failed! (Error: {e})")
    def _get_vietnamese_name(self, class_name_en: str) -> str:
        vn_map = {
            "chair": "ghế",
            "book": "sách",
            "bottle": "chai",
            "cup": "cốc",
            "laptop": "laptop",
            "cell phone": "điện thoại",
            "person": "người",
            "table": "bàn",
            "tv": "ti vi",
            # Them nhieu hon sau nay tu database
        } 
        return vn_map.get(class_name_en.lower(), class_name_en)

# Khởi tạo singleton
yolo_service = YOLOService()