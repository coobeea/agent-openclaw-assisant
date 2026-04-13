# 🎉 可配置内核 - 快速开始

> **一键部署、一键测试，立即体验双内核灵活切换！**

---

## 🚀 快速开始（3步）

### 1️⃣  一键部署

```bash
./deploy-configurable-kernel.sh
```

这个脚本会自动：
- ✅ 编译 Go 代码
- ✅ 构建 Docker 镜像
- ✅ 部署到 K8s 集群
- ✅ 等待 Pod 就绪
- ✅ 显示访问信息

**预计时间**：3-5 分钟

---

### 2️⃣  一键测试

```bash
./test-configurable-kernel.sh
```

这个脚本会自动测试：
- ✅ 健康检查
- ✅ 系统状态
- ✅ V1 API（原版）
- ✅ V2 API - OpenClaw 内核
- ✅ V2 API - QwenPaw 内核
- ✅ 内核动态切换
- ✅ K8s Pod 状态

**预计时间**：1-2 分钟

---

### 3️⃣  手动测试（可选）

```bash
# 使用 OpenClaw 内核
curl -X POST http://localhost:30080/api/chat/stream/v2 \
  -H "Content-Type: application/json" \
  -H "X-Kernel-Type: openclaw" \
  -d '{"agent_id":"test","message":"Hello, OpenClaw!"}'

# 使用 QwenPaw 内核（如已部署）
curl -X POST http://localhost:30080/api/chat/stream/v2 \
  -H "Content-Type: application/json" \
  -H "X-Kernel-Type: qwenpaw" \
  -d '{"agent_id":"test","message":"Hello, QwenPaw!"}'
```

---

## 📚 详细文档

- **[使用指南](docs/25-可配置内核使用指南.md)** - 完整使用文档 ⭐
- **[完成报告](docs/26-可配置内核实施完成报告.md)** - 实施总结
- **[架构方案](docs/22-可配置内核架构方案-OpenClaw与QwenPaw.md)** - 技术细节

---

## 🔧 核心文件

### 脚本
- `deploy-configurable-kernel.sh` - 一键部署脚本
- `test-configurable-kernel.sh` - 一键测试脚本

### 配置
- `k8s-manifests/05-scheduler-configurable-kernel.yaml` - K8s 部署配置
- `scheduler-go/Dockerfile` - Docker 镜像构建

### 代码
- `scheduler-go/internal/kernel/` - 内核抽象层（1,318行）
- `scheduler-go/internal/api/chatstream_v2.go` - V2 API（260行）

---

## 💡 常见问题

### Q1: 部署失败怎么办？

**A**: 检查日志
```bash
kubectl logs -f deployment/openclaw-scheduler -n openclaw
```

### Q2: 测试失败怎么办？

**A**: 查看 Pod 状态
```bash
kubectl get pods -n openclaw
kubectl describe pod <pod-name> -n openclaw
```

### Q3: 如何切换内核？

**A**: 三种方式
1. **HTTP Header**（推荐）：`X-Kernel-Type: openclaw|qwenpaw`
2. **环境变量**：修改 ConfigMap 中的 `KERNEL_TYPE`
3. **默认**：不指定则使用 OpenClaw

### Q4: 如何查看日志？

**A**: 
```bash
# Scheduler 日志
kubectl logs -f deployment/openclaw-scheduler -n openclaw

# OpenClaw 日志
kubectl logs -f <openclaw-pod-name> -n openclaw
```

---

## 🎯 功能特性

- ✅ **双内核支持**：OpenClaw + QwenPaw
- ✅ **灵活切换**：环境变量 + HTTP Header
- ✅ **向后兼容**：保留 V1 API
- ✅ **生产就绪**：完整配置和健康检查
- ✅ **一键部署**：自动化脚本
- ✅ **一键测试**：完整测试套件

---

## 📊 系统架构

```
Frontend (Vue3)
    ↓ HTTP/SSE
Scheduler (Go) ──┬─> OpenClaw (WebSocket)
    ↓            └─> QwenPaw (HTTP+SSE)
Kernel Factory
```

---

## 🔥 快速命令

```bash
# 部署
./deploy-configurable-kernel.sh

# 测试
./test-configurable-kernel.sh

# 查看状态
kubectl get pods -n openclaw

# 查看日志
kubectl logs -f deployment/openclaw-scheduler -n openclaw

# 重启 Scheduler
kubectl delete pod -n openclaw -l app=openclaw-scheduler

# 查看配置
kubectl get configmap scheduler-config -n openclaw -o yaml
```

---

## 🎉 开始使用

```bash
# 1. 克隆仓库（如果还没有）
cd agent-openclaw-assisant

# 2. 一键部署
./deploy-configurable-kernel.sh

# 3. 一键测试
./test-configurable-kernel.sh

# 4. 查看文档
cat docs/25-可配置内核使用指南.md
```

---

**祝您使用愉快！** 🚀

如有问题，请查看：
- [使用指南](docs/25-可配置内核使用指南.md)
- [故障排查](docs/25-可配置内核使用指南.md#🐛-故障排查)
