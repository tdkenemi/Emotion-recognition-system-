"""
Pydantic models for request/response validation.
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime


class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=30, description="Tên đăng nhập")
    password: str = Field(..., min_length=8, description="Mật khẩu ít nhất 8 ký tự")

    @field_validator('username')
    @classmethod
    def username_alphanumeric(cls, v):
        import re
        if not re.match(r'^[a-zA-Z0-9_]+$', v):
            raise ValueError('Tên đăng nhập chỉ được dùng chữ, số và dấu gạch dưới')
        return v.lower()

    @field_validator('password')
    @classmethod
    def password_strength(cls, v):
        if len(v) < 8:
            raise ValueError('Mật khẩu phải có ít nhất 8 ký tự')
        return v


class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    username: str
    role: str
    created_at: Optional[str] = None


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    username: str
    role: str


class FeedbackCreate(BaseModel):
    filename: str = Field(..., min_length=1, max_length=255)
    ai_prediction: str
    correct_emotion: str

    @field_validator('filename')
    @classmethod
    def sanitize_filename(cls, v):
        import re
        # Remove path traversal attempts
        v = re.sub(r'[\\/<>:"|?*]', '_', v)
        return v


class HistoryRecord(BaseModel):
    id: str
    time: str
    filename: str
    ai_prediction: str
    confidence: float
    face_count: int
    ip: Optional[str] = None
    batch: bool = False


class PaginationMeta(BaseModel):
    page: int
    per_page: int
    total: int
    total_pages: int


class HealthResponse(BaseModel):
    status: str
    version: str
    model_status: str
    memory_usage_mb: float
    uptime_seconds: float
    time: str
