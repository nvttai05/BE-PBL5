from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from app.models.base import Base

class LearningHistory(Base):
    __tablename__ = 'learning_history'

    history_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("user.user_id"), nullable=False)
    objective_id = Column(Integer, ForeignKey("objective_dictionary.objective_id"))
    objective_name_en = Column(String, nullable=False)
    objective_name_vn = Column(String)
    confidence = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)
    repeat_count = Column(Integer, default=1)
    duration_seconds = Column(Float)

    #relationship
    user= relationship("User")
    objective_dict=relationship("ObjectiveDictionary")