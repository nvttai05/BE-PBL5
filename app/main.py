from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.database import create_tables   # Chỉ import hàm này
from app.services.yolo_service import yolo_service

# Lifespan event
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 Starting English Object Recognition API...")
    print(f"📍 Server running on http://{settings.HOST}:{settings.PORT}")

    # Tạo database tables
    try:
        create_tables()
    except Exception as e:
        print(f"⚠️ Warning: Could not create tables: {e}")

    # Load YOLO model
    try:
        if yolo_service.model is None:
            print("🔄 Loading YOLOv11n model... (this may take 5-15 seconds)")
        else:
            print("✅ YOLOv11n model already loaded")
    except Exception as e:
        print(f"⚠️ Could not load YOLO model: {e}")

    yield
    print("🛑 Shutting down API...")


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Backend API cho hệ thống học tiếng Anh qua nhận diện đồ vật",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static folder để phục vụ file audio (.wav)
os.makedirs("app/static/audio", exist_ok=True)
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Import routers sau khi app được tạo
from app.routers import status, detect, speak, history, quiz

app.include_router(status.router)
app.include_router(detect.router)
app.include_router(speak.router)
app.include_router(history.router)
app.include_router(quiz.router)


@app.get("/")
async def root():
    return {
        "message": "English Object Recognition Learning System API is running",
        "docs": "/docs",
        "status": "/api/v1/status"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )