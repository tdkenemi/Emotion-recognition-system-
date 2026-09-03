import os
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv
import logging

load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Security: Read URI from environment, DO NOT hardcode
MONGO_URI = os.getenv("MONGODB_URI")

if not MONGO_URI:
    logger.warning("MONGODB_URI is not set in environment variables! Using localhost fallback for development.")
    MONGO_URI = "mongodb://localhost:27017/"

try:
    # Connection pooling and timeout settings
    client = MongoClient(
        MONGO_URI,
        serverSelectionTimeoutMS=5000,
        connectTimeoutMS=10000,
        socketTimeoutMS=10000,
        server_api=ServerApi('1')
    )
    
    db = client['emotion_app_db']
    history_collection = db['history']
    feedback_collection = db['feedback']
    users_collection = db['users'] # Collection for Auth
    
    # Ping to verify connection
    client.admin.command('ping')
    logger.info("MongoDB Connected Successfully!")
except Exception as e:
    logger.error(f"MongoDB Connection Error: {e}")
    # We don't exit here so the app can still start, but DB ops will fail gracefully
