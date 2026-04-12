# WebSocket 方案实施总结

## 📝 任务概览

**目标**: 改造 Scheduler 使用 WebSocket 与 OpenClaw Gateway 通信，实现真正的实时流式输出

**状态**: ⚠️ 遇到认证握手问题

---

## ✅ 已完成工作

### 1. WebSocket 连接池实现
**文件**: `scheduler-go/internal/websocket/pool.go`

**功能**:
- 连接复用：多个请求共享同一个 WebSocket 连接
- 自动重连：检测断开并自动重建连接
- 心跳保活：定期发送 ping 保持连接活跃

```go
// 核心 API
pool := websocket.NewPool()
conn, err := pool.GetConn(podIP)
```

### 2. ChatStream 函数改造
**文件**: `scheduler-go/internal/api/api.go`

**改动**:
- 移除 HTTP 客户端调用
- 使用 WebSocket 发送 `agent.message` RPC 请求
- 实时监听 `event.chat` 事件并转换为 HTTP SSE 输出给前端
- SessionKey 管理：每个请求生成独立的 sessionKey

```go
// WebSocket 请求格式
{
  "type": "req",
  "id": requestID,
  "method": "agent.message",
  "params": {
    "sessionKey": sessionKey,
    "message": message
  }
}
```

### 3. 依赖更新
- 添加 `gorilla/websocket v1.5.3`
- Go模块已更新

### 4. Docker 镜像构建
- 镜像：`openclaw-scheduler:websocket`
- 已成功构建并部署到 K8s

---

## ❌ 当前问题

### 认证握手失败

**错误信息**:
```
websocket: close 1008 (policy violation): invalid request frame
```

**原因分析**:

OpenClaw Gateway 的 WebSocket 握手流程如下：

```
1. Client -> Server: {"type":"connect","protocol":3,"client":{...}}
2. Server -> Client: {"type":"event","event":"connect.challenge","payload":{"nonce":"..."}}
3. Client -> Server: {"type":"req","method":"connect","params":{...}}
4. Server -> Client: {"type":"res","ok":true,"payload":{...HelloOk...}}
```

当前实现在 **第 3 步** 失败，服务器拒绝了我们的 `connect` 请求。

**服务器端校验逻辑**:

根据源码分析（`workspace/source/openclaw/src/gateway/server/ws-connection/message-handler.ts:396-406`），
服务器会严格校验：

1. `validateRequestFrame(parsed)` - 请求帧格式
2. `parsed.method === "connect"` - 方法名必须是 connect  
3. `validateConnectParams(parsed.params)` - 参数校验

**ConnectParams Schema**（必须字段）:

```typescript
{
  minProtocol: Integer,  // ✅ 已提供
  maxProtocol: Integer,  // ✅ 已提供
  client: {
    id: GatewayClientIdSchema,     // ✅ 已提供: "scheduler"
    version: NonEmptyString,        // ✅ 已提供: "1.0.0"
    platform: NonEmptyString,       // ✅ 已提供: "linux"
    mode: GatewayClientModeSchema,  // ✅ 已提供: "backend"
  }
  // 其他字段为可选
}
```

**已尝试的修复**:
1. ❌ 使用 `method: "connect.response"` - 错误的方法名
2. ❌ 缺少 `platform` 字段 - 已补充但仍失败
3. ❌ 使用 `mode: "headless"` - 改为 `"backend"` 但仍失败

**可能的原因**:
1. **缺少必须的嵌套字段**: Schema 可能有更深层的必须字段（如 `auth`、`role`、`scopes`）
2. **字段类型错误**: 某些字段的类型或格式不符合 Schema 定义
3. **认证要求**: 即使配置了 `auth.mode=none`，服务器可能仍要求某些认证字段
4. **协议版本问题**: protocol 3 可能有额外的必须字段

---

## 📚 参考资料

### OpenClaw 客户端实现

**文件**: `workspace/source/openclaw/src/gateway/client.ts:267-367`

**正确的 connect 请求示例**:

```typescript
void this.request<HelloOk>("connect", {
  minProtocol: PROTOCOL_VERSION,
  maxProtocol: PROTOCOL_VERSION,
  client: {
    id: clientName ?? "gateway-client",
    displayName: clientDisplayName,
    version: clientVersion ?? VERSION,
    platform: platform,           // 如 "linux", "darwin", "win32"
    deviceFamily: deviceFamily,   // 可选
    modelIdentifier: undefined,   // 可选
    mode: mode ?? "backend",      // "backend" | "headless" | "webchat"
    instanceId: instanceId,       // 可选
  },
  caps: caps || [],
  commands: commands,             // 可选
  permissions: permissions,       // 可选
  pathEnv: pathEnv,               // 可选
  role: role ?? "operator",       // ⚠️ 可能必须
  scopes: scopes ?? ["operator.admin"], // ⚠️ 可能必须
  device: device,                 // 设备签名认证（可选但复杂）
  auth: {                         // 认证信息
    token: token,                 // 共享 token
    deviceToken: deviceToken,     // 设备 token
    password: password,           // 密码
  },
})
```

### Schema 验证

**文件**: `workspace/source/openclaw/src/gateway/protocol/schema/frames.ts:20-50`

**ConnectParamsSchema 完整定义**:

```typescript
Type.Object({
  minProtocol: Type.Integer({ minimum: 1 }),
  maxProtocol: Type.Integer({ minimum: 1 }),
  client: Type.Object({
    id: GatewayClientIdSchema,
    displayName: Type.Optional(NonEmptyString),
    version: NonEmptyString,
    platform: NonEmptyString,
    deviceFamily: Type.Optional(NonEmptyString),
    modelIdentifier: Type.Optional(NonEmptyString),
    mode: GatewayClientModeSchema,
    instanceId: Type.Optional(NonEmptyString),
  }, { additionalProperties: false }),
  caps: Type.Optional(Type.Array(NonEmptyString, { default: [] })),
  commands: Type.Optional(Type.Array(NonEmptyString)),
  permissions: Type.Optional(Type.Record(NonEmptyString, Type.Boolean())),
  pathEnv: Type.Optional(Type.String()),
  role: Type.Optional(NonEmptyString),
  scopes: Type.Optional(Type.Array(NonEmptyString)),
  device: Type.Optional(...),
  auth: Type.Optional(...),
}, { additionalProperties: false })
```

---

## 🔧 下一步方案

### 方案 A: 完整实现认证握手（推荐，但耗时）

**步骤**:
1. 添加 `role: "operator"` 和 `scopes: ["operator.admin"]` 到 connect 请求
2. 添加空的 `auth: {}` 对象（依赖 `auth.mode=none`）
3. 添加空的 `caps: []` 数组
4. 详细记录服务器返回的错误信息（如果有 error 字段）
5. 根据错误信息逐步补充缺失字段

**预计时间**: 2-4 小时

**优点**: 
- 彻底解决问题
- 架构清晰，无需修改 OpenClaw 源码
- 支持真正的实时流式

**缺点**:
- 需要深入研究 OpenClaw 协议
- 可能涉及复杂的设备签名认证

### 方案 B: 简化 OpenClaw 认证配置

**思路**: 检查是否可以完全禁用 WebSocket 握手认证

**配置项** (推测，需验证):
```yaml
auth:
  mode: none
  dangerouslyDisableDeviceAuth: true
  disableConnectChallenge: true  # 如果存在此配置
```

**优点**: 快速解决
**缺点**: 可能不存在这样的配置

### 方案 C: 回退到 HTTP 修复方案

**思路**: 放弃 WebSocket，专注于修复 HTTP SSE 接口的缓冲问题

**方案 C.1 - 修复 OpenClaw HTTP SSE**:
- 继续深入调试 `openai-http.ts` 和 `http-common.ts`
- 确保 `res.socket.setNoDelay(true)` 真正生效
- 检查是否有其他中间件或代理在缓冲

**方案 C.2 - 直接连接 Ollama**:
- Scheduler 跳过 OpenClaw，直接调用 Ollama HTTP API
- 优点：简单直接，Ollama 原生支持流式
- 缺点：绕过了 OpenClaw 的智能体管理功能

---

## 🎯 建议

鉴于当前遇到的复杂握手问题，建议：

1. **短期（1-2小时）**: 尝试方案 A 的前 3 步（添加 role/scopes/auth/caps）
   - 如果还失败，详细记录错误信息

2. **中期（2-4小时）**: 
   - 如果方案 A 快速修复成功 → 继续完善 WebSocket 方案
   - 如果方案 A 陷入僵局 → 考虑方案 B（简化配置）或方案 C.1（修复 HTTP）

3. **长期优化**: 
   - WebSocket 方案是正确方向，应该持续投入
   - 但可能需要更深入的协议研究和测试

---

## 📦 交付物

### 代码变更

1. **新增文件**:
   - `scheduler-go/internal/websocket/pool.go` (WebSocket 连接池)

2. **修改文件**:
   - `scheduler-go/internal/api/api.go` (ChatStream 使用 WebSocket)
   - `scheduler-go/go.mod` (添加 gorilla/websocket 依赖)
   - `scheduler-go/go.sum` (依赖锁定)

3. **Docker 镜像**:
   - `openclaw-scheduler:websocket` (已构建并部署)

### K8s 部署

- **Deployment**: `openclaw-pool` (无需修改)
- **Service**: `openclaw-pool` (无需修改 sessionAffinity)
- **Deployment**: `openclaw-scheduler` (已更新镜像)

**验证**:
```bash
kubectl get pods -n openclaw -l app=openclaw-scheduler
# 应显示 Running 状态
```

---

## 🔍 调试信息

### 当前日志输出

```
🔵 [ChatStream] 收到请求 from 10.1.0.220
✅ [ChatStream] 解析成功 - AgentID: test-agent
⏳ [ChatStream] 开始分配容器...
✅ [ChatStream] 容器分配成功 - Pod: openclaw-pool-xxx, IP: 10.1.0.210
✅ [WSPool] 连接池已初始化
🔌 [WSPool] 建立新连接: ws://10.1.0.210:18789
⚠️  [WSPool] 收到 connect.challenge，nonce: xxx
📤 [WSPool] 已发送 connect 请求，等待响应...
❌ [ChatStream] WebSocket 连接失败: 握手响应失败: 
    websocket: close 1008 (policy violation): invalid request frame
```

### 关键代码位置

**连接池握手逻辑**:
```go
// scheduler-go/internal/websocket/pool.go:91-143
if event == "connect.challenge" {
    // ...
    connectReq := map[string]interface{}{
        "type":   "req",
        "id":     "connect-1",
        "method": "connect",
        "params": map[string]interface{}{
            "minProtocol": 3,
            "maxProtocol": 3,
            "client": map[string]interface{}{
                "id":       "scheduler",
                "mode":     "backend",
                "version":  "1.0.0",
                "platform": "linux",
            },
        },
    }
    // ... WriteJSON(connectReq)
}
```

**需要添加的字段** (推测):
```go
"params": map[string]interface{}{
    // ... 现有字段 ...
    "role":  "operator",
    "scopes": []string{"operator.admin"},
    "auth":  map[string]interface{}{},  // 空对象
    "caps":  []string{},                 // 空数组
}
```

---

## 💡 经验总结

1. **OpenClaw 协议的复杂性超出预期**
   - WebSocket 握手需要精确匹配 Schema
   - 即使 `auth.mode=none`，仍可能需要某些认证字段

2. **HTTP SSE 和 WebSocket 的差异**
   - Control UI 使用 WebSocket 是流式的
   - OpenAI-compatible HTTP API 确实存在缓冲问题
   - 这证实了 WebSocket 方案的必要性

3. **调试策略**
   - 需要更详细的服务器端错误信息
   - 建议在 OpenClaw Gateway 添加调试日志
   - 或者使用 Wireshark 抓包分析

---

**文档生成时间**: 2026-04-11 21:28
**负责人**: AI Assistant
**状态**: 待决策下一步方案
