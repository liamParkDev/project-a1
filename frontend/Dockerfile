# -------------------------------
# Nginx Stage (serve built files)
# -------------------------------
FROM nginx:1.25

# Nginx 설정 복사
COPY nginx.conf /etc/nginx/nginx.conf

# GitHub Actions에서 이미 flutter build web 수행됨
COPY build/web/ /usr/share/nginx/html/

# 권한 설정(optional)
RUN chmod -R 755 /usr/share/nginx/html
