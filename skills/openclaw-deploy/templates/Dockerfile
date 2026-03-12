# OpenClaw Docker 镜像模板
# 包含 Node.js (运行 OpenClaw) 和 Python 3 (运行原生技能)

FROM node:20-alpine

# 安装必要的系统工具和 Python 环境
RUN apk add --no-cache \
    bash \
    curl \
    git \
    python3 \
    py3-pip \
    build-base \
    python3-dev \
    linux-headers

# 创建并激活 Python 虚拟环境 (推荐的最佳实践)
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# 安装一些常用的 Python 库 (供原生技能使用)
RUN pip install --no-cache-dir \
    requests \
    pyyaml \
    python-dotenv

# 安装 OpenClaw
RUN npm install -g openclaw

# 创建工作目录
WORKDIR /workspace

# 暴露端口 (会被 docker-compose 覆盖)
EXPOSE 3000

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD curl -f http://localhost:${PORT:-3000}/health || exit 1

# 启动命令
CMD ["openclaw", "start", "--workspace", "/workspace"]
