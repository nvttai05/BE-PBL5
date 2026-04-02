from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import Base


class LearningHistory(Base):
    __tablename__ = "learning_history"

    history_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    object_id = Column(Integer, ForeignKey("object_dictionary.object_id"))

    object_name_en = Column(String, nullable=False)
    object_name_vn = Column(String)
    confidence = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)
    repeat_count = Column(Integer, default=1)
    duration_seconds = Column(Float)

    # Relationship - Sửa lỗi join condition
    user = relationship("User", foreign_keys=[user_id])
    object_dict = relationship("ObjectDictionary", foreign_keys=[object_id])

    def __repr__(self):
        return f"<LearningHistory {self.object_name_en} confidence={self.confidence}>"