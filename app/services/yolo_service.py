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
            dummy= Image.new("RGB", (640,640))
            self.model.predict(source=dummy, verbose=False)
            print(f"YOLO model loaded successfully! (Confidence threshold: {self.confidence_threshold})")
        except Exception as e:
            print(f"YOLO model NOTTTTT loaded successfully! (Error: {e})")
            self.model = None
            raise

    def detect_objects(self, image_bytes:bytes) -> Dict[str, Any]:
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
            processing_time = (time.time() - start_time) * 1000

            return {
                "detections": detections,
                "processing_time_ms": round(processing_time,2),
                "total_object": len(detections)
            }
        except Exception as e:
            raise Exception(f"YOLO detection failed! (Error: {e})")
    def _get_vietnamese_name(self, class_name_en: str) -> str:
        vn_map = {
            "person": "người",
            "bicycle": "xe đạp",
            "car": "xe hơi",
            "motorcycle": "xe máy",
            "bus": "xe buýt",
            "truck": "xe tải",
            "boat": "thuyền",
            "bench": "ghế dài",
            "bird": "chim",
            "cat": "mèo",
            "dog": "chó",
            "horse": "ngựa",
            "sheep": "cừu",
            "cow": "bò",
            "elephant": "voi",
            "bear": "gấu",
            "zebra": "ngựa vằn",
            "giraffe": "hươu cao cổ",
            "backpack": "ba lô",
            "umbrella": "ô",
            "handbag": "túi xách",
            "tie": "cà vạt",
            "suitcase": "vali",
            "bottle": "chai",
            "wine glass": "ly rượu",
            "cup": "cốc",
            "fork": "nĩa",
            "knife": "dao",
            "spoon": "muỗng",
            "bowl": "bát",
            "banana": "chuối",
            "apple": "táo",
            "sandwich": "bánh mì kẹp",
            "orange": "cam",
            "broccoli": "bông cải xanh",
            "carrot": "cà rốt",
            "hot dog": "xúc xích",
            "pizza": "pizza",
            "donut": "bánh donut",
            "cake": "bánh kem",
            "chair": "ghế",
            "couch": "ghế sofa",
            "potted plant": "cây cảnh",
            "bed": "giường",
            "dining table": "bàn ăn",
            "toilet": "bồn cầu",
            "tv": "ti vi",
            "laptop": "laptop",
            "mouse": "chuột máy tính",
            "remote": "remote",
            "keyboard": "bàn phím",
            "cell phone": "điện thoại",
            "microwave": "lò vi sóng",
            "oven": "lò nướng",
            "toaster": "máy nướng bánh mì",
            "sink": "bồn rửa",
            "refrigerator": "tủ lạnh",
            "book": "sách",
            "clock": "đồng hồ",
            "vase": "bình hoa",
            "scissors": "kéo",
            "teddy bear": "gấu bông",
            "hair drier": "máy sấy tóc",
            "toothbrush": "bàn chải đánh răng",
        }

        return vn_map.get(class_name_en.lower(), class_name_en)

# Khởi tạo singleton
yolo_service = YOLOService()