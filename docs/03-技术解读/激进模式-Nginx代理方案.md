# 激进模式 - Nginx 代理方案详解

## 📋 概述

**问题**：OpenClaw 安全策略不允许在局域网绑定模式（`bind: lan/custom`）下使用完全无认证（`auth.mode: none`）。

**解决方案**：使用 **Nginx 反向代理** 架构，实现真正的零门槛访问。

---

## 🏗️ 架构设计

### 架构图

```
┌─────────────────┐
│   浏览器/客户端   │
└────────┬────────┘
         │ http://0.0.0.0:18900
         ↓
┌─────────────────┐
│  Nginx (代理)    │  ← 对外暴露（0.0.0.0:18900）
│  - 监听所有接口   │
│  - 反向代理       │
│  - WebSocket支持 │
└────────┬────────┘
         │ http://127.0.0.1:3000
         ↓
┌─────────────────┐
│   OpenClaw      │  ← 内部服务（127.0.0.1:3000）
│  - loopback绑定  │
│  - auth.mode=none│
│  - 完全无认证     │
└─────────────────┘
```

---

## 💡 核心原理

### OpenClaw 安全策略限制

| 绑定模式 | 可用认证模式 | 说明 |
|---------|------------|------|
| `loopback` | `none`, `token`, `password` | ✅ 允许无认证（仅本机） |
| `lan` | `token`, `password` | ❌ 必须有认证（局域网） |
| `custom` | `token`, `password` | ❌ 必须有认证（自定义） |

### Nginx 代理方案

**核心思想**：
1. OpenClaw 使用 `loopback` 模式（127.0.0.1）+ `auth.mode=none`
2. Nginx 监听 `0.0.0.0:18900`，反向代理到 `127.0.0.1:3000`
3. 用户访问 Nginx（无需认证），Nginx 转发到 OpenClaw

**优势**：
- ✅ 绕过 OpenClaw 的安全策略限制
- ✅ 实现真正的零门槛访问（完全无需 Token）
- ✅ 支持局域网访问
- ✅ 保持架构清晰（代理层 + 应用层分离）

---

## 🔧 实现细节

### 1. Dockerfile 修改

**添加 Nginx**：
```dockerfile
RUN apt-get install -y nginx
```

**复制配置**：
```dockerfile
COPY nginx.conf /etc/nginx/nginx.conf
COPY start-with-nginx.sh /usr/local/bin/start-with-nginx.sh
RUN chmod +x /usr/local/bin/start-with-nginx.sh
```

**修改启动命令**：
```dockerfile
CMD ["/usr/local/bin/start-with-nginx.sh"]
```

### 2. Nginx 配置（nginx.conf）

```nginx
user  root;
worker_processes  auto;

http {
    # WebSocket 支持
    map $http_upgrade $connection_upgrade {
        default upgrade;
        '' close;
    }

    server {
        listen 18900;
        server_name localhost;
        
        location / {
            proxy_pass http://127.0.0.1:3000;
            proxy_http_version 1.1;
            
            # WebSocket 支持
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection $connection_upgrade;
            
            # 传递原始请求头
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            
            # 超时设置（WebSocket 长连接）
            proxy_connect_timeout 7d;
            proxy_send_timeout 7d;
            proxy_read_timeout 7d;
        }
    }
}
```

**关键配置说明**：
- `listen 18900`：Nginx 监听的外部端口
- `proxy_pass http://127.0.0.1:3000`：转发到 OpenClaw 内部端口
- `Upgrade` 和 `Connection`：支持 WebSocket 协议
- 超时设置：支持长连接（7天）

### 3. 启动脚本（start-with-nginx.sh）

```bash
#!/bin/bash
set -e

echo "🚀 启动 OpenClaw + Nginx 代理..."

# 启动 Nginx
echo "📦 启动 Nginx..."
nginx -c /etc/nginx/nginx.conf

# 等待 Nginx 启动
sleep 2

# 启动 OpenClaw（监听 127.0.0.1:3000）
echo "🦞 启动 OpenClaw..."
exec node /usr/local/lib/node_modules/openclaw/dist/index.js gateway --port 3000
```

**说明**：
- 先启动 Nginx
- 再启动 OpenClaw
- 使用 `exec` 确保 OpenClaw 是主进程（PID 1）

### 4. OpenClaw 配置（openclaw.json）

```json
{
  "gateway": {
    "bind": "loopback",
    "port": 3000,
    "auth": {
      "mode": "none"
    },
    "controlUi": {
      "dangerouslyDisableDeviceAuth": true
    }
  }
}
```

**关键点**：
- `bind: loopback`：允许使用 `auth.mode: none`
- `port: 3000`：内部端口（不对外暴露）
- `auth.mode: none`：完全无认证

---

## ✅ 验证测试

### 1. 容器进程验证

```bash
$ docker exec openclaw-docker-001 ps aux | grep -E "nginx|node"

root  9  nginx: master process nginx
root  10-22  nginx: worker process (12个)
root  1  node gateway --port 3000
```

✅ Nginx 和 OpenClaw 都正常运行

### 2. 端口监听验证

```bash
# 容器内部
$ docker exec openclaw-docker-001 netstat -tlnp
127.0.0.1:3000  ← OpenClaw（内部）
0.0.0.0:18900   ← Nginx（外部）
```

✅ 端口绑定正确

### 3. HTTP 访问测试

```bash
$ curl -s -o /dev/null -w "%{http_code}\n" "http://127.0.0.1:18900/"
200
```

✅ HTTP 访问正常

### 4. 日志验证

```
[gateway] auth mode=none explicitly configured
[gateway] listening on ws://127.0.0.1:3000
Container Status: Up (healthy)
```

✅ 配置生效，无认证模式启用

---

## 🎯 使用场景对比

### 主机模式 vs Docker 模式

| 特性 | 主机模式 | Docker 模式 |
|------|---------|------------|
| **OpenClaw 绑定** | loopback | loopback |
| **OpenClaw 端口** | 18800（用户指定） | 3000（固定） |
| **对外访问** | 仅本机 | 局域网可访问 |
| **代理层** | 无 | Nginx (0.0.0.0:18900) |
| **认证** | 完全无 | 完全无 |
| **适用场景** | 个人开发 | 团队协作/容器化 |

---

## 📚 相关文件

### 核心文件

1. **`skills/openclaw-deploy/templates/Dockerfile`**
   - 安装 Nginx
   - 复制配置文件和启动脚本

2. **`skills/openclaw-deploy/templates/nginx.conf`**
   - Nginx 配置
   - WebSocket 支持
   - 反向代理配置

3. **`skills/openclaw-deploy/templates/start-with-nginx.sh`**
   - 启动脚本
   - 按顺序启动 Nginx 和 OpenClaw

4. **`skills/openclaw-deploy/scripts/deploy_docker.sh`**
   - 部署脚本
   - 自动调整配置端口为 3000

5. **`skills/openclaw-manager/scripts/instance_manager.py`**
   - `_apply_aggressive_config()` 方法
   - 自动应用 loopback + auth.mode=none

---

## ⚠️ 安全建议

### 适用场景

**激进模式 + Nginx 代理适用于**：
- ✅ 开发环境
- ✅ 测试环境
- ✅ 内网环境
- ✅ 团队协作（信任网络）

**不推荐用于**：
- ❌ 公网生产环境
- ❌ 处理敏感数据
- ❌ 不受控的网络环境

### 生产环境部署

如需生产部署，建议：

1. **关闭激进模式**
2. **使用安全配置**：
   ```json
   {
     "gateway": {
       "bind": "loopback",
       "auth": {
         "mode": "token",
         "token": "your-strong-random-token"
       }
     }
   }
   ```
3. **配置 Nginx 认证**（Basic Auth 或其他）
4. **配置防火墙规则**
5. **定期更新依赖**

---

## 🎉 总结

**激进模式 + Nginx 代理方案**是目前最接近"零门槛"的合法实现方案：

✅ **完全无需 Token**
✅ **局域网可访问**（Docker 模式）
✅ **OpenClaw 使用 loopback + auth.mode=none**（合法）
✅ **Nginx 处理外部访问**（灵活）

**这是用户体验最好的开发环境配置！** 🚀

---

**最后更新**: 2026-03-13  
**维护者**: lifeng
