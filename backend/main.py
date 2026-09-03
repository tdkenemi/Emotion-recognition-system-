"""
EmotionAI - Backend chính (FastAPI)
Tác giả: Triệu Duy Khang | ĐH Nguyễn Tất Thành - Khoa CNTT
"""
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Request, Depends, status
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.exception_handlers import http_exception_handler
from starlette.exceptions import HTTPException as StarletteHTTPException
from contextlib import asynccontextmanager
import uvicorn
from datetime import datetime
import os
import uuid
import time
import logging
from pathlib import Path
from typing import List, Optional

# =====================================================================
# SETUP LOGGING
# =====================================================================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("emotionai")

# Đường dẫn tuyệt đối
BASE_DIR = Path(__file__).resolve().parent.parent

from backend.ai_service import analyzer, EMOTION_KEYS, EMOTIONS
from backend.db import history_collection, feedback_collection, users_collection
from backend.auth import (
    get_password_hash, verify_password, create_access_token,
    get_current_user, get_current_admin, get_optional_user,
    check_login_rate_limit, clear_login_attempts
)
from backend.models import UserCreate, FeedbackCreate

# =====================================================================
# SERVER START TIME (for uptime tracking)
# =====================================================================
SERVER_START_TIME = time.time()

# =====================================================================
# LIFESPAN (thay thế on_event deprecated)
# =====================================================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    # === STARTUP ===
    logger.info("EmotionAI Server dang khoi dong...")
    admin_user = os.getenv("ADMIN_USER", "admin")
    admin_pass = os.getenv("ADMIN_PASSWORD", "")

    if admin_pass and len(admin_pass) >= 8:
        existing = users_collection.find_one({"username": admin_user})
        if not existing:
            users_collection.insert_one({
                "username": admin_user,
                "password": get_password_hash(admin_pass),
                "role": "admin",
                "created_at": datetime.now()
            })
            logger.info(f"Da tao tai khoan Admin mac dinh: {admin_user}")
        else:
            logger.info(f"Admin '{admin_user}' da ton tai, bo qua.")
    else:
        logger.warning("ADMIN_PASSWORD trong .env qua yeu (< 8 ky tu) hoac chua dat. Bo qua tao admin tu dong.")

    logger.info("EmotionAI Server san sang tai http://localhost:8000")
    yield
    # === SHUTDOWN ===
    logger.info("EmotionAI Server dang tat...")

# =====================================================================
# APP INIT
# =====================================================================
app = FastAPI(
    title="EmotionAI API",
    description="""
## API Nhận Diện Cảm Xúc Khuôn Mặt

Sử dụng **Deep Learning (CNN)** được huấn luyện trên tập dữ liệu **FER2013** để nhận diện 7 loại cảm xúc:
😠 Tức giận | 🤢 Ghê tởm | 😨 Sợ hãi | 😊 Vui vẻ | 😐 Bình thường | 😢 Buồn bã | 😮 Bất ngờ

### Tác giả
**Triệu Duy Khang** | ĐH Nguyễn Tất Thành - Khoa CNTT
    """,
    version="3.1.0",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# =====================================================================
# CORS MIDDLEWARE
# =====================================================================
cors_origins_env = os.getenv("CORS_ORIGINS", "")
cors_origins = [o.strip() for o in cors_origins_env.split(",")] if cors_origins_env else ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# =====================================================================
# SECURITY & LOGGING MIDDLEWARE
# =====================================================================
@app.middleware("http")
async def security_and_logging_middleware(request: Request, call_next):
    req_id = str(uuid.uuid4())[:8]
    start_time = time.time()
    response = await call_next(request)
    process_time = (time.time() - start_time) * 1000

    # Security Headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "SAMEORIGIN"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["X-Request-ID"] = req_id

    # Skip logging for static files
    if not request.url.path.startswith("/static"):
        logger.info(f"[{req_id}] {request.method} {request.url.path} → {response.status_code} ({process_time:.1f}ms)")

    return response

# =====================================================================
# RATE LIMITING (predict only)
# =====================================================================
RATE_LIMIT_DURATION = 60
RATE_LIMIT_REQUESTS = 30
rate_limits: dict = {}

def check_rate_limit(client_ip: str):
    now = time.time()
    if client_ip not in rate_limits:
        rate_limits[client_ip] = []
    rate_limits[client_ip] = [t for t in rate_limits[client_ip] if now - t < RATE_LIMIT_DURATION]
    if len(rate_limits[client_ip]) >= RATE_LIMIT_REQUESTS:
        raise HTTPException(
            status_code=429,
            detail=f"Bạn đã đạt giới hạn {RATE_LIMIT_REQUESTS} phân tích/phút. Vui lòng đợi."
        )
    rate_limits[client_ip].append(now)

# =====================================================================
# STATIC FILES & TEMPLATES
# =====================================================================
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif", "image/bmp"}
MAX_FILE_SIZE_MB = 15

# =====================================================================
# CUSTOM 404 HANDLER
# =====================================================================
@app.exception_handler(StarletteHTTPException)
async def custom_404_handler(request: Request, exc: StarletteHTTPException):
    if exc.status_code == 404 and not request.url.path.startswith("/api"):
        return templates.TemplateResponse("404.html", {"request": request}, status_code=404)
    return await http_exception_handler(request, exc)

# =====================================================================
# PAGE ROUTES
# =====================================================================
@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def home(request: Request):
    total = history_collection.count_documents({}) if history_collection is not None else 0
    return templates.TemplateResponse("index.html", {"request": request, "total_analyses": total})

@app.get("/admin", response_class=HTMLResponse, include_in_schema=False)
async def admin(request: Request):
    return templates.TemplateResponse("admin.html", {"request": request})

# =====================================================================
# AUTH API
# =====================================================================
@app.post("/api/register", tags=["Auth"], summary="Đăng ký tài khoản mới")
async def register(request: Request, form_data: OAuth2PasswordRequestForm = Depends()):
    username = form_data.username.strip().lower()
    password = form_data.password

    # Validate
    if len(username) < 3 or len(username) > 30:
        raise HTTPException(status_code=422, detail="Tên đăng nhập phải từ 3-30 ký tự")
    if len(password) < 8:
        raise HTTPException(status_code=422, detail="Mật khẩu phải có ít nhất 8 ký tự")
    if not username.replace('_', '').isalnum():
        raise HTTPException(status_code=422, detail="Tên đăng nhập chỉ được dùng chữ, số và dấu gạch dưới")

    existing = users_collection.find_one({"username": username})
    if existing:
        raise HTTPException(status_code=409, detail="Tên đăng nhập đã được sử dụng")

    users_collection.insert_one({
        "username": username,
        "password": get_password_hash(password),
        "role": "user",
        "created_at": datetime.now()
    })
    logger.info(f"New user registered: {username}")
    return {"message": "Đăng ký thành công! Chào mừng bạn đến với EmotionAI."}

@app.post("/api/login", tags=["Auth"], summary="Đăng nhập nhận JWT Token")
async def login(request: Request, form_data: OAuth2PasswordRequestForm = Depends()):
    client_ip = request.client.host
    check_login_rate_limit(client_ip)

    username = form_data.username.strip().lower()
    user = users_collection.find_one({"username": username})

    if not user or not verify_password(form_data.password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Tên đăng nhập hoặc mật khẩu không đúng",
            headers={"WWW-Authenticate": "Bearer"},
        )

    clear_login_attempts(client_ip)
    access_token = create_access_token(data={"sub": user["username"], "role": user.get("role", "user")})
    logger.info(f"User logged in: {username} from {client_ip}")
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "username": user["username"],
        "role": user.get("role", "user")
    }

@app.get("/api/me", tags=["Auth"], summary="Lấy thông tin user hiện tại")
async def get_me(current_user: dict = Depends(get_current_user)):
    return current_user

# =====================================================================
# EMOTION INFO API
# =====================================================================
@app.get("/api/emotions", tags=["Info"], summary="Danh sách 7 cảm xúc được nhận diện")
async def get_emotions():
    return {"emotions": EMOTIONS, "total": len(EMOTIONS)}

# =====================================================================
# PREDICT API
# =====================================================================
@app.post("/api/predict", tags=["AI"], summary="Phân tích cảm xúc từ ảnh upload")
async def predict_emotion(
    request: Request,
    file: UploadFile = File(...),
    current_user: Optional[dict] = Depends(get_optional_user)
):
    client_ip = request.client.host
    check_rate_limit(client_ip)

    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(status_code=415, detail=f"Chỉ chấp nhận file ảnh (JPG/PNG/WEBP). Nhận được: {file.content_type}")

    contents = await file.read()
    size_mb = len(contents) / (1024 * 1024)
    if size_mb > MAX_FILE_SIZE_MB:
        raise HTTPException(status_code=413, detail=f"File quá lớn ({size_mb:.1f}MB). Tối đa {MAX_FILE_SIZE_MB}MB.")

    result = analyzer.analyze_image(contents)

    if result["success"]:
        record = {
            "time": datetime.now(),
            "filename": file.filename or "unknown",
            "ai_prediction": result["predicted_emotion"],
            "confidence": result.get("confidence", 0),
            "face_count": result.get("face_count", 1),
            "ip": client_ip,
            "user": current_user["username"] if current_user else None,
            "batch": False
        }
        try:
            history_collection.insert_one(record)
        except Exception as e:
            logger.warning(f"MongoDB insert failed: {e}")
        return JSONResponse(content=result)
    else:
        return JSONResponse(content=result, status_code=400)

@app.post("/api/predict/batch", tags=["AI"], summary="Phân tích nhiều ảnh cùng lúc (tối đa 10)")
async def predict_batch(
    request: Request,
    files: List[UploadFile] = File(...),
    current_user: Optional[dict] = Depends(get_optional_user)
):
    client_ip = request.client.host
    check_rate_limit(client_ip)

    if len(files) > 10:
        raise HTTPException(status_code=400, detail="Tối đa 10 ảnh mỗi lần.")

    results = []
    for file in files:
        if file.content_type not in ALLOWED_IMAGE_TYPES:
            results.append({"filename": file.filename, "success": False, "message": "Sai định dạng"})
            continue
        contents = await file.read()
        if len(contents) / (1024 * 1024) > MAX_FILE_SIZE_MB:
            results.append({"filename": file.filename, "success": False, "message": "File quá lớn"})
            continue
        res = analyzer.analyze_image(contents)
        res["filename"] = file.filename
        results.append(res)
        if res["success"]:
            try:
                history_collection.insert_one({
                    "time": datetime.now(),
                    "filename": file.filename,
                    "ai_prediction": res["predicted_emotion"],
                    "confidence": res.get("confidence", 0),
                    "face_count": res.get("face_count", 1),
                    "ip": client_ip,
                    "user": current_user["username"] if current_user else None,
                    "batch": True
                })
            except Exception:
                pass
    return {"success": True, "count": len(results), "results": results}

# =====================================================================
# FEEDBACK API
# =====================================================================
@app.post("/api/feedback", tags=["Feedback"], summary="Gửi feedback về kết quả phân tích")
async def submit_feedback(
    filename: str = Form(...),
    ai_prediction: str = Form(...),
    correct_emotion: str = Form(...),
    current_user: Optional[dict] = Depends(get_optional_user)
):
    if correct_emotion not in EMOTION_KEYS:
        raise HTTPException(status_code=422, detail=f"Cảm xúc '{correct_emotion}' không hợp lệ.")

    record = {
        "time": datetime.now(),
        "filename": filename[:255],
        "ai_prediction": ai_prediction,
        "correct_emotion": correct_emotion,
        "is_correct": ai_prediction == correct_emotion,
        "user": current_user["username"] if current_user else None
    }
    try:
        feedback_collection.insert_one(record)
    except Exception as e:
        logger.warning(f"Feedback insert failed: {e}")

    return {"success": True, "message": "Cảm ơn bạn đã góp ý! AI sẽ ngày càng thông minh hơn."}

# =====================================================================
# HISTORY API (cá nhân)
# =====================================================================
@app.get("/api/history/me", tags=["History"], summary="Lịch sử phân tích của tôi")
async def get_my_history(
    page: int = 1,
    per_page: int = 20,
    current_user: dict = Depends(get_current_user)
):
    try:
        skip = (page - 1) * per_page
        username = current_user["username"]
        query = {"user": username}
        items = list(history_collection.find(query).sort("time", -1).skip(skip).limit(per_page))
        total = history_collection.count_documents(query)
        for item in items:
            item["_id"] = str(item["_id"])
            item["time"] = item["time"].strftime("%Y-%m-%d %H:%M:%S") if isinstance(item["time"], datetime) else str(item["time"])
        return {
            "history": items,
            "pagination": {"page": page, "per_page": per_page, "total": total, "total_pages": max(1, (total + per_page - 1) // per_page)}
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# =====================================================================
# ADMIN API
# =====================================================================
@app.get("/api/history", tags=["Admin"], summary="[Admin] Lịch sử phân tích toàn hệ thống")
async def get_all_history(
    page: int = 1,
    per_page: int = 20,
    emotion: Optional[str] = None,
    current_user: dict = Depends(get_current_admin)
):
    try:
        skip = (page - 1) * per_page
        query = {}
        if emotion and emotion in EMOTION_KEYS:
            query["ai_prediction"] = emotion

        history = list(history_collection.find(query).sort("time", -1).skip(skip).limit(per_page))
        feedbacks = list(feedback_collection.find().sort("time", -1).skip(0).limit(per_page))
        total = history_collection.count_documents(query)

        for h in history:
            h["_id"] = str(h["_id"])
            h["time"] = h["time"].strftime("%Y-%m-%d %H:%M:%S") if isinstance(h["time"], datetime) else str(h["time"])
        for f in feedbacks:
            f["_id"] = str(f["_id"])
            f["time"] = f["time"].strftime("%Y-%m-%d %H:%M:%S") if isinstance(f["time"], datetime) else str(f["time"])

        return {
            "history": history,
            "feedbacks": feedbacks,
            "pagination": {"page": page, "per_page": per_page, "total": total, "total_pages": max(1, (total + per_page - 1) // per_page)}
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/history/{record_id}", tags=["Admin"], summary="[Admin] Xóa 1 bản ghi lịch sử")
async def delete_history_record(record_id: str, current_user: dict = Depends(get_current_admin)):
    from bson import ObjectId
    try:
        result = history_collection.delete_one({"_id": ObjectId(record_id)})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Không tìm thấy bản ghi")
        return {"success": True, "message": "Đã xóa bản ghi"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"ID không hợp lệ: {str(e)}")

@app.get("/api/users", tags=["Admin"], summary="[Admin] Danh sách tất cả người dùng")
async def get_users(page: int = 1, per_page: int = 20, current_user: dict = Depends(get_current_admin)):
    try:
        skip = (page - 1) * per_page
        users = list(users_collection.find({}, {"password": 0}).sort("created_at", -1).skip(skip).limit(per_page))
        total = users_collection.count_documents({})
        for u in users:
            u["_id"] = str(u["_id"])
            if "created_at" in u and isinstance(u["created_at"], datetime):
                u["created_at"] = u["created_at"].strftime("%Y-%m-%d %H:%M:%S")
        return {
            "users": users,
            "pagination": {"page": page, "per_page": per_page, "total": total, "total_pages": max(1, (total + per_page - 1) // per_page)}
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# =====================================================================
# STATS API (Admin + Cache)
# =====================================================================
_stats_cache: dict = {"data": None, "timestamp": 0}

@app.get("/api/stats", tags=["Admin"], summary="[Admin] Thống kê tổng hợp (cache 60s)")
async def get_stats(current_user: dict = Depends(get_current_admin)):
    now = time.time()
    if _stats_cache["data"] and (now - _stats_cache["timestamp"] < 60):
        return _stats_cache["data"]

    try:
        total = history_collection.count_documents({})
        fb_total = feedback_collection.count_documents({})
        correct = feedback_collection.count_documents({"is_correct": True})
        accuracy = round(correct / fb_total * 100, 1) if fb_total > 0 else None

        dist_pipeline = [
            {"$group": {"_id": "$ai_prediction", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        distribution = {r["_id"]: r["count"] for r in history_collection.aggregate(dist_pipeline) if r["_id"]}

        top_emotion = max(distribution, key=distribution.get) if distribution else None

        # Users count
        user_count = users_collection.count_documents({"role": "user"})

        data = {
            "total_analyses": total,
            "total_feedbacks": fb_total,
            "correct_feedbacks": correct,
            "accuracy_percent": accuracy,
            "top_emotion": top_emotion,
            "emotion_distribution": distribution,
            "user_count": user_count,
        }
        _stats_cache["data"] = data
        _stats_cache["timestamp"] = now
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi truy vấn: {str(e)}")

@app.get("/api/stats/trend", tags=["Admin"], summary="[Admin] Xu hướng phân tích 7 ngày gần nhất")
async def get_trend(current_user: dict = Depends(get_current_admin)):
    """Trả dữ liệu cho Line chart: số lượt phân tích mỗi ngày trong 7 ngày qua."""
    try:
        from datetime import timedelta
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        result = []
        for i in range(6, -1, -1):
            day = today - timedelta(days=i)
            next_day = day + timedelta(days=1)
            count = history_collection.count_documents({"time": {"$gte": day, "$lt": next_day}})
            result.append({"date": day.strftime("%d/%m"), "count": count})
        return {"trend": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# =====================================================================
# HEALTH CHECK
# =====================================================================
import psutil

@app.get("/api/health", tags=["System"], summary="Kiểm tra trạng thái server")
async def health_check():
    process = psutil.Process(os.getpid())
    memory_mb = process.memory_info().rss / 1024 / 1024
    uptime = time.time() - SERVER_START_TIME
    return {
        "status": "ok",
        "version": "3.1.0",
        "model_status": "loaded" if analyzer.model is not None else "failed",
        "memory_usage_mb": round(memory_mb, 2),
        "uptime_seconds": round(uptime, 1),
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
