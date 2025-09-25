from fastapi import APIRouter, HTTPException, Depends, Header
from typing import Optional
import json
import os

router = APIRouter()

# API Key cho admin (trong thực tế nên lưu trong environment variable)
ADMIN_API_KEY = "admin-secret-key-123"

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

def save_routes():
    """Save routes vào file JSON"""
    try:
        with open(ROUTES_FILE, 'w', encoding='utf-8') as f:
            json.dump(dynamic_routes, f, indent=2, ensure_ascii=False)
            print(f"Saved {len(dynamic_routes)} routes to {ROUTES_FILE}")
    except IOError as e:
        print(f"Error saving routes: {e}")

def require_api_key(x_api_key: Optional[str] = Header(None)):
    """Dependency để kiểm tra X-API-Key"""
    if x_api_key != ADMIN_API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized. Missing or invalid X-API-Key")
    return x_api_key

# Load routes khi import
load_routes()

@router.get("/healthz")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok", "service": "admin"}

# Admin API endpoints
@router.post("/admin/routes")
async def create_route(route_data: dict, api_key: str = Depends(require_api_key)):
    """Tạo route mới"""
    if 'path' not in route_data:
        raise HTTPException(status_code=400, detail="Missing 'path' in request body")
    
    path = route_data['path']
    message = route_data.get('message', f'this is {path}')
    
    # Đảm bảo path bắt đầu bằng /
    if not path.startswith('/'):
        path = '/' + path
    
    # Kiểm tra xem route đã tồn tại chưa
    if path in dynamic_routes:
        raise HTTPException(status_code=409, detail=f"Route {path} already exists")
    
    # Lưu JSON object vào dictionary
    dynamic_routes[path] = {"message": message}
    
    # Save routes vào file
    save_routes()
    
    return {"message": f"Route {path} created successfully", "path": path}

@router.get("/admin/routes")
async def list_routes(api_key: str = Depends(require_api_key)):
    """Liệt kê tất cả routes đã tạo"""
    routes_list = [{"path": path, "response": response} for path, response in dynamic_routes.items()]
    return {"routes": routes_list, "count": len(routes_list)}

@router.delete("/admin/routes/{route_path:path}")
async def delete_route(route_path: str, api_key: str = Depends(require_api_key)):
    """Xóa route"""
    # Đảm bảo path bắt đầu bằng /
    if not route_path.startswith('/'):
        route_path = '/' + route_path
    
    if route_path not in dynamic_routes:
        raise HTTPException(status_code=404, detail=f"Route {route_path} not found")
    
    # Xóa khỏi dictionary
    del dynamic_routes[route_path]
    
    # Save routes vào file
    save_routes()
    
    return {"message": f"Route {route_path} deleted successfully"}
