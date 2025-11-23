# ---- Nginx Serve Stage ----
FROM nginx:1.25

# Nginx 설정 복사
COPY nginx.conf /etc/nginx/nginx.conf

# Flutter 웹 빌드 결과물을 복사
COPY build/web/ /usr/share/nginx/html/
