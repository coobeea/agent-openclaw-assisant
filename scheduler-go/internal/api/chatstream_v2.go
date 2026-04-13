package api

import (
	"context"
	"fmt"
	"net/http"
	"os"
	"time"

	"openclaw-scheduler/internal/k8s"
	"openclaw-scheduler/internal/kernel"
	_ "openclaw-scheduler/internal/kernel/adapters" // 触发自动注册

	"github.com/gin-gonic/gin"
	"github.com/google/uuid"
)

// ChatStreamV2 是使用可配置内核架构的新版本流式聊天接口
// 支持动态切换 OpenClaw 和 QwenPaw 内核
func ChatStreamV2(c *gin.Context) {
	fmt.Printf("🔵 [ChatStreamV2] 收到请求 from %s\n", c.ClientIP())

	var req struct {
		AgentID string `json:"agent_id"`
		Message string `json:"message"`
	}

	if err := c.ShouldBindJSON(&req); err != nil {
		fmt.Printf("❌ [ChatStreamV2] 参数解析失败: %v\n", err)
		c.JSON(http.StatusBadRequest, gin.H{"error": "参数错误"})
		return
	}

	fmt.Printf("✅ [ChatStreamV2] 解析成功 - AgentID: %s, Message: %s\n", req.AgentID, req.Message)

	if req.AgentID == "" || req.Message == "" {
		fmt.Printf("❌ [ChatStreamV2] 参数为空\n")
		c.JSON(http.StatusBadRequest, gin.H{"error": "agent_id 和 message 不能为空"})
		return
	}

	// 1. 确定要使用的内核类型
	kernelType := getKernelType(c)
	fmt.Printf("🔧 [ChatStreamV2] 使用内核: %s\n", kernelType)

	// 2. 设置 SSE 响应头
	c.Header("Content-Type", "text/event-stream; charset=utf-8")
	c.Header("Cache-Control", "no-cache")
	c.Header("Connection", "keep-alive")
	c.Header("X-Accel-Buffering", "no")
	c.Header("X-Kernel-Type", string(kernelType)) // 告诉前端使用的内核

	flusher, ok := c.Writer.(http.Flusher)
	if !ok {
		fmt.Printf("❌ [ChatStreamV2] Writer 不支持 Flush\n")
		c.JSON(http.StatusInternalServerError, gin.H{"error": "不支持流式传输"})
		return
	}

	c.Status(http.StatusOK)
	fmt.Fprintf(c.Writer, ": connected\n\n")
	flusher.Flush()
	fmt.Printf("📤 [ChatStreamV2] SSE 响应头已发送\n")

	writeSSEStatus(c.Writer, flusher, fmt.Sprintf("正在分配容器（内核：%s）...", kernelType))

	// 3. 根据内核类型分配容器
	fmt.Printf("⏳ [ChatStreamV2] 开始分配容器...\n")
	container, err := k8s.AllocateContainerByKernel(string(kernelType), req.AgentID)
	if err != nil {
		fmt.Printf("❌ [ChatStreamV2] 容器分配失败: %v\n", err)
		writeSSEError(c.Writer, flusher, err.Error())
		return
	}
	fmt.Printf("✅ [ChatStreamV2] 容器分配成功 - Pod: %s, IP: %s\n", container.PodName, container.IP)
	writeSSEStatus(c.Writer, flusher, fmt.Sprintf("容器已就绪：%s", container.PodName))

	// 4. 创建内核配置
	kernelConfig := createKernelConfig(kernelType, container.IP)
	fmt.Printf("🔧 [ChatStreamV2] 内核配置: %+v\n", kernelConfig)

	// 5. 创建内核实例
	kernelInstance, err := kernel.GetFactory().CreateKernel(kernelConfig)
	if err != nil {
		fmt.Printf("❌ [ChatStreamV2] 创建内核失败: %v\n", err)
		writeSSEError(c.Writer, flusher, fmt.Sprintf("创建内核失败: %v", err))
		return
	}
	defer kernelInstance.Close()
	fmt.Printf("✅ [ChatStreamV2] 内核实例创建成功: %s\n", kernelInstance.GetKernelType())

	writeSSEStatus(c.Writer, flusher, "正在初始化内核连接...")

	// 6. 初始化内核连接
	ctx, cancel := context.WithTimeout(c.Request.Context(), 30*time.Second)
	defer cancel()

	if err := kernelInstance.Initialize(ctx, kernelConfig); err != nil {
		fmt.Printf("❌ [ChatStreamV2] 内核初始化失败: %v\n", err)
		writeSSEError(c.Writer, flusher, fmt.Sprintf("连接失败: %v", err))
		return
	}
	fmt.Printf("✅ [ChatStreamV2] 内核初始化成功\n")

	writeSSEStatus(c.Writer, flusher, "内核已就绪，正在发送消息...")

	// 7. 生成 SessionKey
	sessionKey := fmt.Sprintf("session-%s-%s", req.AgentID, uuid.New().String()[:8])
	requestID := uuid.New().String()
	fmt.Printf("📝 [ChatStreamV2] SessionKey: %s, RequestID: %s\n", sessionKey, requestID)

	// 8. 发送聊天请求（统一接口）
	chatReq := &kernel.ChatRequest{
		AgentID:    req.AgentID,
		SessionKey: sessionKey,
		Message:    req.Message,
		UserID:     c.GetString("user_id"), // 从认证中获取
		RequestID:  requestID,
	}

	streamCtx, streamCancel := context.WithTimeout(c.Request.Context(), 3*time.Minute)
	defer streamCancel()

	eventChan, err := kernelInstance.StreamChat(streamCtx, chatReq)
	if err != nil {
		fmt.Printf("❌ [ChatStreamV2] 发送聊天请求失败: %v\n", err)
		writeSSEError(c.Writer, flusher, fmt.Sprintf("发送失败: %v", err))
		return
	}
	fmt.Printf("✅ [ChatStreamV2] 聊天请求已发送，开始监听流式响应\n")

	writeSSEStatus(c.Writer, flusher, "正在等待模型响应...")

	// 9. 监听事件流并转换为 SSE（统一格式）
	fullResponse := ""
	eventCount := 0

	for event := range eventChan {
		eventCount++
		fmt.Printf("📦 [ChatStreamV2] 收到事件 #%d - Type: %s\n", eventCount, event.Type)

		switch event.Type {
		case kernel.EventTypeStart:
			// 流开始
			fmt.Printf("▶️  [ChatStreamV2] 流式输出开始\n")
			writeSSEStatus(c.Writer, flusher, "模型开始响应...")

		case kernel.EventTypeDelta:
			// 增量内容
			if event.Content != "" {
				fullResponse += event.Content
				fmt.Printf("💬 [ChatStreamV2] Delta: %s\n", event.Content)
				writeSSEChunk(c.Writer, flusher, requestID, event.Content)
			}

		case kernel.EventTypeDone:
			// 完成
			fmt.Printf("✅ [ChatStreamV2] 流式输出完成，总长度: %d\n", len(fullResponse))
			writeSSEStatus(c.Writer, flusher, fmt.Sprintf("完成（共 %d 字符）", len(fullResponse)))
			fmt.Fprintf(c.Writer, "data: [DONE]\n\n")
			flusher.Flush()
			return

		case kernel.EventTypeError:
			// 错误
			fmt.Printf("❌ [ChatStreamV2] 内核错误: %s\n", event.Error)
			writeSSEError(c.Writer, flusher, event.Error)
			return

		default:
			fmt.Printf("⚠️  [ChatStreamV2] 未知事件类型: %s\n", event.Type)
		}
	}

	// 如果事件流结束但没有收到 Done 事件
	if fullResponse != "" {
		fmt.Printf("⚠️  [ChatStreamV2] 事件流结束，未收到 Done 事件，总长度: %d\n", len(fullResponse))
		fmt.Fprintf(c.Writer, "data: [DONE]\n\n")
		flusher.Flush()
	} else {
		fmt.Printf("⚠️  [ChatStreamV2] 事件流结束，未收到任何内容\n")
		writeSSEError(c.Writer, flusher, "未收到响应")
	}
}

// getKernelType 从环境变量或 HTTP Header 获取内核类型
func getKernelType(c *gin.Context) kernel.KernelType {
	// 优先从 HTTP Header 获取（支持动态切换）
	headerKernel := c.GetHeader("X-Kernel-Type")
	if headerKernel != "" {
		if headerKernel == string(kernel.KernelTypeOpenClaw) {
			return kernel.KernelTypeOpenClaw
		}
		if headerKernel == string(kernel.KernelTypeQwenPaw) {
			return kernel.KernelTypeQwenPaw
		}
		fmt.Printf("⚠️  [getKernelType] 未知的内核类型: %s，使用默认\n", headerKernel)
	}

	// 从环境变量获取（全局配置）
	envKernel := os.Getenv("KERNEL_TYPE")
	if envKernel != "" {
		if envKernel == string(kernel.KernelTypeOpenClaw) {
			return kernel.KernelTypeOpenClaw
		}
		if envKernel == string(kernel.KernelTypeQwenPaw) {
			return kernel.KernelTypeQwenPaw
		}
		fmt.Printf("⚠️  [getKernelType] 环境变量中未知的内核类型: %s，使用默认\n", envKernel)
	}

	// 默认使用 OpenClaw
	return kernel.KernelTypeOpenClaw
}

// createKernelConfig 根据内核类型和 Pod IP 创建配置
func createKernelConfig(kernelType kernel.KernelType, podIP string) *kernel.KernelConfig {
	switch kernelType {
	case kernel.KernelTypeOpenClaw:
		// OpenClaw 配置（WebSocket, Port 18789）
		authToken := os.Getenv("KERNEL_OPENCLAW_AUTH_TOKEN")
		if authToken == "" {
			authToken = "openclaw-internal-k8s-token" // 默认 token
		}
		config := kernel.DefaultOpenClawConfig(podIP, authToken)
		config.Timeout = 120 // 2分钟超时
		return config

	case kernel.KernelTypeQwenPaw:
		// QwenPaw 配置（HTTP, Port 8088）
		config := kernel.DefaultQwenPawConfig(fmt.Sprintf("%s:8088", podIP))
		config.Timeout = 120
		
		// 如果有配置的 Token，添加认证
		authToken := os.Getenv("KERNEL_QWENPAW_AUTH_TOKEN")
		if authToken != "" {
			config.Auth = &kernel.AuthConfig{
				Type:  "token",
				Token: authToken,
			}
		}
		return config

	default:
		// 默认返回 OpenClaw 配置
		return kernel.DefaultOpenClawConfig(podIP, "openclaw-internal-k8s-token")
	}
}
