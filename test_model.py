from ultralytics import YOLO
import cv2

# Load model
model = YOLO("yolo11n.pt")

# Đường dẫn ảnh
image_path = "debug_frames/frame_70.jpg"  # đổi thành ảnh của bạn

# Nhận diện
results = model(image_path)

# Lấy ảnh đã vẽ bounding box
annotated_image = results[0].plot()

# Hiển thị ảnh
cv2.imshow("Result", annotated_image)
cv2.waitKey(0)
cv2.destroyAllWindows()

# In ra các object detect được
for box in results[0].boxes:
    cls_id = int(box.cls[0])
    conf = float(box.conf[0])
    name = model.names[cls_id]
    print(f"{name}: {conf:.2f}")
