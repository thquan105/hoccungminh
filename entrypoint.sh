#!/bin/bash

# Chạy migrations để cập nhật database
python manage.py migrate

# Kiểm tra nếu superuser đã tồn tại, nếu chưa thì tạo mới
python manage.py shell <<EOF
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
import os

# Lấy thông tin superuser từ biến môi trường
username = os.getenv('DJANGO_SUPERUSER_USERNAME')
email = os.getenv('DJANGO_SUPERUSER_EMAIL')
password = os.getenv('DJANGO_SUPERUSER_PASSWORD')

# Kiểm tra nếu superuser đã tồn tại, nếu không tạo mới
User = get_user_model()
try:
    user = User.objects.get(username=username)
    print(f"Superuser '{username}' đã tồn tại.")
except ObjectDoesNotExist:
    user = User.objects.create_superuser(username=username, email=email, password=password)
    print(f"Đã tạo superuser: {username}")

EOF

# Khởi động server Django
exec python manage.py runserver 0.0.0.0:${PORT}
