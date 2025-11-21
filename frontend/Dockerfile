# ---- Flutter Build Stage ----
FROM debian:stable-slim AS build

RUN apt update && apt install -y curl git unzip xz-utils zip libglu1-mesa \
    && rm -rf /var/lib/apt/lists/*

RUN git clone https://github.com/flutter/flutter.git /flutter

ENV PATH="/flutter/bin:/flutter/bin/cache/dart-sdk/bin:${PATH}"

WORKDIR /app
COPY . .

RUN flutter config --enable-web
RUN flutter build web

# ---- Nginx Serve Stage ----
FROM nginx:1.25

COPY nginx.conf /etc/nginx/nginx.conf
COPY --from=build /app/build/web /usr/share/nginx/html
