# Flask API Bài Tập

Đây là một API đơn giản được xây dựng bằng Flask với các endpoint cơ bản.

## Cài đặt

1. Cài đặt Python dependencies:
```bash
pip install -r requirements.txt
```

## Chạy ứng dụng

```bash
python app.py
```

API sẽ chạy tại: http://localhost:5000

## API Endpoints

### 1. Health Check
- **URL:** `GET /healthz`
- **Mô tả:** Kiểm tra trạng thái của API
- **Response:** 
```json
{
  "status": "ok"
}
```

### 2. Hello World
- **URL:** `GET /A`
- **Mô tả:** Trả về message hello world
- **Response:**
```json
{
  "message": "hello world"
}
```

## Admin API Endpoints

**Lưu ý:** Tất cả Admin API endpoints yêu cầu header `X-API-Key: admin-secret-key-123`

### 3. Tạo Route Mới
- **URL:** `POST /admin/routes`
- **Headers:** `X-API-Key: admin-secret-key-123`
- **Mô tả:** Tạo một route mới với JSON response tĩnh
- **Request Body:**
```json
{
  "path": "/B",
  "message": "this is B"
}
```
- **Response:**
```json
{
  "message": "Route /B created successfully",
  "path": "/B"
}
```

### 4. Liệt Kê Routes
- **URL:** `GET /admin/routes`
- **Headers:** `X-API-Key: admin-secret-key-123`
- **Mô tả:** Liệt kê tất cả routes đã tạo
- **Response:**
```json
{
  "routes": [
    {
      "path": "/B",
      "message": "this is B"
    },
    {
      "path": "/C", 
      "message": "this is C"
    }
  ],
  "count": 2
}
```

### 5. Xóa Route
- **URL:** `DELETE /admin/routes/{path}`
- **Headers:** `X-API-Key: admin-secret-key-123`
- **Mô tả:** Xóa một route đã tạo
- **Response:**
```json
{
  "message": "Route /B deleted successfully"
}
```

## Test API

Bạn có thể test API bằng các cách sau:

### Sử dụng curl:
```bash
# Test health check
curl http://localhost:5000/healthz

# Test hello world
curl http://localhost:5000/A
```

### Sử dụng trình duyệt:
- Mở http://localhost:5000/healthz
- Mở http://localhost:5000/A

### Sử dụng Postman:
- Import các endpoint vào Postman
- Gửi GET request đến các URL trên
