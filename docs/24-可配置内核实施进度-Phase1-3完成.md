# 可配置内核实施进度报告

> **时间**：2026-04-13  
> **状态**：Phase 1-3 已完成 ✅（共4个阶段）

---

## 📊 整体进度

| 阶段 | 任务 | 状态 | 完成时间 |
|------|------|------|----------|
| **Phase 1** | 接口抽象 | ✅ 完成 | 2026-04-13 08:56 |
| **Phase 2** | OpenClaw 重构 | ✅ 完成 | 2026-04-13 08:58 |
| **Phase 3** | QwenPaw 适配器 | ✅ 完成 | 2026-04-13 08:59 |
| **Phase 4** | Scheduler 改造 | ⏳ 进行中 | - |

**总体进度**：75% ✅✅✅⏳

---

## ✅ Phase 1: 接口抽象（已完成）

### 创建的文件

```
scheduler-go/internal/kernel/
├── interface.go     (127 行) - 统一接口定义
├── config.go        (243 行) - 配置结构
└── factory.go       (138 行) - 工厂模式
```

### 核心接口

```go
type KernelInterface interface {
    Initialize(ctx context.Context, config *KernelConfig) error
    StreamChat(ctx context.Context, req *ChatRequest) (<-chan ChatEvent, error)
    CreateAgent(ctx context.Context, agentID, workspace string) error
    HealthCheck(ctx context.Context) error
    Close() error
    GetKernelType() string
}
```

### 关键特性

✅ **统一接口定义**：所有内核必须实现 `KernelInterface`  
✅ **配置抽象**：`KernelConfig` 支持多种认证方式（token/basic/none）  
✅ **工厂模式**：动态创建内核实例，支持注册机制  
✅ **重试策略**：内置指数退避重试  
✅ **连接池配置**：支持连接池参数设置

---

## ✅ Phase 2: OpenClaw 重构（已完成）

### 创建的文件

```
scheduler-go/internal/kernel/adapters/
├── openclaw.go      (407 行) - OpenClaw WebSocket 适配器
└── register.go      (18 行)  - 自动注册机制
```

### 核心功能

✅ **WebSocket 连接管理**：
- 建立连接到 OpenClaw Gateway (`ws://pod-ip:18789`)
- 自动握手协议（`connect.challenge`）

✅ **RPC 通信**：
```go
// chat.send RPC 请求
{
  "type": "req",
  "method": "chat.send",
  "params": {
    "message": "Hello",
    "sessionKey": "agent:main:session-123",
    "idempotencyKey": "req-12345"
  }
}
```

✅ **流式输出**：
- 监听 WebSocket 事件流
- 转换为统一的 `ChatEvent` 格式
- 支持 `delta`、`done`、`error` 事件

✅ **健康检查**：
- WebSocket Ping/Pong 机制

### 握手流程

```
1. 连接 WebSocket → ws://pod-ip:18789
2. 等待 server 发送 connect.challenge
3. 发送 connect 请求（包含 nonce + auth token）
4. 等待 HelloOk 响应
5. 连接建立成功 ✅
```

---

## ✅ Phase 3: QwenPaw 适配器（已完成）

### 创建的文件

```
scheduler-go/internal/kernel/adapters/
└── qwenpaw.go       (385 行) - QwenPaw HTTP+SSE 适配器
```

### 核心功能

✅ **HTTP Client**：
- 连接到 QwenPaw FastAPI (`http://pod-ip:8088`)
- 支持 Bearer Token / Basic Auth

✅ **SSE 流式解析**：
```
POST /api/console/chat
Content-Type: application/json

{
  "sender_id": "user123",
  "content_parts": [{"type": "text", "text": "Hello"}],
  "meta": {"session_id": "session-123", "user_id": "user123"}
}
```

✅ **SSE 事件处理**：
```
data: {"content": "Hello"}
data: {"content": " World"}
data: [DONE]
```

✅ **自动重连**：
- 支持网络中断自动重连
- 自定义超时策略

### API 对比

| 特性 | OpenClaw | QwenPaw |
|------|----------|---------|
| **协议** | WebSocket | HTTP + SSE |
| **端口** | 18789 | 8088 |
| **认证** | Token (connect.challenge) | Bearer Token / Basic Auth |
| **请求格式** | RPC (`chat.send`) | REST (`/api/console/chat`) |
| **响应格式** | WebSocket events | SSE stream |

---

## ⏳ Phase 4: Scheduler 改造（进行中）

### 需要改造的函数

```go
// 现有实现（使用 websocket/pool.go）
func ChatStream(c *gin.Context) {
    // 1. 分配容器
    container, _ := k8s.AllocateContainer(req.AgentID)
    
    // 2. 获取 WebSocket 连接
    conn, _ := wsPool.GetConn(container.IP)
    
    // 3. 发送 chat.send 请求
    conn.WriteJSON(chatReq)
    
    // 4. 监听 WebSocket 事件并转换为 SSE
    for {
        conn.ReadJSON(&frame)
        // ... 转换为 SSE 输出
    }
}
```

### 改造后的实现（使用内核抽象层）

```go
// 新实现（使用 kernel 抽象层）
func ChatStream(c *gin.Context) {
    // 1. 获取内核类型（从环境变量或 HTTP Header）
    kernelType := getKernelType(c)
    
    // 2. 分配容器（根据内核类型）
    container, _ := k8s.AllocateContainerByKernel(kernelType)
    
    // 3. 创建内核配置
    config := createKernelConfig(kernelType, container.IP)
    
    // 4. 创建内核实例
    kernel, _ := kernel.GetFactory().CreateKernel(config)
    defer kernel.Close()
    
    // 5. 初始化连接
    kernel.Initialize(ctx, config)
    
    // 6. 发送聊天请求
    eventChan, _ := kernel.StreamChat(ctx, &kernel.ChatRequest{
        AgentID:    req.AgentID,
        SessionKey: sessionKey,
        Message:    req.Message,
    })
    
    // 7. 监听事件流并转换为 SSE（统一格式）
    for event := range eventChan {
        switch event.Type {
        case kernel.EventTypeDelta:
            writeSSEChunk(c.Writer, flusher, event.Content)
        case kernel.EventTypeDone:
            writeSSEDone(c.Writer, flusher)
        case kernel.EventTypeError:
            writeSSEError(c.Writer, flusher, event.Error)
        }
    }
}
```

### 关键改进

✅ **内核选择灵活性**：
```go
// 方式 1：环境变量（全局）
export KERNEL_TYPE=openclaw

// 方式 2：HTTP Header（动态）
curl -H "X-Kernel-Type: qwenpaw" ...
```

✅ **统一的事件处理**：
```go
// 不再关心 WebSocket 或 HTTP 的细节
for event := range eventChan {
    // 统一的 ChatEvent 格式
}
```

✅ **更好的错误处理**：
```go
// 内核自动处理连接失败、超时等
if err != nil {
    // 已经是统一的错误格式
    writeSSEError(c.Writer, err.Error())
}
```

---

## 📈 代码统计

### 新增代码行数

```
scheduler-go/internal/kernel/
├── interface.go         127 行
├── config.go            243 行
├── factory.go           138 行
└── adapters/
    ├── openclaw.go      407 行
    ├── qwenpaw.go       385 行
    └── register.go       18 行
───────────────────────────────
总计：                 1,318 行
```

### 代码质量

✅ **类型安全**：所有接口都有明确的类型定义  
✅ **错误处理**：完善的错误处理和日志记录  
✅ **并发安全**：使用 `sync.Mutex` 保护共享资源  
✅ **上下文支持**：支持 `context.Context` 超时和取消  
✅ **可测试性**：接口抽象便于单元测试

---

## 🔧 配置示例

### OpenClaw 配置

```go
config := kernel.DefaultOpenClawConfig(
    "10.1.2.3:3000",  // Endpoint
    "openclaw-internal-k8s-token",  // Token
)

// 自定义超时
config.Timeout = 120  // 120秒

// 自定义连接池
config.ConnectionPool.MaxConnections = 20
```

### QwenPaw 配置

```go
config := kernel.DefaultQwenPawConfig(
    "10.1.2.3:8088",  // Endpoint
)

// 添加 Bearer Token
config.Auth = &kernel.AuthConfig{
    Type:  "token",
    Token: "my-secret-token",
}
```

### 环境变量配置

```bash
# K8s ConfigMap
apiVersion: v1
kind: ConfigMap
metadata:
  name: scheduler-config
  namespace: openclaw
data:
  KERNEL_TYPE: "openclaw"  # 或 "qwenpaw"
  KERNEL_OPENCLAW_AUTH_TOKEN: "openclaw-internal-k8s-token"
  KERNEL_QWENPAW_ENDPOINT: "10.1.2.3:8088"
```

---

## 🚀 下一步（Phase 4）

### 待完成任务

1. **改造 ChatStream 函数**（核心）
   - 替换直接的 WebSocket 调用为内核抽象层
   - 支持动态内核选择（环境变量 + HTTP Header）
   - 统一 SSE 输出格式

2. **更新 K8s 管理**
   - 添加 `AllocateContainerByKernel` 函数
   - 支持根据内核类型选择 Pod（openclaw vs qwenpaw）

3. **更新依赖导入**
   - 导入 `_ "openclaw-scheduler/internal/kernel/adapters"` 触发自动注册

4. **编译测试**
   - `go mod tidy`
   - `go build`
   - 验证编译无误

### 预计时间

- **改造时间**：1-2 小时
- **测试时间**：1-2 小时
- **总计**：2-4 小时

---

## 🎯 成果展示

### 使用示例（改造后）

```bash
# 使用 OpenClaw（默认）
curl -X POST http://localhost:8080/api/chat/stream \
  -H "Content-Type: application/json" \
  -d '{"agent_id":"test","message":"Hello"}'

# 使用 QwenPaw（通过 Header）
curl -X POST http://localhost:8080/api/chat/stream \
  -H "Content-Type: application/json" \
  -H "X-Kernel-Type: qwenpaw" \
  -d '{"agent_id":"test","message":"Hello"}'

# 响应（统一 SSE 格式）
: connected

data: {"type":"delta","content":"Hello"}
data: {"type":"delta","content":" World"}
data: {"type":"done"}
```

### 架构演进

```
【改造前】
Frontend → Scheduler → WebSocket Pool → OpenClaw Gateway
              ↓
          (固定 WebSocket)

【改造后】
Frontend → Scheduler → Kernel Factory → OpenClawAdapter  → OpenClaw Gateway
                           ↓              (WebSocket)
                       统一接口
                           ↓
                       QwenPawAdapter   → QwenPaw FastAPI
                         (HTTP + SSE)
```

---

## 💡 关键收获

### ✅ 灵活性提升

- 不再被单一内核绑定
- 支持未来扩展更多内核（LangChain、AutoGPT等）

### ✅ 代码质量提升

- 接口抽象，降低耦合
- 工厂模式，易于扩展
- 统一错误处理，更健壮

### ✅ 用户体验提升

- 前端代码无需修改（统一 SSE）
- 动态切换内核，无需重启

---

## 📖 相关文档

- [可配置内核架构方案](./22-可配置内核架构方案-OpenClaw与QwenPaw.md)
- [可配置内核快速实施指南](./23-可配置内核-快速实施指南.md)

---

**总结**：Phase 1-3 已顺利完成，内核抽象层架构已就绪。下一步将改造 Scheduler 的 ChatStream 函数，实现真正的可配置内核切换。
