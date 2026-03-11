# OpenClaw Docker 镜像模板

FROM node:20-alpine

# 安装依赖
RUN apk add --no-cache \
    bash \
    curl \
    git

# 安装 OpenClaw
RUN npm install -g openclaw

# 创建工作目录
WORKDIR /workspace

# 暴露端口
EXPOSE 3000

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD curl -f http://localhost:3000/health || exit 1

# 启动命令
CMD ["openclaw", "start", "--workspace", "/workspace"]
