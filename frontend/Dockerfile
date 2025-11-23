# -------------------------------
# Nginx Stage (serve built files)
# -------------------------------
FROM nginx:1.25

COPY nginx.conf /etc/nginx/nginx.conf

COPY build/web/ /usr/share/nginx/html/

RUN chmod -R 755 /usr/share/nginx/html
