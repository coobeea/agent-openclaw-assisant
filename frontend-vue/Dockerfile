FROM node:18-alpine AS builder

WORKDIR /app

# 复制 package.json
COPY package.json ./
RUN npm install

# 复制源代码
COPY . .

# 构建
RUN npm run build

# 生产镜像
FROM nginx:alpine

# 复制构建产物
COPY --from=builder /app/dist /usr/share/nginx/html

# Nginx 配置
RUN echo 'server { \
    listen 80; \
    location / { \
        root /usr/share/nginx/html; \
        index index.html; \
        try_files $uri $uri/ /index.html; \
    } \
    location /api { \
        proxy_pass http://openclaw-scheduler:8080; \
        proxy_http_version 1.1; \
        proxy_set_header Connection ""; \
        proxy_buffering off; \
        proxy_cache off; \
        chunked_transfer_encoding off; \
        proxy_read_timeout 86400s; \
        proxy_send_timeout 86400s; \
    } \
}' > /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
