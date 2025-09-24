from flask import Flask, jsonify, request
import functools
import json
import os

app = Flask(__name__)

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

# Load routes khi khởi động
load_routes()

def require_api_key(f):
    """Decorator để kiểm tra X-API-Key"""
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if api_key != ADMIN_API_KEY:
            return jsonify({"error": "Unauthorized. Missing or invalid X-API-Key"}), 401
        return f(*args, **kwargs)
    return decorated_function

@app.route('/healthz', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "ok"})

@app.route('/A', methods=['GET'])
def hello_world():
    """Hello world endpoint"""
    return jsonify({"message": "hello world"})

# Route handler động cho các routes được tạo (tránh xung đột với routes cố định)
@app.route('/<path:dynamic_path>', methods=['GET'])
def dynamic_route_handler(dynamic_path):
    """Handler cho các routes động"""
    full_path = '/' + dynamic_path
    
    # Bỏ qua các routes cố định
    if full_path in ['/healthz', '/A'] or full_path.startswith('/admin'):
        return jsonify({"error": "Route not found"}), 404
    
    # Kiểm tra xem route có tồn tại trong dynamic_routes không
    if full_path in dynamic_routes:
        return jsonify(dynamic_routes[full_path])
    else:
        return jsonify({"error": "Route not found"}), 404

# Admin API endpoints
@app.route('/admin/routes', methods=['POST'])
@require_api_key
def create_route():
    """Tạo route mới"""
    data = request.get_json()
    
    if not data or 'path' not in data:
        return jsonify({"error": "Missing 'path' in request body"}), 400
    
    path = data['path']
    message = data.get('message', f'this is {path}')
    
    # Đảm bảo path bắt đầu bằng /
    if not path.startswith('/'):
        path = '/' + path
    
    # Kiểm tra xem route đã tồn tại chưa
    if path in dynamic_routes:
        return jsonify({"error": f"Route {path} already exists"}), 409
    
    # Lưu JSON object vào dictionary
    dynamic_routes[path] = {"message": message}
    
    # Save routes vào file
    save_routes()
    
    return jsonify({"message": f"Route {path} created successfully", "path": path}), 201

@app.route('/admin/routes', methods=['GET'])
@require_api_key
def list_routes():
    """Liệt kê tất cả routes đã tạo"""
    routes_list = [{"path": path, "response": response} for path, response in dynamic_routes.items()]
    return jsonify({"routes": routes_list, "count": len(routes_list)})

@app.route('/admin/routes/<path:route_path>', methods=['DELETE'])
@require_api_key
def delete_route(route_path):
    """Xóa route"""
    # Đảm bảo path bắt đầu bằng /
    if not route_path.startswith('/'):
        route_path = '/' + route_path
    
    if route_path not in dynamic_routes:
        return jsonify({"error": f"Route {route_path} not found"}), 404
    
    # Xóa khỏi dictionary
    del dynamic_routes[route_path]
    
    # Save routes vào file
    save_routes()
    
    return jsonify({"message": f"Route {route_path} deleted successfully"}), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)
