from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.database import Base, engine
from app.services.yolo_service import yolo_service  # Để load model lúc startup


# Lifespan event để load model khi startup
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 Starting English Object Recognition API...")
    print(f"📍 Server running at http://{settings.HOST}:{settings.PORT}")

    # Tạo database tables
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created/verified")

    # Load YOLO model
    try:
        if yolo_service.model is None:
            print("Loading YOLO model during startup...")
    except:
        pass

    yield

    # Shutdown
    print("🛑 Shutting down API...")


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Backend API cho hệ thống học tiếng Anh qua nhận diện đồ vật",
    version="1.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Cho phép tất cả (dev), sau này giới hạn
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files để phục vụ audio
os.makedirs("app/static/audio", exist_ok=True)
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Include routers
from app.routers import status, detect, speak, history, quiz

app.include_router(status.router)
app.include_router(detect.router)
app.include_router(speak.router)
app.include_router(history.router)
app.include_router(quiz.router)


# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "English Object Recognition Learning System API",
        "docs": "/docs",
        "status": "/api/v1/status"
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host=settings.HOST, port=settings.PORT)