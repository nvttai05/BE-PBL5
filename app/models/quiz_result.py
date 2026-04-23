from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.models.base import Base

class QuizResult(Base):
    __tablename__ = "quiz_results"

    quiz_id = Column(Integer, primary_key=True, autoincrement=True)
    history_id = Column(Integer, ForeignKey("learning_history.history_id", ondelete="SET NULL"), nullable=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    score = Column(Integer, nullable=False)
    total_questions = Column(Integer, nullable=False)
    questions_json = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)

    # Relationships
    history = relationship("LearningHistory", back_populates="quiz_results", foreign_keys=[history_id])