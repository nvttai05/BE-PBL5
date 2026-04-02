from sqlalchemy.orm import Session
from typing import List, Dict, Any
import random
from app.models import LearningHistory, ObjectDictionary
from app.schemas.quiz import QuizQuestion


class QuizService:
    def generate_quiz(
            self,
            db: Session,
            user_id: int,
            limit: int = 5,
            objects: List[str] = None
    ) -> List[QuizQuestion]:
        """
        Tạo quiz dựa trên lịch sử học của user
        """
        # Lấy các object đã học gần đây
        if objects:
            # Quiz theo danh sách object chỉ định
            object_list = objects
        else:
            # Lấy từ lịch sử
            recent_objects = db.query(LearningHistory.object_name_en) \
                .filter(LearningHistory.user_id == user_id) \
                .distinct().limit(20).all()
            object_list = [obj[0] for obj in recent_objects]

        if not object_list:
            # Fallback: dùng một số object phổ biến
            object_list = ["chair", "book", "bottle", "cup", "laptop", "table"]

        questions = []
        selected_objects = random.sample(object_list, min(limit, len(object_list)))

        for obj_en in selected_objects:
            # Tìm tên tiếng Việt
            obj_db = db.query(ObjectDictionary).filter(
                ObjectDictionary.class_name_en == obj_en
            ).first()

            name_vn = obj_db.class_name_vn if obj_db else obj_en

            # Tạo câu hỏi multiple choice
            question_text = f"What is this? (Đây là gì?) - {name_vn}"

            # Tạo 3 đáp án sai ngẫu nhiên
            wrong_options = random.sample([o for o in object_list if o != obj_en], 3)
            options = wrong_options + [obj_en]
            random.shuffle(options)

            questions.append(QuizQuestion(
                question=question_text,
                options=[o.capitalize() for o in options],
                correct_answer=obj_en.capitalize()
            ))

        return questions


# Khởi tạo singleton
quiz_service = QuizService()