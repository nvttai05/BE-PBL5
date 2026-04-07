import asyncio
import cv2
import httpx
import numpy as np
import time
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.services.yolo_service import yolo_service
from app.services.tts_service import tts_service
from app.services.history_service import history_service
from app.core.database import SessionLocal

router = APIRouter(prefix="/api/v1", tags=["Detection"])

# --- CẤU HÌNH IP (THAY ĐỔI THEO THỰC TẾ) ---
SPEAKER_URL = "http://192.168.2.106/play"
BASE_URL = "http://192.168.2.104:8000"

# --- BIẾN ĐIỀU TIẾT GIỌNG NÓI ---
last_spoken_object = ""
last_spoken_time = 0
COOLDOWN_SAME_OBJ = 3.0  # 10 giây mới nhắc lại cùng 1 vật
COOLDOWN_ANY_OBJ = 2.0  # 3 giây mới đọc vật tiếp theo (dù khác loại)

http_client = httpx.AsyncClient()


async def run_detection_pipeline(image_bytes, db):
    global last_spoken_object, last_spoken_time
    try:
        # 1. Nhận diện YOLO (Thread riêng)
        result = await asyncio.to_thread(yolo_service.detect_objects, image_bytes)
        detections = result.get("detections", [])

        if detections:
            first_obj = detections[0]
            label = first_obj['class_name']
            now = time.time()
            time_passed = now - last_spoken_time

            # --- LOGIC CHỐNG ĐỌC TRÙNG VÀ NHANH ---
            if label == last_spoken_object:
                if time_passed < COOLDOWN_SAME_OBJ: return
            else:
                if time_passed < COOLDOWN_ANY_OBJ: return

            # Cập nhật trạng thái đọc
            last_spoken_object = label
            last_spoken_time = now
            print(f"🎤 Đang phát âm thanh: {label}")

            # 2. Tạo TTS
            tts_res = await asyncio.to_thread(tts_service.generate_audio, text=f"This is a {label}")
            audio_path = tts_res.get("audio_url")

            if audio_path:
                full_url = BASE_URL + audio_path
                # 3. Gọi loa phát nhạc
                try:
                    await http_client.post(SPEAKER_URL, json={"audio_url": full_url}, timeout=1.0)
                except:
                    pass

            # 4. Lưu DB
            history_service.create_history(
                db=db, user_id=1,
                object_name_en=label,
                object_name_vn=first_obj.get("name_vn", label),
                confidence=first_obj["confidence"],
                duration_seconds=result.get("processing_time_ms", 0) / 1000
            )
    except Exception as e:
        print(f"🚨 Pipeline Error: {e}")


@router.websocket("/ws/detect")
async def websocket_detect(websocket: WebSocket):
    await websocket.accept()
    print("🟢 ESP32-CAM connected")
    db = SessionLocal()
    try:
        while True:
            image_bytes = await websocket.receive_bytes()

            # Hiển thị Debug Real-time
            nparr = np.frombuffer(image_bytes, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            if img is not None:
                cv2.imshow("Server Monitor", img)
                cv2.waitKey(1)

            # Chạy nhận diện ngầm
            asyncio.create_task(run_detection_pipeline(image_bytes, db))
    except WebSocketDisconnect:
        print("🔴 CAM disconnected")
    finally:
        db.close()
        cv2.destroyAllWindows()