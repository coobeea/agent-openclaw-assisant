package api

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"log"
	"net/http"
	"os"
	"strconv"
	"strings"
	"sync"
	"time"

	"openclaw-scheduler/internal/db"
	"openclaw-scheduler/internal/k8s"
	wspool "openclaw-scheduler/internal/websocket"

	"github.com/gin-gonic/gin"
	"github.com/google/uuid"
)

// 全局 WebSocket 连接池
var (
	wsPool     *wspool.Pool
	wsPoolOnce sync.Once
)

func getWSPool() *wspool.Pool {
	wsPoolOnce.Do(func() {
		wsPool = wspool.NewPool()
		log.Println("✅ [WSPool] 连接池已初始化")
	})
	return wsPool
}

// RegisterRoutes 注册所有路由
func RegisterRoutes(r *gin.Engine) {
	// 健康检查
	r.GET("/health", func(c *gin.Context) {
		c.JSON(http.StatusOK, gin.H{
			"status":    "healthy",
			"timestamp": time.Now().Format(time.RFC3339),
		})
	})

	// 系统状态
	r.GET("/api/status", GetSystemStatus)

	// 用户相关
	userGroup := r.Group("/api/users")
	{
		userGroup.POST("/register", RegisterUser)
		userGroup.POST("/login", LoginUser)
	}

	// 智能体相关
	agentGroup := r.Group("/api/agents")
	{
		agentGroup.POST("/create", CreateAgent)
		agentGroup.GET("/list", ListAgents)
	}

	// 容器相关
	containerGroup := r.Group("/api/containers")
	{
		containerGroup.POST("/allocate", AllocateContainer)
		containerGroup.POST("/release", ReleaseContainer)
		containerGroup.GET("/status", GetContainerStatus)
	}

	// 对话相关
	chatGroup := r.Group("/api/chat")
	{
		chatGroup.POST("", Chat)
		chatGroup.POST("/stream", ChatStream)   // 原版流式接口（直接 WebSocket）
		chatGroup.POST("/stream/v2", ChatStreamV2) // V2 流式接口（可配置内核）
		chatGroup.GET("/history", GetChatHistory)
	}
}

// ========== 系统状态 ==========

func GetSystemStatus(c *gin.Context) {
	dbStatus := "ok"
	if err := db.DB.Ping(); err != nil {
		dbStatus = "error"
	}

	poolStatus, err := k8s.GetPoolStatus()
	k8sStatus := "ok"
	podCount := 0
	if err != nil {
		k8sStatus = "error"
	} else {
		if count, ok := poolStatus["total_pods"].(int); ok {
			podCount = count
		}
	}

	c.JSON(http.StatusOK, gin.H{
		"database":        dbStatus,
		"kubernetes":      k8sStatus,
		"pod_count":       podCount,
		"active_sessions": len(poolStatus),
		"timestamp":       time.Now().Format(time.RFC3339),
	})
}

// ========== 用户相关 ==========

func RegisterUser(c *gin.Context) {
	var req struct {
		Username string `json:"username"`
		Password string `json:"password"`
	}

	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "参数错误"})
		return
	}

	if req.Username == "" || req.Password == "" {
		c.JSON(http.StatusBadRequest, gin.H{"error": "用户名和密码不能为空"})
		return
	}

	user, err := db.CreateUser(req.Username, req.Password)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "用户名已存在"})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"success":  true,
		"user_id":  user.ID,
		"username": user.Username,
	})
}

func LoginUser(c *gin.Context) {
	var req struct {
		Username string `json:"username"`
		Password string `json:"password"`
	}

	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "参数错误"})
		return
	}

	user, err := db.GetUserByCredentials(req.Username, req.Password)
	if err != nil {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "用户名或密码错误"})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"success":  true,
		"user_id":  user.ID,
		"username": user.Username,
		"token":    fmt.Sprintf("token_%d_%d", user.ID, time.Now().Unix()),
	})
}

// ========== 智能体相关 ==========

func CreateAgent(c *gin.Context) {
	var req struct {
		UserID      int    `json:"user_id"`
		Name        string `json:"name"`
		Description string `json:"description"`
	}

	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "参数错误"})
		return
	}

	if req.UserID == 0 || req.Name == "" {
		c.JSON(http.StatusBadRequest, gin.H{"error": "user_id 和 name 不能为空"})
		return
	}

	// 生成 agent_id
	agentID := fmt.Sprintf("agent-%d-%d", req.UserID, time.Now().Unix())

	// 创建工作空间目录
	workspacePath := fmt.Sprintf("/data/agents/%s", agentID)
	os.MkdirAll(workspacePath, 0755)

	agent, err := db.CreateAgent(agentID, req.UserID, req.Name, req.Description, workspacePath)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	go func(agentID string) {
		container, warmErr := k8s.WarmAgent(agentID)
		if warmErr != nil {
			log.Printf("⚠️  [CreateAgent] 智能体预热失败: %s, err=%v", agentID, warmErr)
			return
		}
		log.Printf("🔥 [CreateAgent] 智能体预热完成: %s -> %s", agentID, container.PodName)
	}(agent.AgentID)

	c.JSON(http.StatusOK, gin.H{
		"success":        true,
		"agent_id":       agent.AgentID,
		"name":           agent.Name,
		"workspace_path": agent.WorkspacePath,
		"warming":        true,
	})
}

func ListAgents(c *gin.Context) {
	userIDStr := c.Query("user_id")
	userID := 0
	if userIDStr != "" {
		userID, _ = strconv.Atoi(userIDStr)
	}

	agents, err := db.ListAgents(userID)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"agents": agents,
	})
}

// ========== 容器相关 ==========

func AllocateContainer(c *gin.Context) {
	var req struct {
		AgentID string `json:"agent_id"`
	}

	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "参数错误"})
		return
	}

	if req.AgentID == "" {
		c.JSON(http.StatusBadRequest, gin.H{"error": "agent_id 不能为空"})
		return
	}

	status, err := k8s.AllocateContainer(req.AgentID)
	if err != nil {
		c.JSON(http.StatusServiceUnavailable, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, status)
}

func ReleaseContainer(c *gin.Context) {
	var req struct {
		Container string `json:"container"`
		AgentID   string `json:"agent_id"`
	}

	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "参数错误"})
		return
	}

	k8s.ReleaseContainer(req.Container, req.AgentID)

	c.JSON(http.StatusOK, gin.H{
		"status":    "released",
		"container": req.Container,
	})
}

func GetContainerStatus(c *gin.Context) {
	status, err := k8s.GetPoolStatus()
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, status)
}

// ========== 对话相关 ==========

func Chat(c *gin.Context) {
	var req struct {
		AgentID string `json:"agent_id"`
		Message string `json:"message"`
	}

	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "参数错误"})
		return
	}

	if req.AgentID == "" || req.Message == "" {
		c.JSON(http.StatusBadRequest, gin.H{"error": "agent_id 和 message 不能为空"})
		return
	}

	// 1. 分配容器
	container, err := k8s.AllocateContainer(req.AgentID)
	if err != nil {
		c.JSON(http.StatusServiceUnavailable, gin.H{"error": err.Error()})
		return
	}

	// 2. 确保智能体在容器中已注册
	if err := k8s.EnsureAgentReady(req.AgentID, container); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	// 3. 调用 OpenClaw Gateway HTTP API (非流式)
	gatewayURL := fmt.Sprintf("http://%s:18789/v1/chat/completions", container.IP)

	requestBody := map[string]interface{}{
		"model": fmt.Sprintf("openclaw:%s", req.AgentID),
		"messages": []map[string]string{
			{"role": "user", "content": req.Message},
		},
		"stream": false,
	}

	bodyBytes, _ := json.Marshal(requestBody)
	httpReq, err := http.NewRequest("POST", gatewayURL, bytes.NewReader(bodyBytes))
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": fmt.Sprintf("创建请求失败: %v", err)})
		return
	}

	httpReq.Header.Set("Content-Type", "application/json")
	httpReq.Header.Set("Authorization", "Bearer openclaw123")

	client := &http.Client{Timeout: 300 * time.Second}
	resp, err := client.Do(httpReq)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": fmt.Sprintf("调用 OpenClaw 失败: %v", err)})
		return
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		body, _ := io.ReadAll(resp.Body)
		c.JSON(http.StatusInternalServerError, gin.H{"error": fmt.Sprintf("OpenClaw 返回错误: %d, %s", resp.StatusCode, string(body))})
		return
	}

	// 4. 解析 OpenAI 格式的响应
	var openaiResp struct {
		Choices []struct {
			Message struct {
				Content string `json:"content"`
			} `json:"message"`
		} `json:"choices"`
	}

	body, _ := io.ReadAll(resp.Body)
	if err := json.Unmarshal(body, &openaiResp); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": fmt.Sprintf("解析响应失败: %v, body: %s", err, string(body))})
		return
	}

	responseText := ""
	if len(openaiResp.Choices) > 0 {
		responseText = openaiResp.Choices[0].Message.Content
	} else {
		responseText = "[空回复]"
	}

	// 5. 保存对话历史
	conv, err := db.CreateConversation(req.AgentID, req.Message, responseText)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	// 6. 返回结果（不释放容器，保持会话）
	c.JSON(http.StatusOK, gin.H{
		"success":         true,
		"agent_id":        req.AgentID,
		"message":         req.Message,
		"response":        responseText,
		"conversation_id": conv.ID,
		"container":       container.PodName,
		"timestamp":       time.Now().Format(time.RFC3339),
	})
}

func GetChatHistory(c *gin.Context) {
	agentID := c.Query("agent_id")
	limitStr := c.DefaultQuery("limit", "50")

	if agentID == "" {
		c.JSON(http.StatusBadRequest, gin.H{"error": "agent_id 不能为空"})
		return
	}

	limit, _ := strconv.Atoi(limitStr)

	history, err := db.GetConversationHistory(agentID, limit)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"agent_id": agentID,
		"history":  history,
	})
}

func writeSSEJSON(w io.Writer, flusher http.Flusher, payload interface{}) {
	data, err := json.Marshal(payload)
	if err != nil {
		return
	}
	fmt.Fprintf(w, "data: %s\n\n", string(data))
	flusher.Flush()
}

func writeSSEError(w io.Writer, flusher http.Flusher, message string) {
	writeSSEJSON(w, flusher, gin.H{
		"type":    "error",
		"content": message,
	})
}

func writeSSEStatus(w io.Writer, flusher http.Flusher, message string) {
	writeSSEJSON(w, flusher, gin.H{
		"type":    "status",
		"content": message,
	})
}

func writeSSEComment(w io.Writer, flusher http.Flusher, message string) {
	fmt.Fprintf(w, ": %s\n\n", message)
	flusher.Flush()
}

func writeSSEChunk(w io.Writer, flusher http.Flusher, requestID, content string) {
	if content == "" {
		return
	}

	sseData := map[string]interface{}{
		"id":      requestID,
		"object":  "chat.completion.chunk",
		"created": time.Now().Unix(),
		"model":   "openclaw-agent",
		"choices": []map[string]interface{}{
			{
				"index": 0,
				"delta": map[string]interface{}{
					"content": content,
				},
				"finish_reason": nil,
			},
		},
	}
	writeSSEJSON(w, flusher, sseData)
}

// ChatStream 流式对话接口 (SSE) - 使用 WebSocket 连接 OpenClaw
func ChatStream(c *gin.Context) {
	fmt.Printf("🔵 [ChatStream] 收到请求 from %s\n", c.ClientIP())

	var req struct {
		AgentID string `json:"agent_id"`
		Message string `json:"message"`
	}

	if err := c.ShouldBindJSON(&req); err != nil {
		fmt.Printf("❌ [ChatStream] 参数解析失败: %v\n", err)
		c.JSON(http.StatusBadRequest, gin.H{"error": "参数错误"})
		return
	}

	fmt.Printf("✅ [ChatStream] 解析成功 - AgentID: %s, Message: %s\n", req.AgentID, req.Message)

	if req.AgentID == "" || req.Message == "" {
		fmt.Printf("❌ [ChatStream] 参数为空\n")
		c.JSON(http.StatusBadRequest, gin.H{"error": "agent_id 和 message 不能为空"})
		return
	}

	c.Header("Content-Type", "text/event-stream; charset=utf-8")
	c.Header("Cache-Control", "no-cache")
	c.Header("Connection", "keep-alive")
	c.Header("X-Accel-Buffering", "no")

	flusher, ok := c.Writer.(http.Flusher)
	if !ok {
		fmt.Printf("❌ [ChatStream] Writer 不支持 Flush\n")
		c.JSON(http.StatusInternalServerError, gin.H{"error": "不支持流式传输"})
		return
	}

	c.Status(http.StatusOK)
	fmt.Fprintf(c.Writer, ": connected\n\n")
	flusher.Flush()
	fmt.Printf("📤 [ChatStream] SSE 响应头已发送\n")
	writeSSEStatus(c.Writer, flusher, "正在分配容器...")

	// 1. 分配容器
	fmt.Printf("⏳ [ChatStream] 开始分配容器...\n")
	container, err := k8s.AllocateContainer(req.AgentID)
	if err != nil {
		fmt.Printf("❌ [ChatStream] 容器分配失败: %v\n", err)
		writeSSEError(c.Writer, flusher, err.Error())
		return
	}
	fmt.Printf("✅ [ChatStream] 容器分配成功 - Pod: %s, IP: %s\n", container.PodName, container.IP)
	writeSSEStatus(c.Writer, flusher, fmt.Sprintf("容器已就绪：%s，正在准备智能体...", container.PodName))

	// 2. 确保智能体在容器中已注册
	if err := k8s.EnsureAgentReady(req.AgentID, container); err != nil {
		fmt.Printf("❌ [ChatStream] 智能体准备失败: %v\n", err)
		writeSSEError(c.Writer, flusher, err.Error())
		return
	}
	writeSSEStatus(c.Writer, flusher, "智能体已就绪，正在建立流式连接...")

	// 3. 获取 WebSocket 连接（复用已有连接）
	pool := getWSPool()
	conn, err := pool.GetConn(container.IP)
	if err != nil {
		fmt.Printf("❌ [ChatStream] WebSocket 连接失败: %v\n", err)
		writeSSEError(c.Writer, flusher, fmt.Sprintf("连接失败: %v", err))
		return
	}
	defer conn.Close()
	fmt.Printf("✅ [ChatStream] WebSocket 连接就绪\n")
	writeSSEStatus(c.Writer, flusher, "流式连接已建立，正在等待模型响应...")

	// 5. 生成请求 ID 和 SessionKey（用于区分多个 Agent 在同一个 WS 连接上的会话）
	requestID := uuid.New().String()
	sessionKey := fmt.Sprintf("session-%s-%s", req.AgentID, uuid.New().String()[:8])
	fmt.Printf("📝 [ChatStream] SessionKey: %s\n", sessionKey)

	// 6. 通过 WebSocket 发送聊天请求（使用正确的方法名：chat.send）
	chatReq := map[string]interface{}{
		"type":   "req",
		"id":     requestID,
		"method": "chat.send",
		"params": map[string]interface{}{
			"sessionKey":     sessionKey,
			"message":        req.Message,
			"idempotencyKey": requestID, // 必需参数！
		},
	}

	fmt.Printf("📡 [ChatStream] 发送 WebSocket 请求 - RequestID: %s, SessionKey: %s\n", requestID, sessionKey)
	fmt.Printf("🔍 [Debug] 准备调用 WriteJSON...\n")
	err = conn.WriteJSON(chatReq)
	fmt.Printf("🔍 [Debug] WriteJSON 完成，err=%v\n", err)

	if err != nil {
		fmt.Printf("❌ [ChatStream] 发送请求失败: %v\n", err)
		writeSSEError(c.Writer, flusher, "发送请求失败")
		return
	}
	fmt.Printf("✅ [Debug] WriteJSON 成功\n")

	// 7. 实时监听 WebSocket 事件并转换为 SSE
	fullResponse := ""
	done := false
	timeout := time.After(180 * time.Second)
	requestContext := c.Request.Context()
	consecutiveReadTimeouts := 0

	fmt.Printf("⏳ [ChatStream] 开始监听 WebSocket 事件...\n")

	for !done {
		select {
		case <-requestContext.Done():
			fmt.Printf("🛑 [ChatStream] 客户端已断开\n")
			done = true
		case <-timeout:
			fmt.Printf("⏰ [ChatStream] 超时\n")
			writeSSEError(c.Writer, flusher, "超时")
			done = true

		default:
			conn.SetReadDeadline(time.Now().Add(15 * time.Second))

			fmt.Printf("🔍 [Debug] 开始 ReadJSON...\n")
			var frame map[string]interface{}
			err := conn.ReadJSON(&frame)
			fmt.Printf("🔍 [Debug] ReadJSON 完成, err=%v\n", err)

			if err != nil {
				if netErr, ok := err.(interface{ Timeout() bool }); ok && netErr.Timeout() {
					consecutiveReadTimeouts++
					fmt.Printf("⏱️  [ChatStream] 读取超时（15秒），继续等待... 连续超时=%d\n", consecutiveReadTimeouts)
					if consecutiveReadTimeouts >= 4 {
						writeSSEError(c.Writer, flusher, "模型响应超时")
						done = true
						break
					}
					writeSSEComment(c.Writer, flusher, "heartbeat")
					continue
				}
				fmt.Printf("❌ [ChatStream] 读取错误: %v\n", err)
				writeSSEError(c.Writer, flusher, "流式连接中断")
				done = true
				break
			}

			consecutiveReadTimeouts = 0

			frameType, _ := frame["type"].(string)
			eventName, _ := frame["event"].(string)

			// 调试：打印所有收到的帧
			fmt.Printf("📦 [Debug] 收到帧 - type: %s, event: %s\n", frameType, eventName)
			if frameType == "event" && eventName != "" {
				fmt.Printf("🔔 [Debug] 收到事件: %s\n", eventName)
			}

			// 处理响应帧
			if frameType == "res" {
				reqID, _ := frame["id"].(string)
				if reqID == requestID {
					ok, _ := frame["ok"].(bool)
					if !ok {
						errorData, _ := json.Marshal(frame["error"])
						fmt.Printf("❌ [ChatStream] 请求失败: %s\n", errorData)
						writeSSEError(c.Writer, flusher, "请求失败")
						done = true
					}
					fmt.Printf("✅ [ChatStream] 请求已接受\n")
				}
			}

			// 处理事件帧（实时流式）
			if frameType == "event" {
				eventName, _ := frame["event"].(string)
				payload, _ := frame["payload"].(map[string]interface{})

				// 打印 agent 事件（可能包含错误信息）
				if eventName == "agent" && payload != nil {
					payloadJSON, _ := json.Marshal(payload)
					fmt.Printf("📢 [Debug] Agent 事件: %s\n", string(payloadJSON))
				}

				if eventName == "agent" {
					payloadSessionKey, _ := payload["sessionKey"].(string)
					if !strings.Contains(payloadSessionKey, sessionKey) {
						continue
					}

					streamName, _ := payload["stream"].(string)
					data, _ := payload["data"].(map[string]interface{})

					if streamName == "assistant" && data != nil {
						delta, _ := data["delta"].(string)
						if delta != "" {
							fullResponse += delta
							fmt.Printf("💬 [ChatStream] 实时输出(delta): %s\n", delta)
							writeSSEChunk(c.Writer, flusher, requestID, delta)
						}
					}
				}

				// chat 事件主要用于兜底补全和结束信号
				if eventName == "chat" {
					fmt.Printf("💬 [Debug] 收到 chat 事件！\n")
					payloadSessionKey, _ := payload["sessionKey"].(string)

					// OpenClaw 返回的 sessionKey 是完整格式：agent:main:session-xxx
					// 我们只需要检查是否包含我们的 sessionKey 作为后缀
					if !strings.Contains(payloadSessionKey, sessionKey) {
						continue
					}

					state, _ := payload["state"].(string)
					message, _ := payload["message"].(map[string]interface{})

					// 处理 assistant 消息（只作为兜底，避免 agent.delta 缺失时完全无输出）
					if message != nil {
						role, _ := message["role"].(string)
						if role == "assistant" {
							// 从 message.content[0].text 提取文本
							contentArray, _ := message["content"].([]interface{})
							var text string
							if len(contentArray) > 0 {
								contentItem, _ := contentArray[0].(map[string]interface{})
								text, _ = contentItem["text"].(string)
							}

							// 计算增量（使用完整text与之前的对比）
							content := ""
							if text != "" && len(text) > len(fullResponse) {
								content = text[len(fullResponse):]
								fullResponse = text
							}

							if content != "" {
								fmt.Printf("💬 [ChatStream] 兜底输出(chat): %s\n", content)
								writeSSEChunk(c.Writer, flusher, requestID, content)
							}
						}
					}

					// 检查是否结束
					if state == "final" {
						fmt.Printf("✅ [ChatStream] 对话完成\n")
						fmt.Fprintf(c.Writer, "data: [DONE]\n\n")
						flusher.Flush()
						done = true
					}

					// 处理错误
					if state == "error" {
						fmt.Printf("❌ [ChatStream] Agent 错误\n")
						writeSSEError(c.Writer, flusher, "Agent 错误")
						done = true
					}
				}
			}
		}
	}

	// 8. 保存对话历史
	if fullResponse != "" {
		_, _ = db.CreateConversation(req.AgentID, req.Message, fullResponse)
		fmt.Printf("💾 [ChatStream] 对话已保存 - 响应长度: %d\n", len(fullResponse))
	}
}
