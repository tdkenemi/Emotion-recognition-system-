import sys
import os
import random
from datetime import datetime, timedelta

# Đảm bảo import được backend
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.db import history_collection, feedback_collection
from backend.ai_service import EMOTION_KEYS

def seed_data():
    print("Bắt đầu tạo dữ liệu mẫu...")
    
    # Xóa dữ liệu cũ
    history_collection.delete_many({})
    feedback_collection.delete_many({})
    
    now = datetime.now()
    
    # Tạo 50 bản ghi history
    for i in range(50):
        time = now - timedelta(hours=random.randint(0, 100), minutes=random.randint(0, 60))
        predicted = random.choice(EMOTION_KEYS)
        history_collection.insert_one({
            "time": time,
            "filename": f"demo_img_{i}.jpg",
            "ai_prediction": predicted,
            "confidence": round(random.uniform(50, 99), 2),
            "face_count": 1,
            "ip": f"192.168.1.{random.randint(1, 255)}"
        })
        
        # 30% có feedback
        if random.random() < 0.3:
            correct = predicted if random.random() < 0.8 else random.choice(EMOTION_KEYS)
            feedback_collection.insert_one({
                "time": time + timedelta(minutes=random.randint(1, 5)),
                "filename": f"demo_img_{i}.jpg",
                "ai_prediction": predicted,
                "correct_emotion": correct,
                "is_correct": predicted == correct
            })
            
    print("✅ Đã tạo xong 50 bản ghi mẫu!")

if __name__ == "__main__":
    seed_data()
