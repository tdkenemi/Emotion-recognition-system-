import pytest
from fastapi.testclient import TestClient
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert "memory_usage_mb" in response.json()

def test_home_page():
    response = client.get("/")
    assert response.status_code == 200
    assert "EmotionAI" in response.text

def test_register_login():
    # Test register
    test_user = "testuser123"
    test_pass = "password123"
    test_email = "testuser123@example.com"
    
    res_reg = client.post("/api/register", data={"username": test_user, "password": test_pass, "email": test_email})
    # If already exists, it will be 400. Otherwise 200.
    assert res_reg.status_code in [200, 400]
    
    # Test login
    res_login = client.post("/api/login", data={"username": test_user, "password": test_pass})
    assert res_login.status_code == 200
    assert "access_token" in res_login.json()
    
    token = res_login.json()["access_token"]
    
    # Test /api/me
    res_me = client.get("/api/me", headers={"Authorization": f"Bearer {token}"})
    assert res_me.status_code == 200
    assert res_me.json()["username"] == test_user

def test_invalid_feedback():
    response = client.post("/api/feedback", data={
        "filename": "test.jpg",
        "ai_prediction": "Vui vẻ",
        "correct_emotion": "Cảm xúc lạ"  # Không nằm trong danh sách
    })
    assert response.status_code == 422
