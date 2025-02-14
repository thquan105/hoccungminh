#!/bin/bash
echo "📦 Đang tạo lại migrations..."
python manage.py makemigrations --noinput

echo "🚀 Đang chạy migrate..."
python manage.py migrate --noinput

echo "🔍 Kiểm tra danh sách migrations..."
python manage.py showmigrations

echo "👤 Kiểm tra và tạo superuser nếu cần..."
python manage.py shell <<EOF
from django.contrib.auth import get_user_model
import os

username = os.getenv('DJANGO_SUPERUSER_USERNAME')
email = os.getenv('DJANGO_SUPERUSER_EMAIL')
password = os.getenv('DJANGO_SUPERUSER_PASSWORD')

User = get_user_model()
if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username=username, email=email, password=password)
    print(f"✅ Đã tạo superuser: {username}")
else:
    print(f"⚡ Superuser '{username}' đã tồn tại.")
EOF

python manage.py runserver 0.0.0.0:8000 