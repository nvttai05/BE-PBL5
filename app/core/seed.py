from sqlalchemy.orm import Session
from app.models.object_dictionary import ObjectDictionary


def seed_object_dictionary(db: Session):
    # Danh sách một số class phổ biến (bạn có thể mở rộng sau)
    common_objects = [
        ("person", "người"),
        ("bicycle", "xe đạp"),
        ("car", "xe hơi"),
        ("motorcycle", "xe máy"),
        ("airplane", "máy bay"),
        ("bus", "xe buýt"),
        ("train", "tàu hỏa"),
        ("truck", "xe tải"),
        ("boat", "thuyền"),
        ("traffic light", "đèn giao thông"),
        ("fire hydrant", "vòi chữa cháy"),
        ("stop sign", "biển dừng"),
        ("bench", "ghế dài"),
        ("bird", "chim"),
        ("cat", "mèo"),
        ("dog", "chó"),
        ("horse", "ngựa"),
        ("sheep", "cừu"),
        ("cow", "bò"),
        ("elephant", "voi"),
        ("bear", "gấu"),
        ("zebra", "ngựa vằn"),
        ("giraffe", "hươu cao cổ"),
        ("backpack", "ba lô"),
        ("umbrella", "ô"),
        ("handbag", "túi xách"),
        ("tie", "cà vạt"),
        ("suitcase", "vali"),
        ("frisbee", "đĩa bay"),
        ("skis", "ván trượt tuyết"),
        ("snowboard", "ván trượt tuyết"),
        ("sports ball", "bóng thể thao"),
        ("kite", "diều"),
        ("baseball bat", "gậy bóng chày"),
        ("baseball glove", "găng tay bóng chày"),
        ("skateboard", "ván trượt"),
        ("surfboard", "ván lướt sóng"),
        ("tennis racket", "vợt tennis"),
        ("bottle", "chai"),
        ("wine glass", "ly rượu"),
        ("cup", "cốc"),
        ("fork", "nĩa"),
        ("knife", "dao"),
        ("spoon", "muỗng"),
        ("bowl", "bát"),
        ("banana", "chuối"),
        ("apple", "táo"),
        ("sandwich", "bánh mì kẹp"),
        ("orange", "cam"),
        ("broccoli", "bông cải"),
        ("carrot", "cà rốt"),
        ("hot dog", "xúc xích"),
        ("pizza", "pizza"),
        ("donut", "bánh donut"),
        ("cake", "bánh kem"),
        ("chair", "ghế"),
        ("couch", "ghế sofa"),
        ("potted plant", "cây cảnh"),
        ("bed", "giường"),
        ("dining table", "bàn ăn"),
        ("toilet", "bồn cầu"),
        ("tv", "ti vi"),
        ("laptop", "laptop"),
        ("mouse", "chuột máy tính"),
        ("remote", "remote"),
        ("keyboard", "bàn phím"),
        ("cell phone", "điện thoại"),
        ("microwave", "lò vi sóng"),
        ("oven", "lò nướng"),
        ("toaster", "máy nướng bánh"),
        ("sink", "bồn rửa"),
        ("refrigerator", "tủ lạnh"),
        ("book", "sách"),
        ("clock", "đồng hồ"),
        ("vase", "bình hoa"),
        ("scissors", "kéo"),
        ("teddy bear", "gấu bông"),
        ("hair drier", "máy sấy tóc"),
        ("toothbrush", "bàn chải đánh răng")
    ]
    count =0
    for en, vn in common_objects:
        existing = db.query(ObjectDictionary).filter(ObjectDictionary.class_name_en == en).first()
        if not existing:
            obj = ObjectDictionary(
                class_name_en=en,
                class_name_vn=vn,
                example_sentence_en=f"This is a {en}."
            )
            db.add(obj)
            count += 1

    db.commit()
    print(f"Seeded {count} common objects into object_dictionary")