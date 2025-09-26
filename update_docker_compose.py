#!/usr/bin/env python3
"""
Script để tự động thêm service vào docker-compose.yml
Usage: python update_docker_compose.py <service_name> <port>
"""

import os
import sys
import re

def update_docker_compose(service_name, port):
    """Thêm service vào docker-compose.yml"""
    
    docker_compose_file = "docker-compose.yml"
    if not os.path.exists(docker_compose_file):
        print("[ERROR] Khong tim thay docker-compose.yml")
        return False
    
    try:
        with open(docker_compose_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Kiểm tra service đã tồn tại chưa
        if f"  {service_name}:" in content:
            print(f"[WARNING] Service '{service_name}' da ton tai trong docker-compose.yml")
            return True
        
        # Tạo service config
        service_config = f"""
  {service_name}:
    build: ./services/{service_name}
    ports:
      - "{port}:8000"
    environment:
      - DEBUG=true
      - MONGODB_URI=mongodb+srv://BlueDuck2:Fcsunny0907@tpexpress.zjf26.mongodb.net/?retryWrites=true&w=majority&appName=TPExpress
      - MONGODB_DB=test
    restart: unless-stopped
"""
        
        # Tìm vị trí để thêm service (trước dòng cuối)
        lines = content.split('\n')
        
        # Tìm dòng cuối cùng không phải comment hoặc empty
        last_line_idx = len(lines) - 1
        while last_line_idx >= 0 and (lines[last_line_idx].strip() == '' or lines[last_line_idx].strip().startswith('#')):
            last_line_idx -= 1
        
        # Thêm service config
        lines.insert(last_line_idx + 1, service_config)
        
        # Ghi lại file
        with open(docker_compose_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
        
        print(f"[SUCCESS] Da them service '{service_name}' vao docker-compose.yml voi port {port}")
        print(f"[INFO] MongoDB environment variables da duoc them tu dong")
        return True
        
    except Exception as e:
        print(f"[ERROR] Loi khi cap nhat docker-compose.yml: {e}")
        return False

def main():
    if len(sys.argv) != 3:
        print("Usage: python update_docker_compose.py <service_name> <port>")
        print("Example: python update_docker_compose.py payment 8005")
        sys.exit(1)
    
    service_name = sys.argv[1]
    port = sys.argv[2]
    
    success = update_docker_compose(service_name, port)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()