import os
from datetime import datetime
import pyttsx3
from app.core.config import settings


class TTSService:
    def __init__(self):
        self.engine = None
        self.audio_dir = settings.AUDIO_DIR
        self._init_engine()
        self._ensure_audio_dir()

    def _init_engine(self):
        try:
            self.engine = pyttsx3.init()
            self.engine.setProperty('rate', settings.TTS_RATE)
            self.engine.setProperty('volume', settings.TTS_VOLUME)

            print("TS Service initialized successfully (WAV output)")

        except Exception as e:
            print(f"Failed to initialize TTS engine: {e}")
            self.engine = None

    def _ensure_audio_dir(self):
        os.makedirs(self.audio_dir, exist_ok=True)

    def generate_audio(self, text: str, accent: str = "en-uk") -> dict:

        if not self.engine:
            raise Exception("TTS engine is not initialized")

        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"speech_{timestamp}.wav"  # ← Đổi thành .wav
            filepath = os.path.join(self.audio_dir, filename)

            self.engine.save_to_file(text, filepath)
            self.engine.runAndWait()

            if not os.path.exists(filepath) or os.path.getsize(filepath) == 0:
                raise Exception("Generated WAV file is missing or empty")

            audio_url = f"/static/audio/{filename}"

            estimated_duration = max(0.8, len(text) * 0.085)

            print(f"Generated audio: {filename} | Duration {estimated_duration:.2f}s")

            return {
                "audio_url": audio_url,
                "duration_seconds": round(estimated_duration, 2),
                "filename": filename,
                "full_path": filepath
            }

        except Exception as e:
            raise Exception(f"TTS generation failed: {str(e)}")

    def speak(self, text: str, accent: str = "en-uk"):
        if self.engine:
            self.engine.say(text)
            self.engine.runAndWait()
        else:
            print("TTS engine is not available")

tts_service = TTSService()