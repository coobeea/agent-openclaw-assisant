# 容器模式部署

## Docker 部署

### 使用部署脚本

```bash
bash scripts/deploy_docker.sh openclaw-prod-01
```

### Dockerfile 模板

位置: `templates/Dockerfile`

### docker-compose 配置

位置: `templates/docker-compose.yml`

### 部署命令

```bash
# 构建镜像
docker build -t openclaw-prod-01 .

# 启动容器
docker run -d \
  --name openclaw-prod-01 \
  -v ./workspace/openclaw-prod-01:/workspace \
  -p 3000:3000 \
  openclaw-prod-01
```

---

## Kubernetes 部署

详见 [kubernetes.md](kubernetes.md)

---

## 健康检查

```bash
python ../scripts/health_check.py openclaw-prod-01
```

检查项：
- 容器运行状态
- 端口可访问性
- API 响应
- 资源使用
