# OpenClaw 快速启动指南

## 🚀 当前状态

✅ **服务已运行！** 所有 9 个 Pod 正常运行
- 📍 API 地址：http://localhost:30080
- 🧪 健康检查：http://localhost:30080/health
- 📊 系统状态：http://localhost:30080/api/status

---

## 📜 管理脚本

### 1️⃣ 查看状态（推荐）
```bash
./status.sh
```
显示：
- K8s 集群状态
- Pod 运行状态
- 服务地址
- 健康检查结果
- 容器池状态
- 数据目录统计

### 2️⃣ 启动服务
```bash
./start-services.sh
```
按顺序启动：
1. PostgreSQL, Redis, MinIO（基础设施）
2. OpenClaw 容器池（5 个 Pod）
3. Go 调度服务

### 3️⃣ 停止服务
```bash
./stop-services.sh
```
停止所有服务，但保留数据

### 4️⃣ 重启服务
```bash
./restart-services.sh
```
完整的停止 + 启动流程

### 5️⃣ 完整测试
```bash
./test-api.sh
```
自动执行：
- 用户注册/登录
- 创建智能体
- 发送对话
- 验证容器分配

---

## 🌐 API 端点

### 用户管理
```bash
# 注册
curl -X POST http://localhost:30080/api/users/register \
  -H "Content-Type: application/json" \
  -d '{"username": "demo", "password": "123456"}'

# 登录
curl -X POST http://localhost:30080/api/users/login \
  -H "Content-Type: application/json" \
  -d '{"username": "demo", "password": "123456"}'
```

### 智能体管理
```bash
# 创建智能体
curl -X POST http://localhost:30080/api/agents/create \
  -H "Content-Type: application/json" \
  -d '{"user_id": 1, "name": "助手", "description": "我的智能助手"}'

# 查看列表
curl http://localhost:30080/api/agents/list?user_id=1
```

### 对话管理
```bash
# 发送消息
curl -X POST http://localhost:30080/api/chat \
  -H "Content-Type: application/json" \
  -d '{"agent_id": "agent-1-xxxx", "message": "你好"}'

# 查看历史
curl http://localhost:30080/api/chat/history?agent_id=agent-1-xxxx
```

### 容器管理
```bash
# 容器池状态
curl http://localhost:30080/api/containers/status

# 系统状态
curl http://localhost:30080/api/status
```

---

## 🖥️ 前端界面

### 启动 Vue3 前端（可选）

```bash
cd frontend-vue
npm install      # 首次需要
npm run dev      # 启动开发服务器
```

访问：http://localhost:3001

---

## 📂 项目结构

```
.
├── start-services.sh       # ⭐ 启动所有服务
├── stop-services.sh        # 🛑 停止所有服务
├── restart-services.sh     # 🔄 重启服务
├── status.sh               # 📊 查看状态（推荐）
├── test-api.sh            # 🧪 完整测试
│
├── k8s-manifests/         # K8s 配置文件
│   ├── 01-postgres.yaml
│   ├── 02-redis.yaml
│   ├── 03-minio.yaml
│   ├── 04-openclaw-pool.yaml    # OpenClaw 容器池
│   └── 05-scheduler-service.yaml # Go 调度服务
│
├── scheduler-go/          # Go 后端源码
├── frontend-vue/          # Vue3 前端源码
├── workspace/lobsters/    # 数据持久化目录
│   ├── agents/           # 智能体工作空间
│   ├── database/         # PostgreSQL 数据
│   ├── cache/            # Redis 数据
│   └── storage/          # MinIO 数据
│
└── docs/05-集群控制/      # 完整文档
    └── 8.完成总结.md      # ⭐ 最终总结
```

---

## 🔧 常用命令

### K8s 管理
```bash
# 查看所有资源
kubectl get all -n openclaw

# 查看日志
kubectl logs -n openclaw -l app=openclaw-scheduler --tail=50
kubectl logs -n openclaw -l app=openclaw-pool --tail=50

# 进入容器
kubectl exec -it -n openclaw <pod-name> -- /bin/sh
```

### 数据管理
```bash
# 查看智能体
ls -la workspace/lobsters/agents/

# 查看数据库大小
du -sh workspace/lobsters/database/

# 备份数据
tar -czf backup-$(date +%Y%m%d).tar.gz workspace/lobsters/
```

---

## 🐛 故障排查

### 服务无法访问
```bash
# 1. 检查 K8s 集群
kubectl cluster-info

# 2. 检查 Pod 状态
kubectl get pods -n openclaw

# 3. 查看日志
kubectl logs -n openclaw -l app=openclaw-scheduler --tail=100

# 4. 重启服务
./restart-services.sh
```

### 容器池问题
```bash
# 查看 OpenClaw 日志
kubectl logs -n openclaw -l app=openclaw-pool --tail=100

# 检查容器池状态
curl http://localhost:30080/api/containers/status | jq .
```

### 数据库问题
```bash
# 进入 PostgreSQL
kubectl exec -it -n openclaw postgres-xxx -- psql -U postgres -d openclaw

# 查看表
\dt

# 查看用户
SELECT * FROM users;

# 查看智能体
SELECT * FROM agents;
```

---

## 📚 文档索引

- **快速开始**：本文档
- **完整总结**：`docs/05-集群控制/8.完成总结.md`
- **实施指南**：`docs/05-集群控制/3.方案A-单节点快速验证.md`
- **项目结构**：`PROJECT_STRUCTURE.md`
- **API 文档**：本文档 API 端点部分

---

## 🎯 下一步

1. ✅ **服务已运行**：直接使用 API
2. 🧪 **运行测试**：`./test-api.sh`
3. 🖥️ **启动前端**：`cd frontend-vue && npm run dev`
4. 📖 **阅读文档**：`docs/05-集群控制/8.完成总结.md`

---

**当前版本：v1.0**  
**最后更新：2026-04-10**  
**状态：✅ 生产就绪**
