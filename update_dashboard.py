#!/usr/bin/env python3
"""
Script để cập nhật Grafana dashboard từ root directory
Usage: python update_dashboard.py
"""

import os
import sys
import subprocess

def main():
    """Main function"""
    print("=== Grafana Dashboard Auto Updater ===")
    print("Script sẽ tự động cập nhật và import dashboard vào Grafana")
    print()
    
    # Kiểm tra có file script không
    script_path = "k8s/monitoring/update-dashboard.py"
    if not os.path.exists(script_path):
        print(f"[ERROR] Không tìm thấy script: {script_path}")
        return 1
    
    try:
        # Chạy script từ thư mục monitoring
        result = subprocess.run([
            sys.executable, "update-dashboard.py"
        ], cwd="k8s/monitoring", capture_output=True, text=True)
        
        print(result.stdout)
        if result.stderr:
            print(result.stderr)
        
        return result.returncode
        
    except Exception as e:
        print(f"[ERROR] Lỗi chạy script: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
