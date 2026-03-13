# OpenClaw Docker 镜像模板
# 包含 Node.js (运行 OpenClaw) 和 Python 3 (运行原生技能)

# 使用 docker pull 官方镜像，如果网络不通，请在宿主机配置 Docker 代理
FROM node:22-bullseye

# 接收代理参数
ARG HTTP_PROXY
ARG HTTPS_PROXY
ARG NO_PROXY

# 设置环境变量供构建过程使用
ENV HTTP_PROXY=$HTTP_PROXY
ENV HTTPS_PROXY=$HTTPS_PROXY
ENV NO_PROXY=$NO_PROXY

# 安装必要的系统工具和 Python 环境
# 使用阿里云镜像源加速 apt
RUN sed -i 's/deb.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list && \
    apt-get update && \
    apt-get install -y \
    bash \
    curl \
    git \
    python3 \
    python3-pip \
    python3-venv \
    build-essential \
    python3-dev \
    cmake \
    && rm -rf /var/lib/apt/lists/*

# 设置环境变量跳过 node-llama-cpp 的编译
ENV NODE_LLAMA_CPP_SKIP_DOWNLOAD=true
ENV NODE_LLAMA_CPP_SKIP_BUILD=true

# 创建并激活 Python 虚拟环境 (推荐的最佳实践)
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# 安装一些常用的 Python 库 (供原生技能使用)
# 使用清华大学镜像源加速 pip
RUN pip install --no-cache-dir -i https://pypi.tuna.tsinghua.edu.cn/simple \
    requests \
    pyyaml \
    python-dotenv

# 安装 OpenClaw
# 使用淘宝镜像源加速 npm
RUN npm install -g @openclaw/cli --registry=https://registry.npmmirror.com || npm install -g openclaw --registry=https://registry.npmmirror.com

# 创建工作目录
WORKDIR /workspace

# 暴露端口 (会被 docker-compose 覆盖)
EXPOSE 3000

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD curl -f http://localhost:${PORT:-3000}/health || exit 1

# 启动命令
CMD ["sh", "-c", "node /usr/local/lib/node_modules/openclaw/dist/index.js gateway --port ${PORT:-3000}"]
