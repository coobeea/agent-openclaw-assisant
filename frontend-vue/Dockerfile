FROM node:18-alpine AS builder

WORKDIR /app

# 复制 package.json
COPY package.json ./

# 显式禁用所有代理，使用国内镜像源安装依赖
RUN unset HTTP_PROXY HTTPS_PROXY http_proxy https_proxy && \
    npm config delete proxy 2>/dev/null || true && \
    npm config delete https-proxy 2>/dev/null || true && \
    npm config set registry https://registry.npmmirror.com && \
    npm install --registry=https://registry.npmmirror.com --no-proxy

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
