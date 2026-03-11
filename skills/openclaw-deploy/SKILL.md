---
name: openclaw-deploy
description: >-
  Deploy OpenClaw instances in host mode (systemd) or container mode (Docker/K8s).
  Use when deploying OpenClaw to production, setting up systemd services, creating
  Docker containers, or deploying to Kubernetes.
---

# OpenClaw Deploy

OpenClaw 部署管理技能包，支持主机模式和容器模式部署。

## 快速开始

### 主机模式部署

```
用户: 把 openclaw-prod-01 部署为 Systemd 服务
```

AI 会生成 systemd 服务文件并配置自动启动。

### 容器模式部署

```
用户: 把 openclaw-prod-01 部署到 Docker
```

AI 会生成 Dockerfile 和 docker-compose.yml，构建并启动容器。

---

## 核心功能

### 1. 主机模式部署

使用 Systemd 管理服务：

```bash
bash scripts/deploy_host.sh <instance-id>
```

**功能**:
- 生成 systemd 服务文件
- 配置自动启动
- 配置自动重启
- 日志集成到 systemd

详见 [reference/host-mode.md](reference/host-mode.md)

### 2. Docker 部署

```bash
bash scripts/deploy_docker.sh <instance-id>
```

**功能**:
- 生成 Dockerfile
- 生成 docker-compose.yml
- 构建镜像
- 启动容器
- 健康检查

详见 [reference/container-mode.md](reference/container-mode.md)

### 3. Kubernetes 部署

详见 [reference/kubernetes.md](reference/kubernetes.md)

### 4. 健康检查

```bash
python scripts/health_check.py <instance-id>
```

检查实例运行状态、端口连通性、资源使用。

---

## 部署模板

### Systemd 服务

模板位置: `templates/systemd/openclaw@.service`

### Docker

模板位置:
- `templates/Dockerfile`
- `templates/docker-compose.yml`

### Kubernetes

模板位置: `templates/kubernetes/`

---

## 使用示例

```
用户: 部署 openclaw-prod-01 到 Docker，映射端口到 8080

AI 会:
1. 生成 Dockerfile 和 docker-compose.yml
2. 配置端口映射 3000:8080
3. 构建镜像
4. 启动容器
5. 配置健康检查
```

---

## 相关文档

- [主机部署](reference/host-mode.md)
- [容器部署](reference/container-mode.md)
- [Kubernetes部署](reference/kubernetes.md)
