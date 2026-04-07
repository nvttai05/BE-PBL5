from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

SQLALCHEMY_DATABASE_URL = f"sqlite:///./{settings.DB_PATH}"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Hàm tạo tất cả bảng (sẽ gọi khi startup)
def create_tables():
    from app.models import Base  # Import tất cả models ở đây
    from app.models.user import User
    from app.models.object_dictionary import ObjectDictionary
    from app.models.learning_history import LearningHistory
    from app.models.quiz_result import QuizResult

    Base.metadata.create_all(bind=engine)
    print("✅ All database tables created successfully!")