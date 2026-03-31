from sqlalchemy.orm import Session
from sqlalchemy import desc
from datetime import datetime
from typing import List, Optional
from app.models import User, LearningHistory, ObjectDictionary
from app.schemas.history import HistoryItem

class HistoryService:
    def create_history(
            self,
            db:Session,
            user_id:int,
            object_name_en:str,
            object_name_vn:str,
            confidence:float,
            duration_seconds: Optional[float] = None
                       ) -> LearningHistory:

        obj = db.query(ObjectDictionary).filter(ObjectDictionary.class_name_en == object_name_en).first()
        if not obj:
            obj = ObjectDictionary(
                object_id=len(db.query(ObjectDictionary).all())+1, #dung tam thoi thoi
                class_name_en=object_name_en,
                class_name_vn=object_name_vn,
                example_sentence_en=f"This is a {object_name_en}.",
            )
            db.add(obj)
            db.commit()
            db.refresh(obj)

        history = LearningHistory(
            user_id=user_id,
            objective_id=obj.object_id,
            objective_name_en=object_name_en,
            objective_name_vn=object_name_vn,
            confidence=confidence,
            duration_seconds=duration_seconds,
            repeat_count=1
        )
        db.add(history)
        db.commit()
        db.refresh(history)
        return history

    def get_history(
            self,
            db:Session,
            user_id:int,
            limit:int = 50,
            skip:int = 0
    ) -> List[HistoryItem]:
        histories = db.query(LearningHistory).filter(LearningHistory.user_id == user_id).order_by(desc(LearningHistory.timestamp)).offset(skip).limit(limit).all()
        return [
            HistoryItem(
            history_id=h.history_id,
            object_name_en=h.objective_name_en,
            object_name_vn=h.objective_name_vn,
            confidence=h.confidence or 0.0,
            timestamp=h.timestamp,
            repeat_count=h.repeat_count,
        ) # dung tam thoi
        for h in histories
        ]

    def increse_repeat_count(
            self,
            db:Session,
            history_id:int
    ) -> bool:
        history = db.query(LearningHistory).filter(LearningHistory.history_id == history_id).first()
        if history:
            history.repeat_count += 1
            db.commit()
            return True
        return False

    def get_total_count(
            self,
            db:Session,
            user_id:int
            ) -> int:
        return db.query(LearningHistory).filter(LearningHistory.user_id == user_id).count()

history_service = HistoryService()