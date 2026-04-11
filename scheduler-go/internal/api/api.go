package api

import (
	"bufio"
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"os"
	"strconv"
	"time"

	"github.com/gin-gonic/gin"
	"openclaw-scheduler/internal/db"
	"openclaw-scheduler/internal/k8s"
)

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
		chatGroup.POST("/stream", ChatStream) // 流式接口（通过 OpenClaw Gateway）
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

	c.JSON(http.StatusOK, gin.H{
		"success":        true,
		"agent_id":       agent.AgentID,
		"name":           agent.Name,
		"workspace_path": agent.WorkspacePath,
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
	agentDir := fmt.Sprintf("/data/agents/%s/agent", req.AgentID)
	workspaceDir := fmt.Sprintf("/data/agents/%s", req.AgentID)
	addCmd := []string{"node", "openclaw.mjs", "agents", "add", req.AgentID, "--workspace", workspaceDir, "--agent-dir", agentDir, "--non-interactive"}
	_, _, _ = k8s.ExecCommand("openclaw", container.PodName, addCmd) // 忽略错误，因为可能已经存在

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
		"success":          true,
		"agent_id":         req.AgentID,
		"message":          req.Message,
		"response":         responseText,
		"conversation_id":  conv.ID,
		"container":        container.PodName,
		"timestamp":        time.Now().Format(time.RFC3339),
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

// ChatStream 流式对话接口 (SSE)
func ChatStream(c *gin.Context) {
	// 添加日志：请求到达
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

	// 1. 分配容器
	fmt.Printf("⏳ [ChatStream] 开始分配容器...\n")
	container, err := k8s.AllocateContainer(req.AgentID)
	if err != nil {
		fmt.Printf("❌ [ChatStream] 容器分配失败: %v\n", err)
		c.JSON(http.StatusServiceUnavailable, gin.H{"error": err.Error()})
		return
	}
	fmt.Printf("✅ [ChatStream] 容器分配成功 - Pod: %s, IP: %s\n", container.PodName, container.IP)

	// 2. 确保智能体在容器中已注册
	agentDir := fmt.Sprintf("/data/agents/%s/agent", req.AgentID)
	workspaceDir := fmt.Sprintf("/data/agents/%s", req.AgentID)
	addCmd := []string{"node", "openclaw.mjs", "agents", "add", req.AgentID, "--workspace", workspaceDir, "--agent-dir", agentDir, "--non-interactive"}
	_, _, _ = k8s.ExecCommand("openclaw", container.PodName, addCmd)

	// 3. 调用 OpenClaw Gateway HTTP API (流式)
	gatewayURL := fmt.Sprintf("http://%s:18789/v1/chat/completions", container.IP)
	fmt.Printf("📡 [ChatStream] 准备调用 Gateway: %s\n", gatewayURL)
	
	requestBody := map[string]interface{}{
		"model": fmt.Sprintf("openclaw:%s", req.AgentID),
		"messages": []map[string]string{
			{"role": "user", "content": req.Message},
		},
		"stream": true,
	}
	
	bodyBytes, _ := json.Marshal(requestBody)
	httpReq, err := http.NewRequest("POST", gatewayURL, bytes.NewReader(bodyBytes))
	if err != nil {
		fmt.Printf("❌ [ChatStream] 创建请求失败: %v\n", err)
		c.JSON(http.StatusInternalServerError, gin.H{"error": fmt.Sprintf("创建请求失败: %v", err)})
		return
	}
	
	httpReq.Header.Set("Content-Type", "application/json")
	httpReq.Header.Set("Authorization", "Bearer openclaw123")
	
	fmt.Printf("⏳ [ChatStream] 发送请求到 OpenClaw Gateway...\n")
	client := &http.Client{Timeout: 0} // 无超时限制
	resp, err := client.Do(httpReq)
	if err != nil {
		fmt.Printf("❌ [ChatStream] Gateway 请求失败: %v\n", err)
		c.JSON(http.StatusInternalServerError, gin.H{"error": fmt.Sprintf("调用 OpenClaw 失败: %v", err)})
		return
	}
	defer resp.Body.Close()
	fmt.Printf("✅ [ChatStream] Gateway 响应状态: %d\n", resp.StatusCode)
	
	if resp.StatusCode != http.StatusOK {
		body, _ := io.ReadAll(resp.Body)
		fmt.Printf("❌ [ChatStream] Gateway 返回错误: %d, %s\n", resp.StatusCode, string(body))
		c.JSON(http.StatusInternalServerError, gin.H{"error": fmt.Sprintf("OpenClaw 返回错误: %d, %s", resp.StatusCode, string(body))})
		return
	}
	
	// 4. 设置 SSE 响应头
	c.Header("Content-Type", "text/event-stream; charset=utf-8")
	c.Header("Cache-Control", "no-cache")
	c.Header("Connection", "keep-alive")
	c.Header("X-Accel-Buffering", "no")
	c.Status(http.StatusOK)
	fmt.Printf("📤 [ChatStream] SSE 响应头已设置\n")
	
	// 4. 读取 SSE 流并转发（OpenClaw Gateway 格式）
	flusher, ok := c.Writer.(http.Flusher)
	if !ok {
		fmt.Printf("❌ [ChatStream] Writer 不支持 Flush！\n")
		c.JSON(http.StatusInternalServerError, gin.H{"error": "不支持流式传输"})
		return
	}
	fmt.Printf("✅ [ChatStream] Flusher 准备就绪\n")
	
	// 立即 flush 一次，确保响应头被发送
	flusher.Flush()
	fmt.Printf("📤 [ChatStream] 初始 Flush 完成\n")
	
	reader := bufio.NewReader(resp.Body)
	
	fullResponse := ""
	lineCount := 0
	
	fmt.Printf("⏳ [ChatStream] 开始读取 SSE 流...\n")
	for {
		// 逐行读取
		line, err := reader.ReadString('\n')
		lineCount++
		if lineCount%10 == 1 {
			fmt.Printf("📥 [ChatStream] 已读取 %d 行\n", lineCount)
		}
		
		// 移除换行符
		trimmed := bytes.TrimRight([]byte(line), "\r\n")
		lineStr := string(trimmed)
		
		// 空行，跳过
		if lineStr == "" {
			if err == io.EOF {
				break
			}
			continue
		}
		
		// [DONE] 标记
		if lineStr == "data: [DONE]" {
			fmt.Printf("✅ [ChatStream] 收到 [DONE] 标记\n")
			fmt.Fprintf(c.Writer, "data: {\"type\":\"done\"}\n\n")
			flusher.Flush()
			break
		}
		
		// 解析 SSE 数据
		if len(lineStr) > 6 && lineStr[:6] == "data: " {
			dataStr := lineStr[6:]
			
			var chunk struct {
				Choices []struct {
					Delta struct {
						Content string `json:"content"`
						Role    string `json:"role"`
					} `json:"delta"`
					FinishReason string `json:"finish_reason"`
				} `json:"choices"`
			}
			
			if json.Unmarshal([]byte(dataStr), &chunk) == nil {
				if len(chunk.Choices) > 0 {
					content := chunk.Choices[0].Delta.Content
					
					if content != "" {
						fullResponse += content
						fmt.Printf("💬 [ChatStream] 转发内容: %s\n", content)
						
						// 转发给前端
						jsonData, _ := json.Marshal(map[string]interface{}{
							"type":    "content",
							"content": content,
						})
						fmt.Fprintf(c.Writer, "data: %s\n\n", string(jsonData))
						flusher.Flush()
					}
				}
			}
		}
		
		// 检查错误
		if err == io.EOF {
			break
		}
		if err != nil {
			break
		}
	}
	
	// 6. 保存对话历史
	if fullResponse != "" {
		_, _ = db.CreateConversation(req.AgentID, req.Message, fullResponse)
	}
}
