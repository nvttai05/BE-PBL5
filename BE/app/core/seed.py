from sqlalchemy.orm import Session
from app.models.object_dictionary import ObjectDictionary


def seed_object_dictionary(db: Session):
    # Danh sách một số class phổ biến (bạn có thể mở rộng sau)
    common_objects = [
        ("person", "người"),
        ("chair", "ghế"),
        ("table", "bàn"),
        ("book", "sách"),
        ("bottle", "chai"),
        ("cup", "cốc"),
        ("laptop", "laptop"),
        ("cell phone", "điện thoại"),
        ("tv", "ti vi"),
        ("keyboard", "bàn phím"),
    ]

    for en, vn in common_objects:
        existing = db.query(ObjectDictionary).filter(ObjectDictionary.class_name_en == en).first()
        if not existing:
            obj = ObjectDictionary(
                class_name_en=en,
                class_name_vn=vn,
                example_sentence_en=f"This is a {en}."
            )
            db.add(obj)

    db.commit()
    print("✅ Seeded common objects into object_dictionary")