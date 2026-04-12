from sqlalchemy import Column, Integer, String, Text
from app.models.base import Base

class ObjectDictionary(Base):
    __tablename__ = 'object_dictionary'
    object_id = Column(Integer, primary_key=True)
    class_name_en = Column(String, nullable = False, unique = True)
    class_name_vn = Column(String, nullable = False)
    example_sentence_en = Column(Text)
    pronunciation_ipa = Column(String)
    audio_file_path = Column(String, nullable = True)