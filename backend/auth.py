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
import smtplib
from email.message import EmailMessage
import random
import string

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
# TOKEN EXTRACTION (Bearer header "hoặc" HTTP-only cookie)
# =====================================================================
from fastapi import Cookie

async def _extract_token(request: Request, bearer_token: str | None) -> str | None:
    """Lấy token từ Authorization header (Bearer) hoặc cookie 'emotionai_token'.
    Ưu tiên cookie để hỗ trợ luồng Google OAuth."""
    if bearer_token:
        return bearer_token
    return request.cookies.get("emotionai_token")

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
            detail="Quá nhiều lần thử đăng nhập. Vui lòng thử lại sau 5 phút."
        )
    _login_attempts[client_ip].append(now)

def clear_login_attempts(client_ip: str):
    if client_ip in _login_attempts:
        del _login_attempts[client_ip]

# =====================================================================
# REGISTER & FORGOT PASSWORD RATE LIMITING
# =====================================================================
_register_attempts: dict = defaultdict(list)
_forgot_pw_attempts: dict = defaultdict(list)

def check_register_rate_limit(client_ip: str):
    """Giới hạn tạo tài khoản: tối đa 3 lần mỗi 60 phút."""
    now = time.time()
    _register_attempts[client_ip] = [t for t in _register_attempts[client_ip] if now - t < 3600]
    if len(_register_attempts[client_ip]) >= 3:
        raise HTTPException(status_code=429, detail="Quá nhiều yêu cầu tạo tài khoản. Vui lòng thử lại sau 1 giờ.")
    _register_attempts[client_ip].append(now)

def check_forgot_password_rate_limit(client_ip: str):
    """Giới hạn gửi email quên mật khẩu: tối đa 3 lần mỗi 15 phút."""
    now = time.time()
    _forgot_pw_attempts[client_ip] = [t for t in _forgot_pw_attempts[client_ip] if now - t < 900]
    if len(_forgot_pw_attempts[client_ip]) >= 3:
        raise HTTPException(status_code=429, detail="Quá nhiều yêu cầu cấp lại mật khẩu. Vui lòng thử lại sau 15 phút.")
    _forgot_pw_attempts[client_ip].append(now)

# =====================================================================
# UTILS: JWT & PASSWORDS
# =====================================================================
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

# =====================================================================
# EMAIL & TOKEN UTILITIES
# =====================================================================
def generate_reset_token() -> str:
    """Tạo mã xác nhận 6 chữ số."""
    return ''.join(random.choices(string.digits, k=6))

def send_reset_email(to_email: str, token: str):
    """Gửi email chứa mã reset password bằng SMTP."""
    smtp_server = os.getenv("SMTP_SERVER")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_user = os.getenv("SMTP_USER")
    smtp_pass = os.getenv("SMTP_PASSWORD")

    if not all([smtp_server, smtp_user, smtp_pass]):
        logger.error("Chưa cấu hình SMTP đầy đủ trong .env!")
        return False

    msg = EmailMessage()
    msg.set_content(f"Mã xác nhận để đổi mật khẩu của bạn là: {token}\n\nMã này có hiệu lực trong vòng 15 phút.\nNếu bạn không yêu cầu đổi mật khẩu, vui lòng bỏ qua email này.")
    msg['Subject'] = 'EmotionAI - Đặt lại mật khẩu'
    msg['From'] = smtp_user
    msg['To'] = to_email

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_user, smtp_pass)
        server.send_message(msg)
        server.quit()
        logger.info(f"Đã gửi email khôi phục mật khẩu tới {to_email}")
        return True
    except Exception as e:
        logger.error(f"Lỗi gửi email: {e}")
        return False

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
async def get_current_user(request: Request, token: str = Depends(oauth2_scheme)) -> dict:
    """Lấy thông tin user từ JWT token (Bearer header hoặc cookie). Raise 401 nếu không hợp lệ."""
    token = await _extract_token(request, token)
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

async def get_optional_user(request: Request, token: str = Depends(oauth2_scheme)) -> dict | None:
    """Trả về user nếu có token hợp lệ (Bearer hoặc cookie), None nếu không có. Không raise lỗi."""
    token = await _extract_token(request, token)
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
