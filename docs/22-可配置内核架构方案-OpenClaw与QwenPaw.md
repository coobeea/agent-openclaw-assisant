# 可配置内核架构方案：OpenClaw 与 QwenPaw

> **设计目标**：让系统支持配置不同的"内核"（OpenClaw 或 QwenPaw），实现灵活切换。

---

## 1. 两大内核对比分析

### 1.1 OpenClaw

**核心特性：**
- **语言**：Node.js/TypeScript
- **通信协议**：WebSocket（`ws://`）
- **流式输出**：WebSocket events（`event: "chat"`, `state: "delta"`）
- **认证**：Token-based (`connect.challenge` handshake)
- **架构**：Gateway + Control UI + Channels
- **API 端点**：WebSocket RPC（`method: "chat.send"`）
- **优势**：
  - 原生 WebSocket，实时性强
  - 官方活跃开发，生态完整
  - Control UI 功能丰富

**核心代码：**
```typescript
// OpenClaw Gateway WebSocket RPC
{
  "type": "req",
  "method": "chat.send",
  "id": "request-123",
  "params": {
    "message": "Hello",
    "sessionKey": "agent:main:session-456",
    "idempotencyKey": "idem-789"
  }
}

// Response Events
{
  "type": "event",
  "event": "chat",
  "payload": {
    "sessionKey": "agent:main:session-456",
    "state": "delta",
    "message": {
      "content": [{"text": "Hello, "}]
    }
  }
}
```

### 1.2 QwenPaw

**核心特性：**
- **语言**：Python
- **通信协议**：HTTP RESTful + SSE（`text/event-stream`）
- **流式输出**：Server-Sent Events（SSE）
- **认证**：HTTP Bearer Token / Basic Auth
- **架构**：FastAPI + AgentScope + MultiAgentManager
- **API 端点**：HTTP POST `/api/console/chat`
- **优势**：
  - Python 生态，AI/ML 库丰富
  - FastAPI 高性能，异步支持
  - AgentScope 框架，多智能体协作

**核心代码：**
```python
# QwenPaw FastAPI Endpoint
@router.post("/console/chat")
async def post_console_chat(
    request_data: AgentRequest,
    request: Request,
) -> StreamingResponse:
    # ... 处理逻辑 ...
    
    async def event_generator():
        async for event_data in stream_it:
            yield event_data  # SSE format: data: {...}\n\n
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
    )
```

---

## 2. 可配置内核架构设计

### 2.1 整体架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                        Frontend (Vue3)                          │
│                     http://localhost:30000                      │
│                                                                 │
│  • 发送: POST /api/chat/stream                                  │
│  • 接收: SSE (text/event-stream)                                │
└────────────────────────────┬────────────────────────────────────┘
                             │ HTTP + SSE
                             ↓
┌─────────────────────────────────────────────────────────────────┐
│                    Scheduler (Go - 调度器)                      │
│                      localhost:30080                            │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │           Kernel Abstraction Layer (抽象层)             │  │
│  │                                                          │  │
│  │   • KernelInterface (接口定义)                           │  │
│  │   • KernelFactory (工厂模式)                             │  │
│  │   • KernelConfig (配置管理)                              │  │
│  └──────────────────────────────────────────────────────────┘  │
│                             │                                   │
│          ┌──────────────────┴──────────────────┐                │
│          ↓                                     ↓                │
│  ┌──────────────────┐               ┌──────────────────┐       │
│  │  OpenClawAdapter │               │  QwenPawAdapter  │       │
│  │                  │               │                  │       │
│  │  • WebSocket池   │               │  • HTTP Client   │       │
│  │  • RPC调用       │               │  • SSE解析       │       │
│  │  • 事件解析      │               │  • JSON处理      │       │
│  └──────────────────┘               └──────────────────┘       │
└────────────────────────────────────────────────────────────────┘
            │                                     │
            ↓ WebSocket                          ↓ HTTP + SSE
┌─────────────────────────┐       ┌─────────────────────────────┐
│   OpenClaw Gateway      │       │    QwenPaw FastAPI         │
│   (Node.js/TypeScript)  │       │    (Python/AgentScope)     │
│                         │       │                            │
│ • ws://pod-ip:3000      │       │ • http://pod-ip:8088       │
│ • WebSocket RPC         │       │ • HTTP POST + SSE          │
│ • chat.send method      │       │ • /api/console/chat        │
└─────────────────────────┘       └─────────────────────────────┘
```

### 2.2 核心接口定义（Go）

```go
// internal/kernel/interface.go

package kernel

import (
	"context"
	"io"
)

// KernelInterface 定义内核统一接口
type KernelInterface interface {
	// 初始化内核连接
	Initialize(ctx context.Context, config *KernelConfig) error
	
	// 发送消息并获取流式响应
	StreamChat(ctx context.Context, req *ChatRequest) (<-chan ChatEvent, error)
	
	// 创建 Agent
	CreateAgent(ctx context.Context, agentID, workspace string) error
	
	// 启动 Agent
	StartAgent(ctx context.Context, agentID string) error
	
	// 停止 Agent
	StopAgent(ctx context.Context, agentID string) error
	
	// 健康检查
	HealthCheck(ctx context.Context) error
	
	// 关闭连接
	Close() error
}

// ChatRequest 统一的聊天请求格式
type ChatRequest struct {
	AgentID     string            `json:"agent_id"`
	SessionKey  string            `json:"session_key"`
	Message     string            `json:"message"`
	UserID      string            `json:"user_id,omitempty"`
	Context     map[string]string `json:"context,omitempty"`
}

// ChatEvent 统一的聊天事件格式
type ChatEvent struct {
	Type      string `json:"type"`      // "delta", "done", "error"
	Content   string `json:"content"`   // 增量内容
	SessionKey string `json:"session_key"`
	Error     string `json:"error,omitempty"`
}

// KernelConfig 内核配置
type KernelConfig struct {
	Type       string            `json:"type"`        // "openclaw" | "qwenpaw"
	Endpoint   string            `json:"endpoint"`    // Pod IP:Port
	Auth       *AuthConfig       `json:"auth"`
	Timeout    int               `json:"timeout"`     // 秒
	Extra      map[string]string `json:"extra"`       // 扩展配置
}

// AuthConfig 认证配置
type AuthConfig struct {
	Type   string `json:"type"`   // "token" | "basic" | "none"
	Token  string `json:"token,omitempty"`
	User   string `json:"user,omitempty"`
	Pass   string `json:"pass,omitempty"`
}
```

### 2.3 OpenClawAdapter 实现

```go
// internal/kernel/adapters/openclaw.go

package adapters

import (
	"context"
	"encoding/json"
	"fmt"
	"github.com/gorilla/websocket"
	"openclaw-scheduler/internal/kernel"
	"sync"
	"time"
)

type OpenClawAdapter struct {
	config *kernel.KernelConfig
	conn   *websocket.Conn
	mu     sync.RWMutex
	
	// WebSocket 连接池
	connPool map[string]*websocket.Conn
}

func NewOpenClawAdapter() *OpenClawAdapter {
	return &OpenClawAdapter{
		connPool: make(map[string]*websocket.Conn),
	}
}

func (a *OpenClawAdapter) Initialize(ctx context.Context, config *kernel.KernelConfig) error {
	a.config = config
	
	// 建立 WebSocket 连接
	wsURL := fmt.Sprintf("ws://%s/gateway", config.Endpoint)
	
	dialer := websocket.Dialer{
		HandshakeTimeout: time.Duration(config.Timeout) * time.Second,
	}
	
	conn, _, err := dialer.Dial(wsURL, nil)
	if err != nil {
		return fmt.Errorf("WebSocket 连接失败: %w", err)
	}
	
	a.conn = conn
	
	// 执行 OpenClaw 的 connect.challenge 握手
	if err := a.performHandshake(); err != nil {
		conn.Close()
		return fmt.Errorf("握手失败: %w", err)
	}
	
	return nil
}

func (a *OpenClawAdapter) performHandshake() error {
	// 1. 等待 connect.challenge
	var challengeFrame map[string]interface{}
	if err := a.conn.ReadJSON(&challengeFrame); err != nil {
		return fmt.Errorf("读取 challenge 失败: %w", err)
	}
	
	if challengeFrame["event"] != "connect.challenge" {
		return fmt.Errorf("期望 connect.challenge，收到: %v", challengeFrame["event"])
	}
	
	// 2. 发送 connect 请求
	nonce := challengeFrame["payload"].(map[string]interface{})["nonce"].(string)
	
	connectReq := map[string]interface{}{
		"type":   "req",
		"method": "connect",
		"id":     generateRequestID(),
		"params": map[string]interface{}{
			"nonce":       nonce,
			"minProtocol": 1,
			"maxProtocol": 1,
			"client": map[string]interface{}{
				"id":       "gateway-client",
				"mode":     "backend",
				"version":  "1.0.0",
				"platform": "linux",
			},
			"role":   "operator",
			"scopes": []string{"operator.admin"},
			"caps":   []string{},
			"auth": map[string]interface{}{
				"token": a.config.Auth.Token,
			},
		},
	}
	
	if err := a.conn.WriteJSON(connectReq); err != nil {
		return fmt.Errorf("发送 connect 请求失败: %w", err)
	}
	
	// 3. 等待 connect 响应
	var connectRes map[string]interface{}
	if err := a.conn.ReadJSON(&connectRes); err != nil {
		return fmt.Errorf("读取 connect 响应失败: %w", err)
	}
	
	if connectRes["type"] == "res" && connectRes["ok"] == true {
		return nil
	}
	
	return fmt.Errorf("连接被拒绝: %v", connectRes)
}

func (a *OpenClawAdapter) StreamChat(ctx context.Context, req *kernel.ChatRequest) (<-chan kernel.ChatEvent, error) {
	eventChan := make(chan kernel.ChatEvent, 10)
	
	// 发送 chat.send 请求
	requestID := generateRequestID()
	chatReq := map[string]interface{}{
		"type":   "req",
		"method": "chat.send",
		"id":     requestID,
		"params": map[string]interface{}{
			"message":        req.Message,
			"sessionKey":     fmt.Sprintf("agent:main:%s", req.SessionKey),
			"idempotencyKey": generateRequestID(),
		},
	}
	
	if err := a.conn.WriteJSON(chatReq); err != nil {
		close(eventChan)
		return nil, fmt.Errorf("发送聊天请求失败: %w", err)
	}
	
	// 异步监听响应
	go func() {
		defer close(eventChan)
		
		for {
			select {
			case <-ctx.Done():
				return
			default:
				var frame map[string]interface{}
				if err := a.conn.ReadJSON(&frame); err != nil {
					eventChan <- kernel.ChatEvent{
						Type:  "error",
						Error: err.Error(),
					}
					return
				}
				
				// 处理事件帧
				if frame["type"] == "event" && frame["event"] == "chat" {
					payload := frame["payload"].(map[string]interface{})
					state := payload["state"].(string)
					
					if state == "delta" {
						// 提取增量内容
						content := extractContent(payload)
						eventChan <- kernel.ChatEvent{
							Type:       "delta",
							Content:    content,
							SessionKey: req.SessionKey,
						}
					} else if state == "done" {
						eventChan <- kernel.ChatEvent{
							Type:       "done",
							SessionKey: req.SessionKey,
						}
						return
					}
				}
			}
		}
	}()
	
	return eventChan, nil
}

func (a *OpenClawAdapter) CreateAgent(ctx context.Context, agentID, workspace string) error {
	// 执行 agents add 命令（通过 exec 或 API）
	// 实现省略...
	return nil
}

func (a *OpenClawAdapter) HealthCheck(ctx context.Context) error {
	// 发送 ping 或健康检查 RPC
	return nil
}

func (a *OpenClawAdapter) Close() error {
	if a.conn != nil {
		return a.conn.Close()
	}
	return nil
}

// extractContent 从 payload 中提取文本内容
func extractContent(payload map[string]interface{}) string {
	if msg, ok := payload["message"].(map[string]interface{}); ok {
		if content, ok := msg["content"].([]interface{}); ok && len(content) > 0 {
			if textBlock, ok := content[0].(map[string]interface{}); ok {
				if text, ok := textBlock["text"].(string); ok {
					return text
				}
			}
		}
	}
	return ""
}

func generateRequestID() string {
	return fmt.Sprintf("req-%d", time.Now().UnixNano())
}
```

### 2.4 QwenPawAdapter 实现

```go
// internal/kernel/adapters/qwenpaw.go

package adapters

import (
	"bufio"
	"context"
	"encoding/json"
	"fmt"
	"net/http"
	"openclaw-scheduler/internal/kernel"
	"strings"
	"time"
)

type QwenPawAdapter struct {
	config *kernel.KernelConfig
	client *http.Client
}

func NewQwenPawAdapter() *QwenPawAdapter {
	return &QwenPawAdapter{
		client: &http.Client{
			Timeout: 0, // 无限超时（SSE）
		},
	}
}

func (a *QwenPawAdapter) Initialize(ctx context.Context, config *kernel.KernelConfig) error {
	a.config = config
	
	// 验证连接（可选）
	healthURL := fmt.Sprintf("http://%s/api/version", config.Endpoint)
	resp, err := a.client.Get(healthURL)
	if err != nil {
		return fmt.Errorf("QwenPaw 连接失败: %w", err)
	}
	defer resp.Body.Close()
	
	if resp.StatusCode != 200 {
		return fmt.Errorf("QwenPaw 健康检查失败: %d", resp.StatusCode)
	}
	
	return nil
}

func (a *QwenPawAdapter) StreamChat(ctx context.Context, req *kernel.ChatRequest) (<-chan kernel.ChatEvent, error) {
	eventChan := make(chan kernel.ChatEvent, 10)
	
	// 构造 QwenPaw 请求
	qwenReq := map[string]interface{}{
		"sender_id": req.UserID,
		"content_parts": []map[string]interface{}{
			{
				"type": "text",
				"text": req.Message,
			},
		},
		"meta": map[string]string{
			"session_id": req.SessionKey,
			"user_id":    req.UserID,
		},
	}
	
	payload, _ := json.Marshal(qwenReq)
	chatURL := fmt.Sprintf("http://%s/api/console/chat", a.config.Endpoint)
	
	httpReq, err := http.NewRequestWithContext(ctx, "POST", chatURL, strings.NewReader(string(payload)))
	if err != nil {
		close(eventChan)
		return nil, fmt.Errorf("创建请求失败: %w", err)
	}
	
	httpReq.Header.Set("Content-Type", "application/json")
	httpReq.Header.Set("X-Agent-Id", req.AgentID)
	if a.config.Auth != nil && a.config.Auth.Token != "" {
		httpReq.Header.Set("Authorization", fmt.Sprintf("Bearer %s", a.config.Auth.Token))
	}
	
	// 发送请求并处理 SSE 流
	go func() {
		defer close(eventChan)
		
		resp, err := a.client.Do(httpReq)
		if err != nil {
			eventChan <- kernel.ChatEvent{
				Type:  "error",
				Error: fmt.Sprintf("请求失败: %v", err),
			}
			return
		}
		defer resp.Body.Close()
		
		if resp.StatusCode != 200 {
			eventChan <- kernel.ChatEvent{
				Type:  "error",
				Error: fmt.Sprintf("HTTP %d", resp.StatusCode),
			}
			return
		}
		
		// 解析 SSE 流
		scanner := bufio.NewScanner(resp.Body)
		for scanner.Scan() {
			line := scanner.Text()
			
			if !strings.HasPrefix(line, "data: ") {
				continue
			}
			
			data := strings.TrimPrefix(line, "data: ")
			if data == "[DONE]" {
				eventChan <- kernel.ChatEvent{
					Type:       "done",
					SessionKey: req.SessionKey,
				}
				return
			}
			
			// 解析事件
			var sseEvent map[string]interface{}
			if err := json.Unmarshal([]byte(data), &sseEvent); err != nil {
				continue
			}
			
			// 提取增量内容
			if content, ok := sseEvent["content"].(string); ok && content != "" {
				eventChan <- kernel.ChatEvent{
					Type:       "delta",
					Content:    content,
					SessionKey: req.SessionKey,
				}
			}
		}
	}()
	
	return eventChan, nil
}

func (a *QwenPawAdapter) CreateAgent(ctx context.Context, agentID, workspace string) error {
	// QwenPaw 通过配置文件管理 Agent，无需运行时创建
	return nil
}

func (a *QwenPawAdapter) HealthCheck(ctx context.Context) error {
	healthURL := fmt.Sprintf("http://%s/api/version", a.config.Endpoint)
	resp, err := a.client.Get(healthURL)
	if err != nil {
		return err
	}
	defer resp.Body.Close()
	
	if resp.StatusCode == 200 {
		return nil
	}
	return fmt.Errorf("health check failed: %d", resp.StatusCode)
}

func (a *QwenPawAdapter) Close() error {
	// HTTP Client 无需手动关闭
	return nil
}
```

### 2.5 工厂模式（Factory）

```go
// internal/kernel/factory.go

package kernel

import (
	"fmt"
	"openclaw-scheduler/internal/kernel/adapters"
)

// KernelFactory 内核工厂
type KernelFactory struct{}

func NewKernelFactory() *KernelFactory {
	return &KernelFactory{}
}

// CreateKernel 根据配置创建对应的内核适配器
func (f *KernelFactory) CreateKernel(config *KernelConfig) (KernelInterface, error) {
	switch config.Type {
	case "openclaw":
		return adapters.NewOpenClawAdapter(), nil
	case "qwenpaw":
		return adapters.NewQwenPawAdapter(), nil
	default:
		return nil, fmt.Errorf("未知的内核类型: %s", config.Type)
	}
}
```

### 2.6 Scheduler 改造（ChatStream）

```go
// internal/api/api.go (改造后)

func ChatStream(c *gin.Context) {
	var req models.ChatRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(400, gin.H{"error": err.Error()})
		return
	}
	
	// 1. 分配容器
	container, err := k8s.AllocateContainer("openclaw")
	if err != nil {
		c.JSON(503, gin.H{"error": "没有可用的容器"})
		return
	}
	defer k8s.ReleaseContainer(container.PodName)
	
	// 2. 从配置中获取内核类型
	kernelType := os.Getenv("KERNEL_TYPE") // "openclaw" | "qwenpaw"
	if kernelType == "" {
		kernelType = "openclaw" // 默认
	}
	
	// 3. 创建内核配置
	kernelConfig := &kernel.KernelConfig{
		Type:     kernelType,
		Endpoint: fmt.Sprintf("%s:3000", container.PodIP), // OpenClaw 端口
		Auth: &kernel.AuthConfig{
			Type:  "token",
			Token: "openclaw-internal-k8s-token",
		},
		Timeout: 60,
	}
	
	// 根据内核类型调整配置
	if kernelType == "qwenpaw" {
		kernelConfig.Endpoint = fmt.Sprintf("%s:8088", container.PodIP) // QwenPaw 端口
		kernelConfig.Auth.Type = "none" // QwenPaw 可能不需要认证
	}
	
	// 4. 创建内核适配器
	factory := kernel.NewKernelFactory()
	kernelAdapter, err := factory.CreateKernel(kernelConfig)
	if err != nil {
		c.JSON(500, gin.H{"error": fmt.Sprintf("创建内核失败: %v", err)})
		return
	}
	defer kernelAdapter.Close()
	
	// 5. 初始化连接
	ctx := c.Request.Context()
	if err := kernelAdapter.Initialize(ctx, kernelConfig); err != nil {
		c.JSON(500, gin.H{"error": fmt.Sprintf("初始化失败: %v", err)})
		return
	}
	
	// 6. 设置 SSE 响应头（前端始终是 SSE）
	c.Header("Content-Type", "text/event-stream")
	c.Header("Cache-Control", "no-cache")
	c.Header("Connection", "keep-alive")
	c.Header("X-Accel-Buffering", "no")
	c.Status(http.StatusOK)
	
	flusher, ok := c.Writer.(http.Flusher)
	if !ok {
		c.JSON(500, gin.H{"error": "不支持流式输出"})
		return
	}
	
	// 发送初始事件（flush headers）
	fmt.Fprintf(c.Writer, ": connected\n\n")
	flusher.Flush()
	
	// 7. 发送聊天请求
	chatReq := &kernel.ChatRequest{
		AgentID:    req.AgentID,
		SessionKey: req.SessionKey,
		Message:    req.Content,
		UserID:     req.UserID,
	}
	
	eventChan, err := kernelAdapter.StreamChat(ctx, chatReq)
	if err != nil {
		fmt.Fprintf(c.Writer, "data: {\"type\":\"error\",\"content\":\"%s\"}\n\n", err.Error())
		flusher.Flush()
		return
	}
	
	// 8. 监听事件流并转换为 SSE 格式
	for event := range eventChan {
		switch event.Type {
		case "delta":
			// 增量内容
			sseData := map[string]interface{}{
				"type":    "delta",
				"content": event.Content,
				"model":   kernelType, // 标识内核类型
			}
			jsonBytes, _ := json.Marshal(sseData)
			fmt.Fprintf(c.Writer, "data: %s\n\n", string(jsonBytes))
			flusher.Flush()
			
		case "done":
			// 完成
			fmt.Fprintf(c.Writer, "data: [DONE]\n\n")
			flusher.Flush()
			return
			
		case "error":
			// 错误
			fmt.Fprintf(c.Writer, "data: {\"type\":\"error\",\"content\":\"%s\"}\n\n", event.Error)
			flusher.Flush()
			return
		}
	}
}
```

---

## 3. 配置系统

### 3.1 环境变量配置

```yaml
# k8s-manifests/05-scheduler.yaml

apiVersion: v1
kind: ConfigMap
metadata:
  name: scheduler-config
  namespace: openclaw
data:
  KERNEL_TYPE: "openclaw"  # 或 "qwenpaw"
  KERNEL_OPENCLAW_AUTH_TOKEN: "openclaw-internal-k8s-token"
  KERNEL_QWENPAW_AUTH_TYPE: "none"
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: openclaw-scheduler
  namespace: openclaw
spec:
  template:
    spec:
      containers:
      - name: scheduler
        image: openclaw-scheduler:configurable-kernel
        envFrom:
        - configMapRef:
            name: scheduler-config
```

### 3.2 动态切换（运行时）

```go
// 支持通过 HTTP Header 动态指定内核
func ChatStream(c *gin.Context) {
	// 优先从请求头获取
	kernelType := c.GetHeader("X-Kernel-Type")
	if kernelType == "" {
		kernelType = os.Getenv("KERNEL_TYPE")
	}
	if kernelType == "" {
		kernelType = "openclaw" // 默认
	}
	
	// ... 后续逻辑 ...
}
```

**前端调用示例：**
```javascript
// 使用 OpenClaw
fetch('/api/chat/stream', {
  headers: {
    'X-Kernel-Type': 'openclaw',
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({ message: 'Hello' })
})

// 使用 QwenPaw
fetch('/api/chat/stream', {
  headers: {
    'X-Kernel-Type': 'qwenpaw',
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({ message: 'Hello' })
})
```

---

## 4. 部署方案

### 4.1 OpenClaw 内核部署

```yaml
# k8s-manifests/04-openclaw-pool.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: openclaw
  namespace: openclaw
spec:
  replicas: 3
  template:
    spec:
      containers:
      - name: openclaw
        image: openclaw/openclaw:latest
        ports:
        - containerPort: 3000
          name: gateway
```

### 4.2 QwenPaw 内核部署

```yaml
# k8s-manifests/07-qwenpaw-pool.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: qwenpaw
  namespace: openclaw
spec:
  replicas: 3
  template:
    spec:
      containers:
      - name: qwenpaw
        image: qwenpaw/qwenpaw:latest
        ports:
        - containerPort: 8088
          name: api
        command:
        - "python"
        - "-m"
        - "qwenpaw"
        - "app"
        - "--host"
        - "0.0.0.0"
        - "--port"
        - "8088"
```

### 4.3 混合部署（同时运行两种内核）

```
┌─────────────────────────────────────────────┐
│              Scheduler                     │
│         (Configurable Kernel)              │
└───────────┬─────────────────┬───────────────┘
            │                 │
    ┌───────┴────────┐   ┌────┴──────────┐
    ↓                ↓   ↓               ↓
┌─────────┐  ┌─────────┐ ┌─────────┐ ┌─────────┐
│OpenClaw │  │OpenClaw │ │QwenPaw  │ │QwenPaw  │
│  Pod 1  │  │  Pod 2  │ │  Pod 1  │ │  Pod 2  │
└─────────┘  └─────────┘ └─────────┘ └─────────┘
```

**Scheduler 容器池管理：**
```go
// 根据内核类型分配容器
func AllocateContainerByKernel(kernelType string) (*ContainerStatus, error) {
	switch kernelType {
	case "openclaw":
		return AllocateContainer("openclaw")
	case "qwenpaw":
		return AllocateContainer("qwenpaw")
	default:
		return nil, fmt.Errorf("未知内核: %s", kernelType)
	}
}
```

---

## 5. 优势分析

### 5.1 对比原架构

| 对比项 | 原架构（固定 OpenClaw） | 可配置内核架构 |
|-------|-------------------------|---------------|
| **灵活性** | 无法切换内核 | ✅ 支持多内核 |
| **扩展性** | 添加新内核需重写 | ✅ 实现接口即可 |
| **性能** | 单一协议（WebSocket） | ✅ 根据场景选择最优协议 |
| **生态** | 仅 Node.js 生态 | ✅ Node.js + Python 双生态 |
| **维护成本** | 低（单一系统） | 中（需维护适配器） |
| **学习曲线** | 低 | 中 |

### 5.2 使用场景建议

**选择 OpenClaw 的场景：**
- 需要实时性强的聊天应用
- 需要 Control UI 的管理界面
- 团队熟悉 Node.js/TypeScript
- 需要官方活跃支持

**选择 QwenPaw 的场景：**
- 需要 Python AI/ML 生态（如 Transformers、Langchain）
- 需要多智能体协作（AgentScope 框架）
- 团队熟悉 Python/FastAPI
- 需要本地模型支持（llama.cpp、Ollama）

---

## 6. 实施路线图

### 6.1 第一阶段：接口抽象（1-2天）

- ✅ 定义 `KernelInterface` 统一接口
- ✅ 实现 `KernelFactory` 工厂模式
- ✅ 创建 `KernelConfig` 配置结构

### 6.2 第二阶段：OpenClawAdapter（2-3天）

- ✅ 重构现有 WebSocket 连接池为 Adapter
- ✅ 实现 `StreamChat` 方法
- ✅ 测试 OpenClaw 流式输出

### 6.3 第三阶段：QwenPawAdapter（3-4天）

- ⏳ 实现 HTTP + SSE 客户端
- ⏳ 实现 `StreamChat` 方法
- ⏳ 适配 QwenPaw API 格式
- ⏳ 测试 QwenPaw 流式输出

### 6.4 第四阶段：集成测试（2-3天）

- ⏳ 前端测试两种内核切换
- ⏳ 性能对比测试
- ⏳ 压力测试
- ⏳ 文档完善

### 6.5 第五阶段：生产部署（1-2天）

- ⏳ K8s 混合部署
- ⏳ 监控告警配置
- ⏳ 回滚方案准备

**总计：约 9-14 天**

---

## 7. 风险与挑战

### 7.1 技术风险

| 风险 | 影响 | 缓解措施 |
|------|------|---------|
| **协议差异大** | 高 | 设计统一接口，隐藏协议细节 |
| **性能差异** | 中 | 性能测试，根据场景推荐 |
| **维护成本增加** | 中 | 文档完善，代码规范 |
| **两套系统 Bug** | 高 | 充分测试，灰度发布 |

### 7.2 建议

1. **先完成 OpenClawAdapter 重构**：验证抽象层设计的合理性
2. **QwenPaw 作为实验性功能**：避免一次性切换
3. **保留原有架构**：通过配置选择是否启用可配置内核
4. **充分测试**：尤其是边界情况（超时、错误、重连）

---

## 8. 总结

可配置内核架构通过**适配器模式 + 工厂模式**实现了对 OpenClaw 和 QwenPaw 的统一抽象。

**核心优势：**
- ✅ **灵活**：根据需求选择最适合的内核
- ✅ **扩展**：未来可轻松添加新的内核（如 AutoGPT、LangChain等）
- ✅ **兼容**：前端无需修改，始终是 HTTP + SSE
- ✅ **独立**：两种内核可独立升级、维护

**关键挑战：**
- ⚠️ 需要维护两套适配器
- ⚠️ 协议差异可能导致功能不完全对等
- ⚠️ 增加了系统复杂度

**最终建议：**  
**优先完成 OpenClawAdapter 重构**，验证抽象层设计，再根据实际需求决定是否实现 QwenPawAdapter。
