from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from app.models.base import Base

class QuizResult(Base):
    __tablename__ = "quiz_results"

    quiz_id = Column(Integer, primary_key=True)
    history_id = Column(Integer, ForeignKey("learning_history.history_id"))
    user_id = Column(Integer, ForeignKey("users.user_id"),nullable=False)
    score = Column(Integer, nullable=False)
    total_questions = Column(Integer, nullable=False)
    questions_json = Column(Text)  # Luu dang Json string
    timestamp = Column(DateTime, default=datetime.utcnow)