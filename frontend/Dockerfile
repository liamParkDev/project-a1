FROM debian:stable-slim as build

RUN apt update && apt install -y curl git unzip xz-utils zip libglu1-mesa && \
    rm -rf /var/lib/apt/lists/*

# Flutter 설치
RUN git clone https://github.com/flutter/flutter.git /flutter
ENV PATH="/flutter/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"

WORKDIR /app
COPY . .

RUN flutter config --enable-web && flutter build web

# ──────────────────────
# Nginx로 서비스
# ──────────────────────
FROM nginx:1.25

COPY --from=build /app/build/web /usr/share/nginx/html

COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
