// Package adapters provides kernel adapter implementations
package adapters

import (
	"bufio"
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"io"
	"log"
	"net/http"
	"strings"
	"sync"
	"time"

	"openclaw-scheduler/internal/kernel"
)

// QwenPawAdapter implements KernelInterface for QwenPaw backend
type QwenPawAdapter struct {
	config *kernel.KernelConfig
	client *http.Client
	mu     sync.Mutex

	// Metrics
	requestCount int64
}

// NewQwenPawAdapter creates a new QwenPaw adapter instance
func NewQwenPawAdapter() kernel.KernelInterface {
	return &QwenPawAdapter{
		client: &http.Client{
			Timeout: 0, // No timeout for SSE streaming
		},
	}
}

// Initialize verifies connection to QwenPaw server
func (a *QwenPawAdapter) Initialize(ctx context.Context, config *kernel.KernelConfig) error {
	if config.Type != kernel.KernelTypeQwenPaw {
		return fmt.Errorf("invalid kernel type: expected 'qwenpaw', got '%s'", config.Type)
	}

	a.config = config

	// Verify connection by calling version endpoint
	healthURL := fmt.Sprintf("http://%s/api/version", config.Endpoint)

	req, err := http.NewRequestWithContext(ctx, "GET", healthURL, nil)
	if err != nil {
		return fmt.Errorf("failed to create health check request: %w", err)
	}

	resp, err := a.client.Do(req)
	if err != nil {
		return fmt.Errorf("failed to connect to QwenPaw: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		body, _ := io.ReadAll(resp.Body)
		return fmt.Errorf("health check failed: HTTP %d, body: %s", resp.StatusCode, string(body))
	}

	log.Printf("✅ [QwenPawAdapter] Initialized successfully, endpoint: %s", config.Endpoint)
	return nil
}

// StreamChat sends a chat message and returns a channel for streaming responses
func (a *QwenPawAdapter) StreamChat(ctx context.Context, req *kernel.ChatRequest) (<-chan kernel.ChatEvent, error) {
	// Create event channel
	eventChan := make(chan kernel.ChatEvent, 100)

	// Construct QwenPaw request payload
	// Based on QwenPaw's API: POST /api/console/chat
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

	// Serialize payload
	payloadBytes, err := json.Marshal(qwenReq)
	if err != nil {
		close(eventChan)
		return nil, fmt.Errorf("failed to marshal request: %w", err)
	}

	// Construct HTTP request
	chatURL := fmt.Sprintf("http://%s/api/console/chat", a.config.Endpoint)
	httpReq, err := http.NewRequestWithContext(ctx, "POST", chatURL, bytes.NewReader(payloadBytes))
	if err != nil {
		close(eventChan)
		return nil, fmt.Errorf("failed to create request: %w", err)
	}

	// Set headers
	httpReq.Header.Set("Content-Type", "application/json")
	httpReq.Header.Set("Accept", "text/event-stream")
	httpReq.Header.Set("X-Agent-Id", req.AgentID)

	// Add authentication if configured
	if a.config.Auth != nil {
		switch a.config.Auth.Type {
		case "token":
			if a.config.Auth.Token != "" {
				httpReq.Header.Set("Authorization", fmt.Sprintf("Bearer %s", a.config.Auth.Token))
			}
		case "basic":
			if a.config.Auth.User != "" && a.config.Auth.Pass != "" {
				httpReq.SetBasicAuth(a.config.Auth.User, a.config.Auth.Pass)
			}
		}
	}

	log.Printf("📤 [QwenPawAdapter] Sending chat request: %s", req.Message[:min(50, len(req.Message))])

	// Start streaming in a goroutine
	go a.streamResponse(ctx, httpReq, req.SessionKey, eventChan)

	return eventChan, nil
}

// streamResponse handles SSE streaming from QwenPaw
func (a *QwenPawAdapter) streamResponse(ctx context.Context, httpReq *http.Request, sessionKey string, eventChan chan<- kernel.ChatEvent) {
	defer close(eventChan)

	// Send request
	resp, err := a.client.Do(httpReq)
	if err != nil {
		eventChan <- kernel.ChatEvent{
			Type:      kernel.EventTypeError,
			Error:     fmt.Sprintf("HTTP request failed: %v", err),
			Timestamp: time.Now(),
		}
		return
	}
	defer resp.Body.Close()

	// Check status code
	if resp.StatusCode != http.StatusOK {
		body, _ := io.ReadAll(resp.Body)
		eventChan <- kernel.ChatEvent{
			Type:      kernel.EventTypeError,
			Error:     fmt.Sprintf("HTTP %d: %s", resp.StatusCode, string(body)),
			Timestamp: time.Now(),
		}
		return
	}

	// Verify content type
	contentType := resp.Header.Get("Content-Type")
	if !strings.Contains(contentType, "text/event-stream") {
		eventChan <- kernel.ChatEvent{
			Type:      kernel.EventTypeError,
			Error:     fmt.Sprintf("unexpected content-type: %s", contentType),
			Timestamp: time.Now(),
		}
		return
	}

	log.Printf("✅ [QwenPawAdapter] Streaming started")

	// Send start event
	eventChan <- kernel.ChatEvent{
		Type:       kernel.EventTypeStart,
		SessionKey: sessionKey,
		Timestamp:  time.Now(),
	}

	// Parse SSE stream
	scanner := bufio.NewScanner(resp.Body)
	scanner.Split(scanSSELines)

	for scanner.Scan() {
		select {
		case <-ctx.Done():
			eventChan <- kernel.ChatEvent{
				Type:      kernel.EventTypeError,
				Error:     "context cancelled",
				Timestamp: time.Now(),
			}
			return
		default:
			line := scanner.Text()

			// Skip empty lines or comments
			if line == "" || strings.HasPrefix(line, ":") {
				continue
			}

			// Parse SSE line: "data: {...}"
			if !strings.HasPrefix(line, "data: ") {
				continue
			}

			data := strings.TrimPrefix(line, "data: ")

			// Check for [DONE] signal
			if data == "[DONE]" {
				eventChan <- kernel.ChatEvent{
					Type:       kernel.EventTypeDone,
					SessionKey: sessionKey,
					Timestamp:  time.Now(),
				}
				return
			}

			// Parse JSON event
			var sseEvent map[string]interface{}
			if err := json.Unmarshal([]byte(data), &sseEvent); err != nil {
				log.Printf("⚠️  [QwenPawAdapter] Failed to parse SSE event: %v", err)
				continue
			}

			// Extract content
			content := extractQwenPawContent(sseEvent)
			if content != "" {
				eventChan <- kernel.ChatEvent{
					Type:       kernel.EventTypeDelta,
					Content:    content,
					SessionKey: sessionKey,
					Metadata:   sseEvent,
					Timestamp:  time.Now(),
				}
			}

			// Check for errors
			if errMsg, ok := sseEvent["error"].(string); ok && errMsg != "" {
				eventChan <- kernel.ChatEvent{
					Type:      kernel.EventTypeError,
					Error:     errMsg,
					Timestamp: time.Now(),
				}
				return
			}
		}
	}

	// Check scanner error
	if err := scanner.Err(); err != nil {
		eventChan <- kernel.ChatEvent{
			Type:      kernel.EventTypeError,
			Error:     fmt.Sprintf("SSE scanner error: %v", err),
			Timestamp: time.Now(),
		}
		return
	}

	// If we reach here without explicit [DONE], send done event
	eventChan <- kernel.ChatEvent{
		Type:       kernel.EventTypeDone,
		SessionKey: sessionKey,
		Timestamp:  time.Now(),
	}

	log.Printf("✅ [QwenPawAdapter] Stream completed")
}

// scanSSELines is a custom scanner split function for SSE events
func scanSSELines(data []byte, atEOF bool) (advance int, token []byte, err error) {
	if atEOF && len(data) == 0 {
		return 0, nil, nil
	}

	// Look for newline
	if i := bytes.IndexByte(data, '\n'); i >= 0 {
		// Return the line including the newline
		return i + 1, data[0:i], nil
	}

	// If at EOF, return remaining data
	if atEOF {
		return len(data), data, nil
	}

	// Request more data
	return 0, nil, nil
}

// extractQwenPawContent extracts text content from QwenPaw SSE event
func extractQwenPawContent(event map[string]interface{}) string {
	// Try different possible content fields based on QwenPaw's response format
	
	// Direct content field
	if content, ok := event["content"].(string); ok && content != "" {
		return content
	}

	// Nested in delta (similar to OpenAI format)
	if delta, ok := event["delta"].(map[string]interface{}); ok {
		if content, ok := delta["content"].(string); ok && content != "" {
			return content
		}
	}

	// Text field
	if text, ok := event["text"].(string); ok && text != "" {
		return text
	}

	// Choices format (OpenAI-compatible)
	if choices, ok := event["choices"].([]interface{}); ok && len(choices) > 0 {
		if choice, ok := choices[0].(map[string]interface{}); ok {
			if delta, ok := choice["delta"].(map[string]interface{}); ok {
				if content, ok := delta["content"].(string); ok && content != "" {
					return content
				}
			}
		}
	}

	return ""
}

// CreateAgent creates a new agent in QwenPaw
func (a *QwenPawAdapter) CreateAgent(ctx context.Context, agentID, workspace string) error {
	// QwenPaw manages agents through configuration files
	// Runtime agent creation may be done via API if supported
	log.Printf("📝 [QwenPawAdapter] CreateAgent called: agentID=%s, workspace=%s", agentID, workspace)
	return nil
}

// StartAgent starts an agent
func (a *QwenPawAdapter) StartAgent(ctx context.Context, agentID string) error {
	log.Printf("▶️  [QwenPawAdapter] StartAgent called: agentID=%s", agentID)
	return nil
}

// StopAgent stops an agent
func (a *QwenPawAdapter) StopAgent(ctx context.Context, agentID string) error {
	log.Printf("⏸️  [QwenPawAdapter] StopAgent called: agentID=%s", agentID)
	return nil
}

// HealthCheck verifies QwenPaw server is responsive
func (a *QwenPawAdapter) HealthCheck(ctx context.Context) error {
	healthURL := fmt.Sprintf("http://%s/api/version", a.config.Endpoint)

	req, err := http.NewRequestWithContext(ctx, "GET", healthURL, nil)
	if err != nil {
		return fmt.Errorf("failed to create request: %w", err)
	}

	resp, err := a.client.Do(req)
	if err != nil {
		return fmt.Errorf("health check failed: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return fmt.Errorf("health check returned HTTP %d", resp.StatusCode)
	}

	return nil
}

// Close releases resources (HTTP client doesn't need explicit closing)
func (a *QwenPawAdapter) Close() error {
	log.Printf("🔌 [QwenPawAdapter] Close called")
	// HTTP client will be garbage collected
	return nil
}

// GetKernelType returns the kernel type identifier
func (a *QwenPawAdapter) GetKernelType() string {
	return string(kernel.KernelTypeQwenPaw)
}

// min returns the minimum of two integers
func min(a, b int) int {
	if a < b {
		return a
	}
	return b
}
