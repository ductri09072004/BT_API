# Makefile cho Monorepo Management

.PHONY: help new-service build-all up down clean

# Default target
help:
	@echo "🚀 Monorepo Management Commands:"
	@echo ""
	@echo "📦 Service Management:"
	@echo "  make new-service name=<service_name>  - Tạo service mới từ template"
	@echo "  make build-all                        - Build tất cả services"
	@echo "  make up                              - Chạy tất cả services với docker-compose"
	@echo "  make down                            - Dừng tất cả services"
	@echo "  make clean                           - Xóa tất cả containers và images"
	@echo ""
	@echo "🔧 Individual Service:"
	@echo "  make build SERVICE=<service_name>     - Build service cụ thể"
	@echo "  make run SERVICE=<service_name>       - Chạy service cụ thể"
	@echo ""
	@echo "📋 Examples:"
	@echo "  make new-service name=payment"
	@echo "  make build SERVICE=auth"
	@echo "  make run SERVICE=user"

# Tạo service mới
new-service:
	@if [ -z "$(name)" ]; then \
		echo "❌ Vui lòng cung cấp tên service: make new-service name=<service_name>"; \
		exit 1; \
	fi
	@echo "🔨 Tạo service mới: $(name)"
	@python create_service.py $(name)
	@echo "✅ Service '$(name)' đã được tạo và cập nhật docker-compose.yml"
	@echo "🚀 Để chạy service: make run SERVICE=$(name)"
	@echo "🐳 Để build service: make build SERVICE=$(name)"

# Build tất cả services
build-all:
	@echo "🔨 Building all services..."
	@docker-compose build

# Build service cụ thể
build:
	@if [ -z "$(SERVICE)" ]; then \
		echo "❌ Vui lòng cung cấp tên service: make build SERVICE=<service_name>"; \
		exit 1; \
	fi
	@echo "🔨 Building service: $(SERVICE)"
	@docker-compose build $(SERVICE)

# Chạy tất cả services
up:
	@echo "🚀 Starting all services..."
	@docker-compose up -d

# Dừng tất cả services
down:
	@echo "🛑 Stopping all services..."
	@docker-compose down

# Chạy service cụ thể
run:
	@if [ -z "$(SERVICE)" ]; then \
		echo "❌ Vui lòng cung cấp tên service: make run SERVICE=<service_name>"; \
		exit 1; \
	fi
	@echo "🚀 Running service: $(SERVICE)"
	@docker-compose up -d $(SERVICE)

# Xóa tất cả containers và images
clean:
	@echo "🧹 Cleaning up..."
	@docker-compose down --rmi all --volumes --remove-orphans
	@docker system prune -f

# Xem logs
logs:
	@if [ -z "$(SERVICE)" ]; then \
		echo "📋 Showing logs for all services..."; \
		docker-compose logs -f; \
	else \
		echo "📋 Showing logs for $(SERVICE)..."; \
		docker-compose logs -f $(SERVICE); \
	fi

# Kiểm tra status
status:
	@echo "📊 Services Status:"
	@docker-compose ps
