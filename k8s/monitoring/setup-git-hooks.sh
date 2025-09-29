#!/bin/bash
"""
Script để setup git hooks tự động cập nhật dashboard
Usage: ./setup-git-hooks.sh
"""

echo "=== Setup Git Hooks for Dashboard Auto Update ==="

# Kiểm tra có phải git repository không
if [ ! -d ".git" ]; then
    echo "❌ Không phải git repository. Vui lòng chạy từ root của project."
    exit 1
fi

# Tạo pre-commit hook
echo "📝 Tạo pre-commit hook..."
cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash
# Pre-commit hook để tự động cập nhật dashboard

# Kiểm tra có thay đổi docker-compose.yml không
if git diff --cached --name-only | grep -q "docker-compose.yml"; then
    echo "🔍 Phát hiện thay đổi docker-compose.yml"
    
    # Chạy script cập nhật dashboard
    if [ -f "k8s/monitoring/update-dashboard.py" ]; then
        echo "📊 Đang cập nhật và import Grafana dashboard..."
        cd k8s/monitoring
        python3 update-dashboard.py
        cd ../..
        
        if [ $? -eq 0 ]; then
            echo "✅ Dashboard đã được cập nhật và import vào Grafana"
            # Thêm dashboard file vào commit
            git add k8s/monitoring/service-details-dashboard.json
        else
            echo "❌ Lỗi cập nhật dashboard"
            exit 1
        fi
    else
        echo "⚠️  Không tìm thấy script cập nhật dashboard"
    fi
fi
EOF

# Tạo quyền thực thi cho hook
chmod +x .git/hooks/pre-commit

echo "✅ Đã setup git hooks thành công!"
echo ""
echo "📋 Hooks đã được tạo:"
echo "   - pre-commit: Tự động cập nhật dashboard khi commit thay đổi docker-compose.yml"
echo ""
echo "💡 Để test:"
echo "   1. Thay đổi docker-compose.yml (thêm/xóa service)"
echo "   2. git add docker-compose.yml"
echo "   3. git commit -m 'Update services'"
echo "   4. Dashboard sẽ được cập nhật tự động"
echo ""
echo "🔧 Để tắt hooks:"
echo "   chmod -x .git/hooks/pre-commit"
