# 方案 B 分析：WebSocket 架构影响评估

## 📋 当前源码修改情况

### 已修改文件
```bash
M src/gateway/http-common.ts    # 添加了 socket.setNoDelay(true)
M src/gateway/openai-http.ts    # 优化了 writeSse 函数
```

### 修改内容
```typescript
// http-common.ts
export function setSseHeaders(res: ServerResponse) {
  res.setHeader("X-Accel-Buffering", "no"); // 新增
  if (res.socket) {
    res.socket.setNoDelay(true);              // 新增
  }
}

// openai-http.ts
function writeSse(res: ServerResponse, data: unknown) {
  res.write(`data: ${JSON.stringify(data)}\n\n`);
  if (res.socket) {
    res.socket.setNoDelay(true);              // 新增
  }
}
```

### ⚠️ 升级风险
**高风险**：
- OpenClaw 更新时，这些文件很可能被覆盖
- 需要手动 merge 我们的修改
- 如果 OpenClaw 重构了这部分代码，可能导致不兼容

**推荐**：避免修改 OpenClaw 源码！

---

## 🎯 方案 B：WebSocket 替代 HTTP SSE

### 核心思路
```
Scheduler (Go)
  ↓ WebSocket 连接
  ws://openclaw-pod-ip:18789
  ↓
OpenClaw Gateway (WebSocket 接口)
  ↓ 实时 broadcast
Agent 事件
```

**关键点**：复用 Control UI 的 WebSocket 接口，无需修改 OpenClaw 源码！

---

## 📊 K8s 架构影响分析

### 1️⃣ 网络层影响

#### 当前架构（HTTP）
```yaml
# Scheduler → OpenClaw
protocol: HTTP/1.1
connection: 短连接（每次请求新建）
port: 18789 (ClusterIP)
load_balance: Kubernetes Service (Round-robin)
```

#### 方案 B（WebSocket）
```yaml
# Scheduler → OpenClaw
protocol: WebSocket (HTTP Upgrade)
connection: 长连接（持久化）
port: 18789 (ClusterIP，同一端口)
load_balance: ⚠️ 需要调整策略
```

**影响评估**：
- ✅ **端口无需变化**：WebSocket 使用同一端口（18789）
- ⚠️ **连接方式变化**：从短连接变为长连接
- ⚠️ **负载均衡策略**：需要考虑会话亲和性

---

### 2️⃣ Service 配置影响

#### 当前 Service
```yaml
apiVersion: v1
kind: Service
metadata:
  name: openclaw-pool
spec:
  selector:
    app: openclaw-pool
  ports:
    - port: 18789
      targetPort: 18789
  type: ClusterIP
  sessionAffinity: None  # 默认 Round-robin
```

#### 方案 B 推荐配置
```yaml
apiVersion: v1
kind: Service
metadata:
  name: openclaw-pool
spec:
  selector:
    app: openclaw-pool
  ports:
    - port: 18789
      targetPort: 18789
  type: ClusterIP
  sessionAffinity: ClientIP  # ⚠️ 需要调整为 ClientIP 亲和
  sessionAffinityConfig:
    clientIP:
      timeoutSeconds: 3600  # WebSocket 保持 1 小时
```

**影响评估**：
- ✅ **配置简单**：只需添加 `sessionAffinity: ClientIP`
- ✅ **向后兼容**：不影响现有 HTTP 请求
- ⚠️ **负载均衡**：同一 IP 的请求会路由到同一 Pod

---

### 3️⃣ Scheduler 代码影响

#### 当前代码（HTTP）
```go
// 每次请求新建 HTTP 连接
resp, err := client.Do(httpReq)
defer resp.Body.Close()
```

#### 方案 B 代码（WebSocket）
```go
// 1. 建立 WebSocket 连接池
type WebSocketPool struct {
    conns map[string]*websocket.Conn // podIP -> conn
    mu    sync.RWMutex
}

// 2. 获取或创建连接
func (p *WebSocketPool) GetConn(podIP string) (*websocket.Conn, error) {
    p.mu.RLock()
    if conn, ok := p.conns[podIP]; ok && conn != nil {
        p.mu.RUnlock()
        return conn, nil
    }
    p.mu.RUnlock()
    
    // 创建新连接
    p.mu.Lock()
    defer p.mu.Unlock()
    
    url := fmt.Sprintf("ws://%s:18789", podIP)
    conn, _, err := websocket.DefaultDialer.Dial(url, nil)
    if err != nil {
        return nil, err
    }
    
    p.conns[podIP] = conn
    return conn, nil
}

// 3. 发送消息并监听响应
func ChatStream(c *gin.Context) {
    podIP := allocatePod(agentID)
    conn, err := wsPool.GetConn(podIP)
    
    // 发送聊天请求
    requestID := generateUUID()
    err = conn.WriteJSON(map[string]interface{}{
        "type": "req",
        "id": requestID,
        "method": "agent.message",
        "params": map[string]interface{}{
            "sessionKey": sessionKey,
            "message": req.Message,
            "agentId": req.AgentID,
        },
    })
    
    // 监听响应（实时流式）
    for {
        var frame map[string]interface{}
        err := conn.ReadJSON(&frame)
        
        if frame["type"] == "event" && frame["event"] == "chat" {
            payload := frame["payload"].(map[string]interface{})
            
            // 转换为 OpenAI SSE 格式
            if payload["role"] == "assistant" && payload["delta"] != nil {
                sseData := map[string]interface{}{
                    "id": requestID,
                    "object": "chat.completion.chunk",
                    "choices": []map[string]interface{}{{
                        "delta": map[string]interface{}{
                            "content": payload["delta"],
                        },
                        "finish_reason": nil,
                    }},
                }
                
                // 写入 SSE
                c.Writer.Write([]byte(fmt.Sprintf("data: %s\n\n", toJSON(sseData))))
                flusher.Flush()
            }
            
            if payload["state"] == "final" {
                break
            }
        }
    }
}
```

**影响评估**：
- ⚠️ **代码改动较大**：需要重构 `ChatStream` 函数（约 200 行）
- ✅ **逻辑更清晰**：直接监听事件，而不是解析 HTTP 流
- ✅ **性能更好**：复用长连接，减少握手开销

---

### 4️⃣ 扩容/缩容影响

#### 场景 A：Pod 扩容
```
初始: 3 个 Pod
  Pod-1: Scheduler 有 5 个 WebSocket 连接
  Pod-2: Scheduler 有 3 个 WebSocket 连接
  Pod-3: Scheduler 有 2 个 WebSocket 连接

扩容: 增加到 4 个 Pod
  Pod-4: 新 Pod，Scheduler 尚未建立连接
  
✅ 影响：新请求会自动分配到 Pod-4
✅ 处理：Scheduler 按需建立新连接
```

#### 场景 B：Pod 缩容
```
初始: 3 个 Pod
  Pod-3: 即将被删除

缩容: 删除 Pod-3
  Scheduler 检测到 WebSocket 断开
  
⚠️ 影响：正在使用 Pod-3 的请求会中断
✅ 处理：Scheduler 自动重连到其他 Pod
```

**推荐策略**：
```go
// WebSocket 断开自动重连
func (p *WebSocketPool) handleDisconnect(podIP string) {
    p.mu.Lock()
    delete(p.conns, podIP)
    p.mu.Unlock()
    
    log.Printf("Pod %s WebSocket 断开，将重新分配", podIP)
}

// 在读取时检测断开
for {
    err := conn.ReadJSON(&frame)
    if err != nil {
        wsPool.handleDisconnect(podIP)
        // 重新分配 Pod 并建立连接
        newPodIP := allocatePod(agentID)
        conn, _ = wsPool.GetConn(newPodIP)
        continue
    }
}
```

---

### 5️⃣ 资源消耗影响

#### HTTP 短连接
```
每次请求:
  - 建立 TCP 连接: 3-way handshake
  - HTTP 请求/响应
  - 关闭连接: 4-way handshake
  
资源消耗: 高（频繁建立/销毁连接）
并发支持: 好（无状态）
```

#### WebSocket 长连接
```
每个 Agent:
  - 建立 1 次 WebSocket 连接
  - 持续使用（心跳保活）
  - 断开时重连
  
资源消耗: 低（复用连接）
并发支持: 需要连接池管理
```

**影响评估**：
- ✅ **CPU 消耗降低**：减少 TCP 握手次数
- ⚠️ **内存消耗增加**：需要维护连接池（每 Pod 约 1-2 MB）
- ✅ **网络延迟降低**：无需重复握手

---

### 6️⃣ 监控/日志影响

#### 当前监控（HTTP）
```
指标:
  - http_request_duration_seconds
  - http_requests_total
  - http_request_size_bytes
  
日志:
  [Scheduler] POST /api/chat/stream -> 200 (12s)
```

#### 方案 B 监控（WebSocket）
```
指标:
  - websocket_connections_active
  - websocket_messages_sent_total
  - websocket_messages_received_total
  - websocket_reconnects_total
  
日志:
  [Scheduler] WebSocket connected: 10.1.0.203
  [Scheduler] Received event: chat (assistant delta)
  [Scheduler] WebSocket disconnected: 10.1.0.203 (reconnecting...)
```

**影响评估**：
- ⚠️ **监控指标变化**：需要更新 Prometheus 抓取规则
- ✅ **日志更详细**：可以看到实时事件流
- ⚠️ **调试复杂度增加**：长连接状态需要专门监控

---

## 🎯 综合评估

### ✅ 优点
1. **无需修改 OpenClaw 源码** - 避免升级冲突 ✅
2. **真正的流式输出** - 复用 Control UI 的实时能力 ✅
3. **性能更好** - 减少 TCP 握手开销 ✅
4. **架构简洁** - 直接监听事件，逻辑清晰 ✅

### ⚠️ 缺点
1. **Scheduler 代码改动较大** - 需要重构约 200 行代码
2. **连接管理复杂** - 需要维护连接池和心跳
3. **负载均衡调整** - 需要启用 ClientIP 亲和
4. **监控指标变化** - 需要更新监控配置

### 🚨 风险
| 风险 | 等级 | 缓解措施 |
|------|------|---------|
| WebSocket 连接不稳定 | 中 | 实现自动重连机制 |
| Pod 缩容时连接中断 | 中 | PreStop Hook + 优雅关闭 |
| 负载不均衡 | 低 | 合理设置 sessionAffinity 超时 |
| 内存泄漏（连接池） | 低 | 定期清理闲置连接 |

---

## 📋 实施方案

### Phase 1：基础实现（1-2 天）
- [ ] Scheduler 实现 WebSocket 连接池
- [ ] 实现消息收发逻辑
- [ ] OpenAI SSE 格式转换
- [ ] 本地测试验证

### Phase 2：容错处理（1 天）
- [ ] 自动重连机制
- [ ] 心跳保活
- [ ] 连接池管理（清理闲置连接）
- [ ] 错误处理和降级

### Phase 3：生产部署（1 天）
- [ ] 更新 Service 配置（sessionAffinity）
- [ ] 更新监控指标
- [ ] 压力测试
- [ ] 灰度发布

### Phase 4：优化（可选）
- [ ] 连接池性能优化
- [ ] 多协程并发处理
- [ ] 指标和告警完善

---

## 🎯 结论

### 对 K8s 架构的影响：**可控且可接受**

| 维度 | 影响程度 | 说明 |
|------|---------|------|
| 网络配置 | 低 | 只需添加 sessionAffinity |
| 资源消耗 | 低 | 内存略增（<5%），CPU 降低 |
| 扩展性 | 低 | 自动适配扩缩容 |
| 稳定性 | 中 | 需要实现重连机制 |
| 复杂度 | 中 | 代码改动约 200 行 |

### 推荐：✅ 采用方案 B

**理由**：
1. ✅ **避免修改 OpenClaw 源码** - 消除升级风险
2. ✅ **真正解决流式问题** - 实时输出，用户体验好
3. ✅ **K8s 影响可控** - 配置简单，风险可管理
4. ✅ **长期收益高** - 性能更好，架构更清晰

### 下一步
如果您同意，我可以立即开始实施：
1. 先在 Scheduler 中实现 WebSocket 客户端
2. 本地测试验证流式输出
3. 部署到 K8s 并压力测试

要开始吗？
