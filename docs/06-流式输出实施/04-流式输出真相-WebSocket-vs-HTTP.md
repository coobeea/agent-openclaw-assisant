# 流式输出真相：WebSocket vs HTTP SSE

## 🎯 关键发现

**Control UI 的流式输出是实时的**，因为它使用的是 **WebSocket 协议**，而不是 HTTP SSE！

## 📊 两种协议对比

### WebSocket（Control UI 使用）✅ 实时流式

```
浏览器 (Control UI)
  ↓ WebSocket 连接
OpenClaw Gateway (ws://localhost:18789)
  ↓ onAgentEvent 订阅
Agent 运行时
  ↓ emitAgentEvent({ stream: "assistant", delta: "你" })
  ↓ broadcast("chat", payload)  # 立即通过 WebSocket 发送！
  ↓ ws.send(JSON.stringify(event))
Control UI
  ↓ 实时显示每个 token ✅
```

**关键代码**（`server-chat.ts:485-491`）：
```typescript
// Assistant 流式更新
if (evt.stream === "assistant" && typeof evt.data?.text === "string") {
  const payload = {
    kind: "assistant" as const,
    role: "assistant",
    text: evt.data.text,
    delta: evt.data.delta,
  };
  broadcast("chat", payload); // 立即广播到所有 WebSocket 客户端！
}
```

### HTTP SSE（OpenAI 兼容接口）❌ 聚合输出

```
Scheduler
  ↓ HTTP POST /v1/chat/completions
OpenClaw Gateway (openai-http.ts)
  ↓ onAgentEvent 订阅
  ↓ const unsubscribe = onAgentEvent((evt) => { ... })
Agent 运行时
  ↓ emitAgentEvent({ stream: "assistant", delta: "你" })
  ❌ onAgentEvent 回调没有被实时触发！
  ⏳ 等待 agentCommandFromIngress() 完成...
  ⏳ 12-32 秒后...
  ↓ if (!sawAssistantDelta) { // 从未收到流式事件
  ↓   writeAssistantContentChunk(res, { content: fullText });
  ↓ }
Scheduler
  ↓ 一次性收到完整响应 ❌
```

**关键代码**（`openai-http.ts:523-561`）：
```typescript
const unsubscribe = onAgentEvent((evt) => {
  if (evt.runId !== runId) return;
  if (closed) return;

  if (evt.stream === "assistant") {
    const content = resolveAssistantStreamDeltaText(evt) ?? "";
    if (!content) return;

    // ❌ 这段代码理论上应该被实时调用，但实际没有！
    writeAssistantContentChunk(res, { runId, model, content });
    return;
  }
});

// ⏳ 等待整个 Agent 执行完成
const result = await agentCommandFromIngress(commandInput, defaultRuntime, deps);

// ❌ 因为上面的回调没有被触发，这里会输出完整响应
if (!sawAssistantDelta) {
  const content = resolveAgentResponseText(result);
  writeAssistantContentChunk(res, { content });
}
```

## 🔍 问题根源

### 为什么 WebSocket 是实时的？

`server-chat.ts` 中的 `broadcast()` 函数**直接发送**事件：

```typescript
function broadcast(type: string, payload: unknown) {
  const frame = { type: "event", event: type, payload };
  
  // 遍历所有 WebSocket 连接，立即发送！
  for (const conn of connections) {
    conn.ws.send(JSON.stringify(frame));
  }
}
```

### 为什么 HTTP SSE 不是实时的？

`openai-http.ts` 中的 `onAgentEvent()` 回调**没有被实时触发**！

**可能原因**：
1. **事件总线延迟**：`emitAgentEvent` → `onAgentEvent` 之间有延迟
2. **异步执行顺序**：`agentCommandFromIngress()` 阻塞了主线程
3. **事件订阅时机**：订阅发生在 Agent 启动之后，错过了早期事件
4. **Agent 运行模式**：可能有"批处理模式"，在完成前不触发事件

## 💡 解决方案

### 方案 A：模仿 WebSocket 的 broadcast 机制（推荐）

修改 `openai-http.ts`，不使用 `onAgentEvent`，而是直接订阅底层的事件总线：

```typescript
// 1. 导入 broadcast 机制
import { ChatEventBroadcast } from "./server-chat.js";

// 2. 直接订阅流式事件
const eventListener = (evt: AgentEventPayload) => {
  if (evt.runId !== runId) return;
  if (closed) return;
  
  if (evt.stream === "assistant" && evt.data?.delta) {
    // 立即写入 SSE
    res.write(`data: ${JSON.stringify({
      id: runId,
      object: "chat.completion.chunk",
      choices: [{
        delta: { content: evt.data.delta },
        finish_reason: null
      }]
    })}\n\n`);
    flusher.flush(); // 立即 flush
  }
};

// 3. 直接注册到事件总线（而不是 onAgentEvent）
agentEventBus.addListener(eventListener);

// 4. Agent 执行（不阻塞）
void agentCommandFromIngress(...);
```

### 方案 B：使用 WebSocket 替代 HTTP SSE

让 Scheduler 也通过 WebSocket 连接到 OpenClaw Gateway：

```go
// scheduler-go/internal/api/api.go
func ChatStream(c *gin.Context) {
    // 1. 升级为 WebSocket
    upgrader := websocket.Upgrader{}
    ws, err := upgrader.Upgrade(c.Writer, c.Request, nil)
    
    // 2. 连接到 OpenClaw Gateway WebSocket
    gatewayWs, _ := websocket.Dial(fmt.Sprintf("ws://%s:18789", podIP))
    
    // 3. 发送聊天请求
    gatewayWs.WriteJSON(map[string]interface{}{
        "type": "req",
        "id": requestID,
        "method": "agent.message",
        "params": map[string]interface{}{
            "message": req.Message,
            "agentId": req.AgentID,
        },
    })
    
    // 4. 实时转发事件
    for {
        var event map[string]interface{}
        gatewayWs.ReadJSON(&event)
        
        if event["type"] == "event" && event["event"] == "chat" {
            // 转换为 OpenAI SSE 格式
            sseData := convertToOpenAISSE(event["payload"])
            c.SSEvent("message", sseData)
            c.Writer.Flush()
        }
    }
}
```

### 方案 C：修复 Agent 事件触发机制（根本解决）

深入 `@mariozechner/pi-agent-core` 源码，找到为什么 `emitAgentEvent` 不会立即触发 `onAgentEvent` 回调：

```typescript
// 可能的问题：事件总线使用了 setTimeout 或 setImmediate
export function emitAgentEvent(event: AgentEventPayload) {
  // ❌ 错误：延迟触发
  setTimeout(() => {
    for (const listener of listeners) {
      listener(event);
    }
  }, 0);
  
  // ✅ 正确：立即触发
  for (const listener of listeners) {
    listener(event);
  }
}
```

## 📋 实施建议

### 短期（立即可用）
使用 **方案 B - WebSocket 替代 HTTP**：
- 修改 Scheduler，通过 WebSocket 连接 OpenClaw Gateway
- 复用 Control UI 的实时流式能力
- 无需修改 OpenClaw 源码

### 中期（优化性能）
使用 **方案 A - 模仿 broadcast**：
- 在 `openai-http.ts` 中直接订阅底层事件
- 绕过 `onAgentEvent` 的延迟问题
- 保持 HTTP SSE 协议兼容性

### 长期（根本解决）
使用 **方案 C - 修复事件机制**：
- 深入 OpenClaw 源码，找到事件延迟的根本原因
- 提交 PR 修复上游问题
- 受益所有使用 OpenClaw 的项目

## 🎯 结论

**OpenClaw 本身支持流式输出**，但：
- ✅ WebSocket 接口（Control UI）：实时流式 ✅
- ❌ HTTP SSE 接口（OpenAI 兼容）：聚合输出 ❌

问题不在网络层（Nginx、Scheduler、TCP 都已优化），而在 **OpenClaw Gateway 的 OpenAI HTTP 适配层没有正确实现流式**。

推荐优先尝试 **方案 B（WebSocket）**，因为：
1. 无需修改 OpenClaw 源码
2. 复用已验证的实时流式能力
3. 实施成本低，风险小
