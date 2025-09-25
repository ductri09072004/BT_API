#!/usr/bin/env python3
"""
Script để tự động cập nhật docker-compose.yml khi tạo service mới
Usage: python update_docker_compose.py <service_name> <port>
"""

import sys
import re

def update_docker_compose(service_name, port):
    """Cập nhật docker-compose.yml với service mới"""
    
    docker_compose_file = "docker-compose.yml"
    
    try:
        # Đọc file docker-compose.yml
        with open(docker_compose_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Tìm vị trí để thêm service mới (trước template service)
        template_pattern = r'(\s+)(# Template service.*?\n)'
        match = re.search(template_pattern, content, re.DOTALL)
        
        if not match:
            print("[ERROR] Khong tim thay template service trong docker-compose.yml")
            return False
        
        # Tạo service config mới
        service_title = service_name.replace('-', ' ').replace('_', ' ').title()
        new_service = f'''  # {service_title} service
  {service_name}:
    build: ./services/{service_name}
    ports:
      - "{port}:8000"
    environment:
      - DEBUG=true
    restart: unless-stopped

'''
        
        # Thêm service mới trước template service
        new_content = content[:match.start()] + new_service + content[match.start():]
        
        # Ghi lại file
        with open(docker_compose_file, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f"[SUCCESS] Da them service '{service_name}' vao docker-compose.yml")
        print(f"[INFO] Service: {service_name}")
        print(f"[INFO] Port: {port}")
        print(f"[INFO] Build: ./services/{service_name}")
        
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
