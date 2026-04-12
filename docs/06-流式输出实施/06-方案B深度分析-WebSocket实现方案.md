# 方案 B 深度分析：WebSocket 实现方案

## 🎯 核心疑问解答

### ❓ 为什么需要 sessionAffinity？

**答案：不需要！** 之前的分析有误。

### 📊 两种连接方式对比

#### 方式 1：通过 Service 域名连接（需要 sessionAffinity）
```go
// ❌ 错误方式：通过 Service
url := "ws://openclaw-pool:18789"  // Service 域名
conn, _ := websocket.Dial(url, nil)

问题：
  每次连接，Service 会随机选择 Pod
  第1次: Service → Pod-1 (10.1.0.203)
  第2次: Service → Pod-3 (10.1.0.212)  ❌ 连错了！
  
解决：需要 sessionAffinity: ClientIP
  确保同一个 Scheduler IP 总是路由到同一个 Pod
```

#### 方式 2：直接连接 Pod IP（我们的实现）✅
```go
// ✅ 正确方式：直接用 Pod IP
podInfo := allocatePod(agentID)  // 返回: {IP: "10.1.0.203"}
url := fmt.Sprintf("ws://%s:18789", podInfo.IP)
conn, _ := websocket.Dial(url, nil)

优点：
  Scheduler 完全控制连接目标
  AgentID → Pod IP 映射由 Scheduler 维护
  不经过 Service，无需 sessionAffinity ✅
```

### 🎯 结论

**您说得完全对**：
- ✅ Scheduler 已经维护了 `AgentID → PodIP` 映射
- ✅ 连接时直接使用 Pod IP
- ✅ **完全不需要 sessionAffinity**
- ✅ **也不需要修改 Service 配置**

我之前的分析是错误的，感谢您的质疑！

---

## 🏗️ 方案 B 详细设计

### 架构图

```
┌─────────────────────────────────────────────────────────────┐
│                    Scheduler (Go)                           │
│                                                             │
│  ┌────────────────────────────────────────────────────┐   │
│  │          AgentMap (内存映射)                        │   │
│  │  agent-001 → {PodIP: 10.1.0.203, SessionKey: xxx}  │   │
│  │  agent-002 → {PodIP: 10.1.0.204, SessionKey: yyy}  │   │
│  │  agent-003 → {PodIP: 10.1.0.203, SessionKey: zzz}  │   │
│  └────────────────────────────────────────────────────┘   │
│                          ↓                                  │
│  ┌────────────────────────────────────────────────────┐   │
│  │       WebSocket 连接池 (wsPool)                     │   │
│  │  10.1.0.203 → ws.Conn (复用，多个 Agent 共享)      │   │
│  │  10.1.0.204 → ws.Conn                               │   │
│  │  10.1.0.212 → ws.Conn                               │   │
│  └────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                          ↓ 直接连接 Pod IP
         ┌────────────────┼────────────────┐
         ↓                ↓                ↓
┌────────────────┐ ┌────────────────┐ ┌────────────────┐
│  OpenClaw Pod  │ │  OpenClaw Pod  │ │  OpenClaw Pod  │
│  10.1.0.203    │ │  10.1.0.204    │ │  10.1.0.212    │
│                │ │                │ │                │
│  WS Server     │ │  WS Server     │ │  WS Server     │
│  :18789        │ │  :18789        │ │  :18789        │
└────────────────┘ └────────────────┘ └────────────────┘
```

### 关键设计点

#### 1. 一对多映射
```
一个 Pod 可以服务多个 Agent：
  Pod 10.1.0.203
    ├─ Agent-001 (sessionKey: xxx)
    ├─ Agent-003 (sessionKey: zzz)
    └─ Agent-007 (sessionKey: www)
    
一个 WebSocket 连接服务多个 Agent：
  ws://10.1.0.203:18789
    ├─ 接收事件: {sessionKey: "xxx", ...}  → Agent-001
    ├─ 接收事件: {sessionKey: "zzz", ...}  → Agent-003
    └─ 接收事件: {sessionKey: "www", ...}  → Agent-007
```

**关键**：通过 `sessionKey` 区分不同的 Agent！

#### 2. 连接复用
```go
// 多个 Agent 共享同一个 WebSocket 连接
type WebSocketPool struct {
    conns map[string]*websocket.Conn  // podIP → conn
    mu    sync.RWMutex
}

// Agent-001 和 Agent-003 都在 Pod 10.1.0.203 上
// 他们共享同一个 WebSocket 连接
conn := wsPool.GetConn("10.1.0.203")  // 复用连接

// 通过 sessionKey 区分
conn.WriteJSON(map[string]interface{}{
    "type": "req",
    "id": uuid.New(),
    "method": "agent.message",
    "params": map[string]interface{}{
        "sessionKey": "xxx",  // Agent-001 的 sessionKey
        "message": "你好",
    },
})
```

---

## 💻 代码实现

### 1. WebSocket 连接池

```go
// scheduler-go/internal/websocket/pool.go
package websocket

import (
    "fmt"
    "sync"
    "github.com/gorilla/websocket"
    "log"
)

type Pool struct {
    conns map[string]*websocket.Conn  // podIP → conn
    mu    sync.RWMutex
}

func NewPool() *Pool {
    return &Pool{
        conns: make(map[string]*websocket.Conn),
    }
}

// 获取或创建连接（复用已有连接）
func (p *Pool) GetConn(podIP string) (*websocket.Conn, error) {
    // 1. 尝试获取已有连接
    p.mu.RLock()
    if conn, ok := p.conns[podIP]; ok && conn != nil {
        // 检查连接是否有效
        if err := conn.WriteControl(websocket.PingMessage, []byte{}, time.Now().Add(time.Second)); err == nil {
            p.mu.RUnlock()
            return conn, nil
        }
        // 连接已断开，需要重建
    }
    p.mu.RUnlock()
    
    // 2. 创建新连接
    p.mu.Lock()
    defer p.mu.Unlock()
    
    url := fmt.Sprintf("ws://%s:18789", podIP)
    log.Printf("建立 WebSocket 连接: %s", url)
    
    conn, _, err := websocket.DefaultDialer.Dial(url, nil)
    if err != nil {
        return nil, fmt.Errorf("连接失败: %v", err)
    }
    
    // 发送 connect 握手
    connectMsg := map[string]interface{}{
        "type": "connect",
        "protocol": 3,
        "client": map[string]interface{}{
            "name": "scheduler",
            "mode": "headless",
        },
    }
    if err := conn.WriteJSON(connectMsg); err != nil {
        conn.Close()
        return nil, fmt.Errorf("握手失败: %v", err)
    }
    
    // 等待 hello-ok
    var helloResp map[string]interface{}
    if err := conn.ReadJSON(&helloResp); err != nil {
        conn.Close()
        return nil, fmt.Errorf("握手响应失败: %v", err)
    }
    
    if helloResp["type"] != "hello-ok" {
        conn.Close()
        return nil, fmt.Errorf("握手失败: %v", helloResp)
    }
    
    log.Printf("✅ WebSocket 连接成功: %s", url)
    
    // 保存连接
    p.conns[podIP] = conn
    
    // 启动后台协程监听断开
    go p.monitorConnection(podIP, conn)
    
    return conn, nil
}

// 监听连接断开
func (p *Pool) monitorConnection(podIP string, conn *websocket.Conn) {
    for {
        _, _, err := conn.ReadMessage()
        if err != nil {
            log.Printf("⚠️ WebSocket 断开: %s, 错误: %v", podIP, err)
            p.mu.Lock()
            delete(p.conns, podIP)
            conn.Close()
            p.mu.Unlock()
            return
        }
    }
}

// 关闭连接
func (p *Pool) Close(podIP string) {
    p.mu.Lock()
    defer p.mu.Unlock()
    
    if conn, ok := p.conns[podIP]; ok {
        conn.Close()
        delete(p.conns, podIP)
        log.Printf("关闭 WebSocket 连接: %s", podIP)
    }
}

// 关闭所有连接
func (p *Pool) CloseAll() {
    p.mu.Lock()
    defer p.mu.Unlock()
    
    for podIP, conn := range p.conns {
        conn.Close()
        log.Printf("关闭 WebSocket 连接: %s", podIP)
    }
    p.conns = make(map[string]*websocket.Conn)
}
```

### 2. 改造 ChatStream

```go
// scheduler-go/internal/api/api.go
var wsPool = websocket.NewPool()

func ChatStream(c *gin.Context) {
    var req ChatRequest
    if err := c.ShouldBindJSON(&req); err != nil {
        c.JSON(400, gin.H{"error": "参数错误"})
        return
    }
    
    log.Printf("🔵 [ChatStream] 收到请求 - AgentID: %s, Message: %s", req.AgentID, req.Message)
    
    // 1. 分配 Pod
    podInfo := allocatePod(req.AgentID)
    log.Printf("✅ [ChatStream] 分配 Pod: %s", podInfo.IP)
    
    // 2. 获取或创建 WebSocket 连接（复用）
    conn, err := wsPool.GetConn(podInfo.IP)
    if err != nil {
        log.Printf("❌ [ChatStream] WebSocket 连接失败: %v", err)
        c.JSON(500, gin.H{"error": fmt.Sprintf("连接失败: %v", err)})
        return
    }
    
    // 3. 设置 SSE 响应头
    c.Header("Content-Type", "text/event-stream; charset=utf-8")
    c.Header("Cache-Control", "no-cache")
    c.Header("Connection", "keep-alive")
    c.Header("X-Accel-Buffering", "no")
    c.Status(200)
    
    flusher, ok := c.Writer.(http.Flusher)
    if !ok {
        c.JSON(500, gin.H{"error": "不支持流式传输"})
        return
    }
    
    // 4. 生成请求 ID 和 SessionKey
    requestID := uuid.New().String()
    sessionKey := podInfo.SessionKey  // 从 AgentMap 获取
    
    log.Printf("📡 [ChatStream] 发送消息 - RequestID: %s, SessionKey: %s", requestID, sessionKey)
    
    // 5. 发送聊天请求
    chatReq := map[string]interface{}{
        "type": "req",
        "id": requestID,
        "method": "agent.message",
        "params": map[string]interface{}{
            "sessionKey": sessionKey,
            "message": req.Message,
            // "agentId": req.AgentID,  // 不需要，sessionKey 已经关联了 Agent
        },
    }
    
    if err := conn.WriteJSON(chatReq); err != nil {
        log.Printf("❌ [ChatStream] 发送消息失败: %v", err)
        c.JSON(500, gin.H{"error": "发送消息失败"})
        return
    }
    
    log.Printf("⏳ [ChatStream] 等待响应...")
    
    // 6. 监听响应（实时流式）
    responseChan := make(chan map[string]interface{}, 100)
    errorChan := make(chan error, 1)
    done := make(chan bool, 1)
    
    // 启动协程读取 WebSocket 消息
    go func() {
        for {
            var frame map[string]interface{}
            err := conn.ReadJSON(&frame)
            if err != nil {
                errorChan <- err
                return
            }
            
            // 只处理我们的请求的响应
            if frame["type"] == "res" && frame["id"] == requestID {
                responseChan <- frame
                if !frame["ok"].(bool) {
                    errorChan <- fmt.Errorf("请求失败: %v", frame["error"])
                    return
                }
            } else if frame["type"] == "event" && frame["event"] == "chat" {
                payload := frame["payload"].(map[string]interface{})
                // 检查 sessionKey 是否匹配
                if payload["sessionKey"] == sessionKey {
                    responseChan <- frame
                }
            }
        }
    }()
    
    // 7. 处理事件流
    fullContent := ""
    
    for {
        select {
        case frame := <-responseChan:
            if frame["type"] == "event" && frame["event"] == "chat" {
                payload := frame["payload"].(map[string]interface{})
                
                // 处理 assistant 消息
                if payload["role"] == "assistant" {
                    delta := ""
                    if payload["delta"] != nil {
                        delta = payload["delta"].(string)
                    } else if payload["text"] != nil {
                        // 第一次可能只有 text
                        text := payload["text"].(string)
                        delta = text[len(fullContent):]
                    }
                    
                    if delta != "" {
                        fullContent += delta
                        
                        // 转换为 OpenAI SSE 格式
                        sseData := map[string]interface{}{
                            "id": requestID,
                            "object": "chat.completion.chunk",
                            "created": time.Now().Unix(),
                            "model": "gemma4:e4b",
                            "choices": []map[string]interface{}{{
                                "index": 0,
                                "delta": map[string]interface{}{
                                    "content": delta,
                                },
                                "finish_reason": nil,
                            }},
                        }
                        
                        jsonData, _ := json.Marshal(sseData)
                        c.Writer.Write([]byte(fmt.Sprintf("data: %s\n\n", jsonData)))
                        flusher.Flush()
                        
                        log.Printf("💬 [ChatStream] 实时输出: %s", delta)
                    }
                    
                    // 检查是否结束
                    if payload["state"] == "final" {
                        // 发送 [DONE]
                        c.Writer.Write([]byte("data: [DONE]\n\n"))
                        flusher.Flush()
                        log.Printf("✅ [ChatStream] 完成")
                        return
                    }
                }
            }
            
        case err := <-errorChan:
            log.Printf("❌ [ChatStream] 错误: %v", err)
            return
            
        case <-time.After(60 * time.Second):
            log.Printf("⏰ [ChatStream] 超时")
            return
        }
    }
}
```

---

## 🔄 生命周期管理

### 场景 1：正常请求流程

```
1. 用户发送消息
   POST /api/chat/stream
   {"message": "你好", "agent_id": "main"}
   
2. Scheduler 查找 Agent 映射
   AgentMap["main"] = {PodIP: "10.1.0.203", SessionKey: "xxx"}
   
3. 获取 WebSocket 连接（复用）
   wsPool.GetConn("10.1.0.203")  → 复用已有连接
   
4. 发送消息（带 sessionKey）
   {
     "type": "req",
     "id": "req-123",
     "method": "agent.message",
     "params": {
       "sessionKey": "xxx",
       "message": "你好"
     }
   }
   
5. 实时接收事件
   {
     "type": "event",
     "event": "chat",
     "payload": {
       "sessionKey": "xxx",
       "role": "assistant",
       "delta": "你"
     }
   }
   → 转换为 OpenAI SSE 格式
   → 立即输出 ✅
   
6. 完成
   {
     "type": "event",
     "event": "chat",
     "payload": {
       "sessionKey": "xxx",
       "state": "final"
     }
   }
   → 发送 [DONE]
```

### 场景 2：WebSocket 断开重连

```
1. Pod 重启或网络故障
   WebSocket 连接断开
   
2. Scheduler 检测到断开
   monitorConnection() 捕获错误
   → 从连接池删除
   
3. 下次请求自动重连
   wsPool.GetConn("10.1.0.203")
   → 检测连接无效
   → 自动创建新连接
   → 重新握手
   
4. 请求照常处理
   无需用户感知 ✅
```

### 场景 3：Pod 缩容

```
1. K8s 删除 Pod-3 (10.1.0.212)
   
2. Scheduler 检测到 WebSocket 断开
   monitorConnection() → 从连接池删除
   
3. 该 Pod 上的 Agent 重新分配
   allocatePod("agent-007")
   → 检测到原 Pod 不可用
   → 分配到新 Pod (10.1.0.203)
   → 创建新连接
   
4. 恢复 Agent 状态（如果需要）
   可能需要从数据库加载 Agent 配置
```

---

## 🎯 优势总结

### vs HTTP SSE（原方案）

| 维度 | HTTP SSE | WebSocket (方案 B) |
|------|---------|-------------------|
| **连接方式** | 每次请求新建 | 复用长连接 ✅ |
| **性能** | 频繁握手 | 握手一次，复用 ✅ |
| **实时性** | 聚合输出 ❌ | 实时流式 ✅ |
| **复杂度** | 简单 | 中等（需要连接池） |
| **源码修改** | 需要 ❌ | 完全不需要 ✅ |

### 关键优势

1. ✅ **完全不修改 OpenClaw 源码** - 消除升级风险
2. ✅ **真正的实时流式** - 复用 Control UI 的能力
3. ✅ **性能更好** - 连接复用，减少握手
4. ✅ **架构清晰** - 直接监听事件，逻辑简单
5. ✅ **K8s 无影响** - 不需要修改任何 K8s 配置（包括 Service）

---

## 📋 实施计划

### Phase 1：WebSocket 连接池（1 天）
- [ ] 实现 `websocket/pool.go`
- [ ] 连接创建、复用、断开处理
- [ ] 心跳保活
- [ ] 单元测试

### Phase 2：改造 ChatStream（1 天）
- [ ] 重构 `api.go` 的 `ChatStream` 函数
- [ ] 实现事件监听和转发
- [ ] OpenAI SSE 格式转换
- [ ] 本地测试

### Phase 3：生产验证（1 天）
- [ ] 部署到 K8s
- [ ] 端到端测试
- [ ] 压力测试（并发、断线重连）
- [ ] 监控指标

### Phase 4：文档和清理（0.5 天）
- [ ] 更新部署文档
- [ ] 添加监控指标
- [ ] 清理旧的 HTTP SSE 代码（可选）

**总计：3.5 天**

---

## ❓ 还有疑问吗？

请告诉我您还有什么疑问，我们继续深入讨论！
