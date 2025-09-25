# 🚀 Monorepo Microservices

Dự án này sử dụng cấu trúc **Monorepo** để quản lý nhiều microservices trong một repository duy nhất.

## 📂 Cấu trúc dự án

```
BT_API/
├── services/                    # 📁 Thư mục chứa tất cả microservices
│   ├── template/               # 📌 KHUÔN MẪU SẴN
│   │   ├── main.py             # Entry point
│   │   ├── routes.py            # API routes
│   │   ├── requirements.txt     # Dependencies
│   │   └── Dockerfile           # Docker config
│   │
│   └── api/                     # Service API (chuyển đổi từ Flask)
│       ├── main.py
│       ├── routes.py
│       ├── requirements.txt
│       └── Dockerfile
│
├── data/                        # 📁 Dữ liệu chung
│   └── routes.json              # Dynamic routes data
│
├── create_service.py            # 🔧 Script tạo service mới
├── Makefile                     # 🛠️ Commands quản lý
├── docker-compose.yml           # 🐳 Docker orchestration
└── README_MONOREPO.md           # 📖 Documentation
```

## 🚀 Cách sử dụng

### 1. Tạo service mới

```bash
# Tạo service mới từ template
python create_service.py <service_name>

# Ví dụ:
python create_service.py payment
python create_service.py auth
python create_service.py user-management
```

### 2. Quản lý services với Makefile

```bash
# Xem tất cả commands
make help

# Tạo service mới
make new-service name=payment

# Build tất cả services
make build-all

# Build service cụ thể
make build SERVICE=api

# Chạy tất cả services
make up

# Chạy service cụ thể
make run SERVICE=api

# Dừng tất cả services
make down

# Xem logs
make logs SERVICE=api

# Kiểm tra status
make status
```

### 3. Chạy với Docker Compose

```bash
# Chạy tất cả services
docker-compose up -d

# Chạy service cụ thể
docker-compose up -d api

# Xem logs
docker-compose logs -f api

# Dừng services
docker-compose down
```

## 🔧 Template Service

Mỗi service mới được tạo từ template có sẵn:

- **FastAPI** framework
- **Health check** endpoint: `/healthz`
- **Hello world** endpoint: `/A`
- **Docker** configuration
- **Environment** variables support

### Cấu trúc template:

```python
# main.py
from fastapi import FastAPI
from routes import router

app = FastAPI(title="Service Name", version="1.0.0")
app.include_router(router)

# routes.py
from fastapi import APIRouter

router = APIRouter()

@router.get("/healthz")
async def health_check():
    return {"status": "ok"}

@router.get("/A")
async def hello_world():
    return {"message": "hello world"}
```

## 🌐 Services hiện tại

### Health Service (Port 8001)
- **Health check**: `GET /healthz`
- Chỉ xử lý health check endpoint

### Hello Service (Port 8002)
- **Hello world**: `GET /A`
- **Health check**: `GET /healthz`
- Chỉ xử lý hello world endpoint

### Admin Service (Port 8003)
- **Health check**: `GET /healthz`
- **Admin APIs**:
  - `POST /admin/routes` - Tạo route mới
  - `GET /admin/routes` - Liệt kê routes
  - `DELETE /admin/routes/{path}` - Xóa route

### Dynamic Service (Port 8004)
- **Health check**: `GET /healthz`
- **Dynamic routes**: `GET /{path}`
- Xử lý các routes động được tạo bởi admin

### Template Service (Port 8000)
- **Health check**: `GET /healthz`
- **Hello world**: `GET /A`
- Khuôn mẫu để tạo services mới

## 📝 Thêm service mới

1. **Tạo service**:
   ```bash
   python create_service.py payment
   ```

2. **Cập nhật docker-compose.yml**:
   ```yaml
   payment:
     build: ./services/payment
     ports:
       - "8004:8000"
     environment:
       - DEBUG=true
     restart: unless-stopped
   ```

3. **Chạy service**:
   ```bash
   make run SERVICE=payment
   ```

## 🎯 Ưu điểm của Monorepo

- ✅ **Nhanh chóng**: Tạo service mới chỉ với 1 lệnh
- ✅ **Quản lý tập trung**: 1 repo chứa tất cả services
- ✅ **Chia sẻ code**: Dễ dàng sử dụng chung utilities
- ✅ **CI/CD đơn giản**: Build từng service từ subfolder
- ✅ **Scale linh hoạt**: Deploy riêng từng service trong k8s

## 🔄 Migration từ Flask

API service đã được chuyển đổi từ Flask sang FastAPI:

- ✅ Giữ nguyên tất cả endpoints
- ✅ Cải thiện performance với FastAPI
- ✅ Auto-generated OpenAPI documentation
- ✅ Better type hints và validation
- ✅ Async support

## 🐳 Docker

Mỗi service có Dockerfile riêng:

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 📊 Monitoring

- **Health checks**: Mỗi service có `/healthz` endpoint
- **Logs**: `docker-compose logs -f <service>`
- **Status**: `make status` hoặc `docker-compose ps`

## 🚀 Production Deployment

Để deploy production:

1. **Environment variables**: Cập nhật `.env` files
2. **Secrets management**: Sử dụng Docker secrets hoặc K8s secrets
3. **Load balancing**: Sử dụng nginx hoặc traefik
4. **Monitoring**: Thêm Prometheus/Grafana
5. **Logging**: Centralized logging với ELK stack
