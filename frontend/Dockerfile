# 1) Build stage
FROM ghcr.io/cirruslabs/flutter:3.24.0 AS builder
WORKDIR /app
COPY . .
RUN flutter build web --release

# 2) Nginx serving stage
FROM nginx:1.25
COPY --from=builder /app/build/web /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
