"""
Authentication & authorization utilities.
JWT tokens, password hashing, dependency injection.
"""
import os
import time
from collections import defaultdict
from datetime import datetime, timedelta

from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from dotenv import load_dotenv
import logging

load_dotenv()
logger = logging.getLogger(__name__)

SECRET_KEY = os.getenv("SECRET_KEY", "CHANGE_ME_USE_PYTHON_SECRETS_TOKEN_HEX_32")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))

if SECRET_KEY == "CHANGE_ME_USE_PYTHON_SECRETS_TOKEN_HEX_32":
    logger.warning("SECRET_KEY is using default! Set a strong random key in .env for production.")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/login", auto_error=False)

# =====================================================================
# LOGIN RATE LIMITING (brute-force protection)
# =====================================================================
_login_attempts: dict = defaultdict(list)
LOGIN_RATE_LIMIT_REQUESTS = 5   # max 5 attempts
LOGIN_RATE_LIMIT_WINDOW = 300   # per 5 minutes

def check_login_rate_limit(client_ip: str):
    """Chặn brute-force: tối đa 5 lần đăng nhập mỗi 5 phút."""
    now = time.time()
    _login_attempts[client_ip] = [
        t for t in _login_attempts[client_ip]
        if now - t < LOGIN_RATE_LIMIT_WINDOW
    ]
    if len(_login_attempts[client_ip]) >= LOGIN_RATE_LIMIT_REQUESTS:
        raise HTTPException(
            status_code=429,
            detail=f"Quá nhiều lần đăng nhập thất bại. Vui lòng thử lại sau {LOGIN_RATE_LIMIT_WINDOW // 60} phút."
        )
    _login_attempts[client_ip].append(now)

def clear_login_attempts(client_ip: str):
    """Xóa record khi đăng nhập thành công."""
    _login_attempts.pop(client_ip, None)

# =====================================================================
# PASSWORD UTILITIES
# =====================================================================
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

# =====================================================================
# JWT UTILITIES
# =====================================================================
def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire, "iat": datetime.utcnow()})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# =====================================================================
# DEPENDENCY INJECTION
# =====================================================================
async def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    """Lấy thông tin user từ JWT token. Raise 401 nếu không hợp lệ."""
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Vui lòng đăng nhập để sử dụng tính năng này",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        role: str = payload.get("role", "user")
        if username is None:
            raise HTTPException(status_code=401, detail="Token không hợp lệ")
        return {"username": username, "role": role}
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token đã hết hạn hoặc không hợp lệ. Vui lòng đăng nhập lại.",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def get_optional_user(token: str = Depends(oauth2_scheme)) -> dict | None:
    """Trả về user nếu có token hợp lệ, None nếu không có. Không raise lỗi."""
    if not token:
        return None
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        role: str = payload.get("role", "user")
        if username:
            return {"username": username, "role": role}
    except JWTError:
        pass
    return None

async def get_current_admin(current_user: dict = Depends(get_current_user)) -> dict:
    """Chỉ cho phép user có role='admin' tiếp tục."""
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không có quyền truy cập chức năng này (Chỉ dành cho Admin)"
        )
    return current_user
