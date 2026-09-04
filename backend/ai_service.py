import cv2
import numpy as np
from deepface import DeepFace
from PIL import Image
import base64
import io
import logging

logger = logging.getLogger(__name__)

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

DEEPFACE_LABEL_MAP = {
    'angry': 'Tức giận',
    'disgust': 'Ghê tởm',
    'fear': 'Sợ hãi',
    'happy': 'Vui vẻ',
    'sad': 'Buồn bã',
    'surprise': 'Bất ngờ',
    'neutral': 'Bình thường'
}

def is_valid_image(image_bytes: bytes) -> bool:
    """Kiểm tra magic bytes để chắc chắn đây là file ảnh hợp lệ."""
    if len(image_bytes) < 12: return False
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
        logger.info("⏳ Đang khởi tạo mô hình AI (DeepFace)...")
        try:
            self.ready = True
            logger.info("✅ Sẵn sàng sử dụng DeepFace!")
        except Exception as e:
            logger.error(f"❌ Lỗi tải mô hình AI: {e}")
            self.ready = False

    def analyze_image(self, image_bytes: bytes) -> dict:
        if not getattr(self, 'ready', False):
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

            try:
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                    future = executor.submit(DeepFace.analyze, img_path=img_bgr, actions=['emotion'], enforce_detection=True)
                    results = future.result(timeout=15) # Ngắt nếu quá 15 giây
            except concurrent.futures.TimeoutError:
                logger.error("DeepFace analyze timeout")
                return {"success": False, "message": "Hệ thống AI xử lý quá lâu, vui lòng thử lại sau."}
            except ValueError as ve:
                return {
                    "success": False,
                    "message": "Không tìm thấy khuôn mặt nào trong ảnh. Vui lòng thử ảnh chụp rõ mặt hơn."
                }

            if not isinstance(results, list):
                results = [results]

            # Lấy khuôn mặt lớn nhất
            faces_sorted = sorted(results, key=lambda f: f['region']['w'] * f['region']['h'], reverse=True)
            face_count = len(faces_sorted)
            largest_face = faces_sorted[0]

            df_emotion = largest_face['dominant_emotion']
            predicted_emotion = DEEPFACE_LABEL_MAP.get(df_emotion, 'Bình thường')
            confidence = round(float(largest_face['emotion'][df_emotion]), 2)

            prob_dict = {
                DEEPFACE_LABEL_MAP.get(k, k): round(float(v), 2)
                for k, v in largest_face['emotion'].items()
            }

            annotated = img_bgr.copy()
            emotion_color_hex = EMOTION_COLORS.get(predicted_emotion, '#7c3aed')
            
            h_val = emotion_color_hex.lstrip('#')
            r, g, b = tuple(int(h_val[i:i+2], 16) for i in (0, 2, 4))
            box_color = (b, g, r)

            for i, res in enumerate(faces_sorted):
                region = res['region']
                fx, fy, fw, fh = region['x'], region['y'], region['w'], region['h']
                thickness = 3 if i == 0 else 1
                opacity_color = box_color if i == 0 else (100, 100, 100)
                cv2.rectangle(annotated, (fx, fy), (fx+fw, fy+fh), opacity_color, thickness)

            x, y = largest_face['region']['x'], largest_face['region']['y']
            w, h = largest_face['region']['w'], largest_face['region']['h']
            
            label = f"{predicted_emotion} {confidence:.0f}%"
            font_scale = max(0.5, w / 150)
            cv2.putText(annotated, label, (x, max(0, y - 10)),
                        cv2.FONT_HERSHEY_SIMPLEX, font_scale, box_color, 2, cv2.LINE_AA)

            _, annotated_buf = cv2.imencode('.jpg', annotated, [cv2.IMWRITE_JPEG_QUALITY, 88])
            annotated_b64 = base64.b64encode(annotated_buf).decode('utf-8')

            face_roi = img_bgr[y:y+h, x:x+w]
            if face_roi.size > 0:
                face_bgr_full = cv2.resize(face_roi, (200, 200))
            else:
                face_bgr_full = np.zeros((200, 200, 3), dtype=np.uint8)
                
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
