#!/bin/bash
"""
Script để tự động cập nhật dashboard khi có thay đổi services
Usage: ./auto-update-dashboard.sh
"""

echo "=== Grafana Dashboard Auto Updater ==="
echo "Đang kiểm tra thay đổi services..."

# Chuyển đến thư mục monitoring
cd "$(dirname "$0")"

# Chạy script Python
python3 update-dashboard.py

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Dashboard đã được cập nhật thành công!"
    echo "📊 Bạn có thể import dashboard mới vào Grafana"
    echo ""
    echo "💡 Để tự động cập nhật khi có thay đổi docker-compose.yml:"
    echo "   - Thêm script này vào git hooks"
    echo "   - Hoặc chạy thủ công sau khi thêm/xóa services"
else
    echo ""
    echo "❌ Cập nhật dashboard thất bại!"
    exit 1
fi
