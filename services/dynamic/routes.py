from fastapi import APIRouter, HTTPException
import json
import os

router = APIRouter()

# File để lưu trữ routes
ROUTES_FILE = "data/routes.json"

# Dictionary để lưu trữ các routes động
dynamic_routes = {}

def load_routes():
    """Load routes từ file JSON"""
    global dynamic_routes
    
    # Tạo thư mục data nếu chưa tồn tại
    os.makedirs(os.path.dirname(ROUTES_FILE), exist_ok=True)
    
    if os.path.exists(ROUTES_FILE):
        try:
            with open(ROUTES_FILE, 'r', encoding='utf-8') as f:
                dynamic_routes = json.load(f)
                print(f"Loaded {len(dynamic_routes)} routes from {ROUTES_FILE}")
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading routes: {e}")
            dynamic_routes = {}
    else:
        print(f"No routes file found, starting with empty routes")
        dynamic_routes = {}

# Load routes khi import
load_routes()

@router.get("/healthz")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok", "service": "dynamic"}

# Route handler động cho các routes được tạo
@router.get("/{dynamic_path:path}")
async def dynamic_route_handler(dynamic_path: str):
    """Handler cho các routes động"""
    full_path = '/' + dynamic_path
    
    # Bỏ qua các routes cố định
    if full_path in ['/healthz', '/A'] or full_path.startswith('/admin'):
        raise HTTPException(status_code=404, detail="Route not found")
    
    # Kiểm tra xem route có tồn tại trong dynamic_routes không
    if full_path in dynamic_routes:
        return dynamic_routes[full_path]
    else:
        raise HTTPException(status_code=404, detail="Route not found")
