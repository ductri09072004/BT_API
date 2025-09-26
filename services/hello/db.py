import os
from pathlib import Path
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

# Load .env ở project root (chạy được dù gọi từ thư mục con)
load_dotenv()  # cố gắng load mặc định
root_env = Path(__file__).resolve().parents[2] / ".env"
if root_env.exists():
    load_dotenv(dotenv_path=root_env, override=True)

# Lấy URI từ biến môi trường MONGODB_URI
MONGODB_URI = os.getenv("MONGODB_URI")

if not MONGODB_URI:
    # Still create a client placeholder to avoid import errors; will fail on use
    client = None  # type: ignore
    db = None  # type: ignore
else:
    client = AsyncIOMotorClient(MONGODB_URI)
    # Chọn database theo nhu cầu; mặc định dùng 'test'
    db = client[os.getenv("MONGODB_DB", "test")]


