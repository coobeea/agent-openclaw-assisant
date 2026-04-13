// Package adapters provides kernel adapter implementations
package adapters

import (
	"context"
	"encoding/json"
	"fmt"
	"log"
	"strings"
	"sync"
	"time"

	"github.com/gorilla/websocket"
	"openclaw-scheduler/internal/kernel"
)

// OpenClawAdapter implements KernelInterface for OpenClaw backend
type OpenClawAdapter struct {
	config *kernel.KernelConfig
	conn   *websocket.Conn
	connMu sync.RWMutex

	// Connection pool for multiple connections (if needed)
	connPool map[string]*websocket.Conn
	poolMu   sync.RWMutex

	// Metrics
	requestCount int64
	mu           sync.Mutex
}

// NewOpenClawAdapter creates a new OpenClaw adapter instance
func NewOpenClawAdapter() kernel.KernelInterface {
	return &OpenClawAdapter{
		connPool: make(map[string]*websocket.Conn),
	}
}

// Initialize establishes a WebSocket connection to OpenClaw Gateway
func (a *OpenClawAdapter) Initialize(ctx context.Context, config *kernel.KernelConfig) error {
	if config.Type != kernel.KernelTypeOpenClaw {
		return fmt.Errorf("invalid kernel type: expected 'openclaw', got '%s'", config.Type)
	}

	a.config = config

	// Establish WebSocket connection
	conn, err := a.connectToGateway(ctx)
	if err != nil {
		return fmt.Errorf("failed to connect to OpenClaw Gateway: %w", err)
	}

	a.connMu.Lock()
	a.conn = conn
	a.connMu.Unlock()

	log.Printf("✅ [OpenClawAdapter] Initialized successfully, endpoint: %s", config.Endpoint)
	return nil
}

// connectToGateway performs the complete WebSocket handshake with OpenClaw Gateway
func (a *OpenClawAdapter) connectToGateway(ctx context.Context) (*websocket.Conn, error) {
	// OpenClaw Gateway WebSocket endpoint (port 18789 for gateway)
	wsURL := fmt.Sprintf("ws://%s:18789", a.config.Endpoint)
	log.Printf("🔌 [OpenClawAdapter] Connecting to: %s", wsURL)

	// Create dialer with timeout
	dialer := websocket.Dialer{
		HandshakeTimeout: time.Duration(a.config.Timeout) * time.Second,
	}

	// Establish WebSocket connection
	conn, _, err := dialer.DialContext(ctx, wsURL, nil)
	if err != nil {
		return nil, fmt.Errorf("WebSocket dial failed: %w", err)
	}

	// Perform OpenClaw's connect.challenge handshake
	if err := a.performHandshake(conn); err != nil {
		conn.Close()
		return nil, fmt.Errorf("handshake failed: %w", err)
	}

	// Reset read deadline after handshake
	conn.SetReadDeadline(time.Time{})

	log.Printf("✅ [OpenClawAdapter] Connection established: %s", wsURL)
	return conn, nil
}

// performHandshake executes the OpenClaw connect.challenge handshake protocol
func (a *OpenClawAdapter) performHandshake(conn *websocket.Conn) error {
	// Step 1: Wait for server's connect.challenge event
	log.Printf("⏳ [OpenClawAdapter] Waiting for connect.challenge...")

	var challengeResp map[string]interface{}
	conn.SetReadDeadline(time.Now().Add(10 * time.Second))
	if err := conn.ReadJSON(&challengeResp); err != nil {
		return fmt.Errorf("failed to read challenge: %w", err)
	}

	// Verify it's a connect.challenge event
	respType, _ := challengeResp["type"].(string)
	if respType != "event" {
		return fmt.Errorf("expected event type, got: %s", respType)
	}

	event, _ := challengeResp["event"].(string)
	if event != "connect.challenge" {
		return fmt.Errorf("expected connect.challenge, got: %s", event)
	}

	// Extract nonce from challenge payload
	payload, _ := challengeResp["payload"].(map[string]interface{})
	nonce, _ := payload["nonce"].(string)

	log.Printf("✅ [OpenClawAdapter] Received connect.challenge, nonce: %s", nonce)

	// Step 2: Send connect request with authentication
	connectParams := map[string]interface{}{
		"minProtocol": 3,
		"maxProtocol": 3,
		"client": map[string]interface{}{
			"id":       "gateway-client",
			"mode":     "backend",
			"version":  "1.0.0",
			"platform": "linux",
		},
		"role":   "operator",
		"scopes": []string{"operator.admin"},
		"caps":   []string{},
	}

	// Add authentication if configured
	if a.config.Auth != nil && a.config.Auth.Type == "token" && a.config.Auth.Token != "" {
		connectParams["auth"] = map[string]interface{}{
			"token": a.config.Auth.Token,
		}
	}

	connectReq := map[string]interface{}{
		"type":   "req",
		"id":     fmt.Sprintf("connect-%d", time.Now().UnixNano()),
		"method": "connect",
		"params": connectParams,
	}

	// Serialize and send connect request
	jsonBytes, err := json.Marshal(connectReq)
	if err != nil {
		return fmt.Errorf("failed to marshal connect request: %w", err)
	}

	log.Printf("📤 [OpenClawAdapter] Sending connect request...")

	if err := conn.WriteMessage(websocket.TextMessage, jsonBytes); err != nil {
		return fmt.Errorf("failed to send connect request: %w", err)
	}

	// Step 3: Wait for connect response
	var connectResp map[string]interface{}
	if err := conn.ReadJSON(&connectResp); err != nil {
		return fmt.Errorf("failed to read connect response: %w", err)
	}

	// Verify successful response
	finalType, _ := connectResp["type"].(string)
	if finalType != "res" {
		return fmt.Errorf("unexpected response type: %s", finalType)
	}

	ok, _ := connectResp["ok"].(bool)
	if !ok {
		// Extract error details
		if errData, exists := connectResp["error"].(map[string]interface{}); exists {
			if msg, exists := errData["message"].(string); exists {
				return fmt.Errorf("connect rejected: %s", msg)
			}
		}
		return fmt.Errorf("connect rejected: %+v", connectResp)
	}

	log.Printf("✅ [OpenClawAdapter] Handshake successful")
	return nil
}

// StreamChat sends a chat message and returns a channel for streaming responses
func (a *OpenClawAdapter) StreamChat(ctx context.Context, req *kernel.ChatRequest) (<-chan kernel.ChatEvent, error) {
	a.connMu.RLock()
	conn := a.conn
	a.connMu.RUnlock()

	if conn == nil {
		return nil, fmt.Errorf("not connected to OpenClaw Gateway")
	}

	// Create event channel
	eventChan := make(chan kernel.ChatEvent, 100)

	// Generate request ID for idempotency
	requestID := req.RequestID
	if requestID == "" {
		requestID = fmt.Sprintf("req-%d", time.Now().UnixNano())
	}

	// Construct chat.send RPC request
	chatReq := map[string]interface{}{
		"type":   "req",
		"method": "chat.send",
		"id":     requestID,
		"params": map[string]interface{}{
			"message":        req.Message,
			"sessionKey":     fmt.Sprintf("agent:main:%s", req.SessionKey),
			"idempotencyKey": requestID,
		},
	}

	// Send chat request
	if err := conn.WriteJSON(chatReq); err != nil {
		close(eventChan)
		return nil, fmt.Errorf("failed to send chat request: %w", err)
	}

	log.Printf("📤 [OpenClawAdapter] Sent chat.send request: %s", requestID)

	// Start listening for events in a goroutine
	go a.listenForEvents(ctx, conn, requestID, req.SessionKey, eventChan)

	return eventChan, nil
}

// listenForEvents listens for WebSocket frames and converts them to ChatEvents
func (a *OpenClawAdapter) listenForEvents(ctx context.Context, conn *websocket.Conn, requestID, sessionKey string, eventChan chan<- kernel.ChatEvent) {
	defer close(eventChan)

	done := false
	for !done {
		select {
		case <-ctx.Done():
			eventChan <- kernel.ChatEvent{
				Type:      kernel.EventTypeError,
				Error:     "context cancelled",
				Timestamp: time.Now(),
			}
			return
		default:
			// Set read deadline
			conn.SetReadDeadline(time.Now().Add(60 * time.Second))

			var frame map[string]interface{}
			if err := conn.ReadJSON(&frame); err != nil {
				if netErr, ok := err.(interface{ Timeout() bool }); ok && netErr.Timeout() {
					// Timeout - normal for long waits
					continue
				}
				eventChan <- kernel.ChatEvent{
					Type:      kernel.EventTypeError,
					Error:     fmt.Sprintf("WebSocket read error: %v", err),
					Timestamp: time.Now(),
				}
				return
			}

			// Process frame
			frameType, _ := frame["type"].(string)

			// Handle RPC response
			if frameType == "res" {
				resID, _ := frame["id"].(string)
				if resID == requestID {
					ok, _ := frame["ok"].(bool)
					if !ok {
						// Request rejected
						var errorMsg string
						if payload, exists := frame["error"].(map[string]interface{}); exists {
							if msg, exists := payload["message"].(string); exists {
								errorMsg = msg
							}
						}
						if errorMsg == "" {
							errorMsg = "request rejected"
						}
						eventChan <- kernel.ChatEvent{
							Type:      kernel.EventTypeError,
							Error:     errorMsg,
							Timestamp: time.Now(),
						}
						done = true
					}
					// Request accepted, continue listening for events
				}
			}

			// Handle events
			if frameType == "event" {
				eventName, _ := frame["event"].(string)

				// Process chat events
				if eventName == "chat" {
					payload, _ := frame["payload"].(map[string]interface{})
					payloadSessionKey, _ := payload["sessionKey"].(string)

					// Match session key (OpenClaw prepends "agent:main:")
					if strings.Contains(payloadSessionKey, sessionKey) {
						state, _ := payload["state"].(string)

						if state == "delta" {
							// Extract content
							content := extractContent(payload)
							if content != "" {
								eventChan <- kernel.ChatEvent{
									Type:       kernel.EventTypeDelta,
									Content:    content,
									SessionKey: sessionKey,
									Timestamp:  time.Now(),
								}
							}
						} else if state == "done" {
							// Stream complete
							eventChan <- kernel.ChatEvent{
								Type:       kernel.EventTypeDone,
								SessionKey: sessionKey,
								Timestamp:  time.Now(),
							}
							done = true
						}
					}
				}
			}
		}
	}
}

// extractContent extracts text content from OpenClaw chat event payload
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

// CreateAgent creates a new agent (executed via kubectl exec)
func (a *OpenClawAdapter) CreateAgent(ctx context.Context, agentID, workspace string) error {
	// This would typically call kubectl exec to run "openclaw agents add"
	// For now, we'll assume this is handled elsewhere (in k8s package)
	log.Printf("📝 [OpenClawAdapter] CreateAgent called: agentID=%s, workspace=%s", agentID, workspace)
	return nil
}

// StartAgent starts an agent (if supported by OpenClaw)
func (a *OpenClawAdapter) StartAgent(ctx context.Context, agentID string) error {
	// OpenClaw agents are started automatically
	log.Printf("▶️  [OpenClawAdapter] StartAgent called: agentID=%s", agentID)
	return nil
}

// StopAgent stops an agent (if supported by OpenClaw)
func (a *OpenClawAdapter) StopAgent(ctx context.Context, agentID string) error {
	// OpenClaw agents are managed per-session
	log.Printf("⏸️  [OpenClawAdapter] StopAgent called: agentID=%s", agentID)
	return nil
}

// HealthCheck verifies the OpenClaw Gateway is responsive
func (a *OpenClawAdapter) HealthCheck(ctx context.Context) error {
	a.connMu.RLock()
	conn := a.conn
	a.connMu.RUnlock()

	if conn == nil {
		return fmt.Errorf("not connected")
	}

	// Send a ping frame
	deadline := time.Now().Add(5 * time.Second)
	if err := conn.WriteControl(websocket.PingMessage, []byte{}, deadline); err != nil {
		return fmt.Errorf("ping failed: %w", err)
	}

	return nil
}

// Close releases resources and closes the WebSocket connection
func (a *OpenClawAdapter) Close() error {
	a.connMu.Lock()
	defer a.connMu.Unlock()

	if a.conn != nil {
		log.Printf("🔌 [OpenClawAdapter] Closing connection")
		err := a.conn.Close()
		a.conn = nil
		return err
	}

	return nil
}

// GetKernelType returns the kernel type identifier
func (a *OpenClawAdapter) GetKernelType() string {
	return string(kernel.KernelTypeOpenClaw)
}
