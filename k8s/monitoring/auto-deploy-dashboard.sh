#!/bin/bash
"""
Script để tự động deploy dashboard sau khi thay đổi services
Usage: ./auto-deploy-dashboard.sh
"""

echo "=== Auto Deploy Grafana Dashboard ==="
echo "Đang cập nhật dashboard dựa trên services hiện có..."

# Chuyển đến thư mục monitoring
cd "$(dirname "$0")"

# Chạy script Python
python3 update-dashboard.py

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Dashboard đã được cập nhật và import vào Grafana thành công!"
    echo "📊 Truy cập: http://localhost:3000"
    echo "🎯 Dashboard: BT_API Service Details"
    echo ""
    echo "💡 Workflow tự động:"
    echo "   1. Thêm/xóa service trong docker-compose.yml"
    echo "   2. Chạy: python update_dashboard.py"
    echo "   3. Dashboard được cập nhật và import tự động"
else
    echo ""
    echo "❌ Cập nhật dashboard thất bại!"
    exit 1
fi
