#!/usr/bin/env python3
"""
Script để tạo service mới từ template
Usage: python create_service.py <service_name>
"""

import os
import sys
import shutil
import re
import subprocess

def create_service(service_name):
    """Tạo service mới từ template"""
    
    # Validate service name
    if not service_name or not service_name.replace('-', '').replace('_', '').isalnum():
        print("[ERROR] Service name chi duoc chua chu cai, so, dau gach ngang va gach duoi")
        return False
    
    template_dir = "services/template"
    service_dir = f"services/{service_name}"
    
    # Kiểm tra service đã tồn tại chưa
    if os.path.exists(service_dir):
        print(f"[ERROR] Service '{service_name}' da ton tai!")
        return False
    
    try:
        # Copy template
        shutil.copytree(template_dir, service_dir)
        print(f"✅ Đã copy template → {service_dir}")
        
        # Đảm bảo file db.py được copy (nếu có trong template)
        template_db = os.path.join(template_dir, "db.py")
        service_db = os.path.join(service_dir, "db.py")
        if os.path.exists(template_db) and not os.path.exists(service_db):
            shutil.copy2(template_db, service_db)
            print(f"✅ Đã copy file db.py")
        
        # Cập nhật tên service trong main.py
        main_file = os.path.join(service_dir, "main.py")
        with open(main_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Thay thế title="Template" bằng tên service mới
        service_title = service_name.replace('-', ' ').replace('_', ' ').title()
        content = content.replace('title="Template"', f'title="{service_title}"')
        
        with open(main_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ Đã cập nhật tên service: {service_title}")
        
        # Tạo file .env.example
        env_file = os.path.join(service_dir, ".env.example")
        with open(env_file, 'w', encoding='utf-8') as f:
            f.write(f"# {service_title} Environment Variables\n")
            f.write("PORT=8000\n")
            f.write("DEBUG=true\n")
            f.write("MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority&appName=AppName\n")
            f.write("MONGODB_DB=TPExpress\n")
        
        print(f"✅ Đã tạo file .env.example")
        
        print(f"\n[SUCCESS] Service '{service_name}' da duoc tao thanh cong!")
        print(f"[INFO] Thu muc: {service_dir}")
        print(f"[INFO] De chay service: cd {service_dir} && python main.py")
        print(f"[INFO] De build Docker: cd {service_dir} && docker build -t {service_name} .")
        
        # Tự động cập nhật docker-compose.yml
        print(f"\n[INFO] Dang cap nhat docker-compose.yml...")
        try:
            # Tìm port trống (bắt đầu từ 8005)
            docker_compose_file = "docker-compose.yml"
            if os.path.exists(docker_compose_file):
                with open(docker_compose_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Tìm port cao nhất
                ports = re.findall(r'"(\d+):8000"', content)
                if ports:
                    next_port = max(int(p) for p in ports) + 1
                else:
                    next_port = 8005
                
                # Cập nhật docker-compose.yml
                result = subprocess.run([
                    sys.executable, "update_docker_compose.py", service_name, str(next_port)
                ], capture_output=True, text=True)
                
                if result.returncode == 0:
                    print(f"[SUCCESS] Da tu dong cap nhat docker-compose.yml voi port {next_port}")
                else:
                    print(f"[WARNING] Khong the tu dong cap nhat docker-compose.yml: {result.stderr}")
                    print(f"[INFO] Hay them service '{service_name}' vao docker-compose.yml thu cong")
            else:
                print(f"[WARNING] Khong tim thay docker-compose.yml")
        except Exception as e:
            print(f"[WARNING] Loi khi cap nhat docker-compose.yml: {e}")
            print(f"[INFO] Hay them service '{service_name}' vao docker-compose.yml thu cong")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Loi khi tao service: {e}")
        return False

def main():
    if len(sys.argv) != 2:
        print("Usage: python create_service.py <service_name>")
        print("Example: python create_service.py payment")
        sys.exit(1)
    
    service_name = sys.argv[1]
    success = create_service(service_name)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
