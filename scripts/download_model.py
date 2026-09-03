import os
import urllib.request
import sys

MODEL_URL = "https://github.com/khangtrieutdk/emotionai/releases/download/v1.0/emotion_model.h5"
MODEL_PATH = "emotion_model.h5"

def download_model():
    print(f"Bắt đầu tải model từ {MODEL_URL}...")
    try:
        urllib.request.urlretrieve(MODEL_URL, MODEL_PATH)
        print("✅ Tải model thành công!")
    except Exception as e:
        print(f"❌ Lỗi tải model: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if not os.path.exists(MODEL_PATH):
        download_model()
    else:
        print("Model đã tồn tại, bỏ qua tải.")
