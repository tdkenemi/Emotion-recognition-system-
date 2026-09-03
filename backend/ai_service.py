import cv2
import numpy as np
from tensorflow.keras.models import load_model
from PIL import Image
import base64
import io
import logging

logger = logging.getLogger(__name__)

MODEL_FILENAME = 'emotion_model.h5'

EMOTIONS = [
    {'key': 'Tức giận',    'emoji': '😠', 'color': '#f87171'},
    {'key': 'Ghê tởm',     'emoji': '🤢', 'color': '#a3e635'},
    {'key': 'Sợ hãi',      'emoji': '😨', 'color': '#c084fc'},
    {'key': 'Vui vẻ',      'emoji': '😊', 'color': '#fbbf24'},
    {'key': 'Bình thường', 'emoji': '😐', 'color': '#94a3b8'},
    {'key': 'Buồn bã',     'emoji': '😢', 'color': '#60a5fa'},
    {'key': 'Bất ngờ',     'emoji': '😮', 'color': '#34d399'},
]
EMOTION_KEYS = [e['key'] for e in EMOTIONS]
EMOTION_COLORS = {e['key']: e['color'] for e in EMOTIONS}

def is_valid_image(image_bytes: bytes) -> bool:
    """Kiểm tra magic bytes để chắc chắn đây là file ảnh hợp lệ."""
    # JPEG: FF D8 FF
    # PNG: 89 50 4E 47 0D 0A 1A 0A
    # WEBP: 52 49 46 46 ... 57 45 42 50
    # GIF: 47 49 46 38
    # BMP: 42 4D
    if len(image_bytes) < 12:
        return False
    if image_bytes.startswith(b'\xff\xd8\xff'): return True # JPG
    if image_bytes.startswith(b'\x89PNG\r\n\x1a\n'): return True # PNG
    if image_bytes.startswith(b'RIFF') and image_bytes[8:12] == b'WEBP': return True # WEBP
    if image_bytes.startswith(b'GIF8'): return True # GIF
    if image_bytes.startswith(b'BM'): return True # BMP
    return False

def get_confidence_label(prob: float) -> str:
    if prob >= 75: return "Rất tự tin"
    if prob >= 50: return "Khá tự tin"
    if prob >= 30: return "Phân vân"
    return "Không chắc"


class EmotionAnalyzer:
    def __init__(self):
        logger.info("⏳ Đang tải mô hình AI...")
        try:
            self.model = load_model(MODEL_FILENAME)
            self.face_cascade = cv2.CascadeClassifier(
                cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            )
            logger.info("✅ Tải mô hình thành công!")
        except Exception as e:
            logger.error(f"❌ Lỗi tải mô hình AI: {e}")
            self.model = None

    def analyze_image(self, image_bytes: bytes) -> dict:
        if self.model is None:
            return {"success": False, "message": "Hệ thống AI đang bảo trì (Không tìm thấy model)."}
            
        if not is_valid_image(image_bytes):
            return {"success": False, "message": "File tải lên không đúng định dạng ảnh thực sự."}

        try:
            image = Image.open(io.BytesIO(image_bytes)).convert('RGB')
        except Exception as e:
            logger.warning(f"Lỗi mở ảnh PIL: {e}")
            return {"success": False, "message": "Không thể đọc file ảnh."}

        try:
            img_array = np.array(image)
            img_bgr = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
            gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)

            faces = self.face_cascade.detectMultiScale(
                gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30)
            )

            if len(faces) == 0:
                return {
                    "success": False,
                    "message": "Không tìm thấy khuôn mặt nào trong ảnh. Vui lòng thử ảnh khác chụp rõ mặt hơn."
                }

            # Lấy khuôn mặt lớn nhất (diện tích w*h lớn nhất)
            faces_sorted = sorted(faces, key=lambda f: f[2] * f[3], reverse=True)
            face_count = len(faces_sorted)
            (x, y, w, h) = faces_sorted[0]

            face_roi = gray[y:y+h, x:x+w]
            face_roi_resized = cv2.resize(face_roi, (48, 48))

            face_input = np.expand_dims(face_roi_resized, axis=-1)
            face_input = np.expand_dims(face_input, axis=0) / 255.0
            
            # Catch OOM or model prediction errors
            predictions = self.model.predict(face_input, verbose=0)[0]

            max_index = int(np.argmax(predictions))
            predicted_emotion = EMOTION_KEYS[max_index]
            confidence = round(float(predictions[max_index]) * 100, 2)

            prob_dict = {
                EMOTION_KEYS[i]: round(float(predictions[i]) * 100, 2)
                for i in range(len(EMOTION_KEYS))
            }

            annotated = img_bgr.copy()
            emotion_color_hex = EMOTION_COLORS.get(predicted_emotion, '#7c3aed')
            
            h_val = emotion_color_hex.lstrip('#')
            r, g, b = tuple(int(h_val[i:i+2], 16) for i in (0, 2, 4))
            box_color = (b, g, r)

            for i, (fx, fy, fw, fh) in enumerate(faces_sorted):
                thickness = 3 if i == 0 else 1
                opacity_color = box_color if i == 0 else (100, 100, 100)
                cv2.rectangle(annotated, (fx, fy), (fx+fw, fy+fh), opacity_color, thickness)

            label = f"{predicted_emotion} {confidence:.0f}%"
            font_scale = max(0.5, w / 150)
            cv2.putText(annotated, label, (x, y - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, font_scale, box_color, 2, cv2.LINE_AA)

            _, annotated_buf = cv2.imencode('.jpg', annotated, [cv2.IMWRITE_JPEG_QUALITY, 88])
            annotated_b64 = base64.b64encode(annotated_buf).decode('utf-8')

            face_bgr = cv2.cvtColor(face_roi_resized, cv2.COLOR_GRAY2BGR)
            face_bgr_full = cv2.resize(face_bgr, (200, 200))
            _, face_buf = cv2.imencode('.jpg', face_bgr_full)
            face_b64 = base64.b64encode(face_buf).decode('utf-8')

            return {
                "success": True,
                "predicted_emotion": predicted_emotion,
                "confidence": confidence,
                "confidence_label": get_confidence_label(confidence),
                "probabilities": prob_dict,
                "face_count": face_count,
                "face_image_base64": face_b64,
                "annotated_image_base64": annotated_b64,
            }
        except Exception as e:
            logger.error(f"Lỗi phân tích ảnh AI: {e}")
            return {"success": False, "message": "Có lỗi xảy ra trong quá trình xử lý AI."}


# Khởi tạo instance singleton
analyzer = EmotionAnalyzer()
