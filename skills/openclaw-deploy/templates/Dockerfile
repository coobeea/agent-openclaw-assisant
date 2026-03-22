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

# 安装必要的系统工具、Python 环境和 Nginx
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
    nginx \
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

# 复制 OpenClaw 源码到全局 node_modules
COPY openclaw-source /usr/local/lib/node_modules/openclaw/

# 安装依赖
RUN cd /usr/local/lib/node_modules/openclaw && \
    npm install --registry=https://registry.npmmirror.com

# 创建全局命令链接
RUN ln -s /usr/local/lib/node_modules/openclaw/openclaw.mjs /usr/local/bin/openclaw && \
    chmod +x /usr/local/lib/node_modules/openclaw/openclaw.mjs

# 创建工作目录
WORKDIR /workspace

# 复制 Nginx 配置和启动脚本
COPY nginx.conf /etc/nginx/nginx.conf
COPY start-with-nginx.sh /usr/local/bin/start-with-nginx.sh
RUN chmod +x /usr/local/bin/start-with-nginx.sh

# 暴露端口
# - 3000: OpenClaw 内部端口（loopback）
# - 18900: Nginx 代理端口（对外暴露）
EXPOSE 18900

# 健康检查（通过 Nginx 代理访问）
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD curl -f http://localhost:18900/ || exit 1

# 启动命令（使用启动脚本）
CMD ["/usr/local/bin/start-with-nginx.sh"]
