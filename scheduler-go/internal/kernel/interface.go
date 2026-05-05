// Package kernel provides a unified interface for different AI kernel backends
// (e.g., OpenClaw, QwenPaw) to enable flexible kernel switching.
package kernel

import (
	"context"
	"time"
)

// KernelInterface defines the unified interface that all kernel adapters must implement.
// This abstraction allows the scheduler to work with different backends (OpenClaw, QwenPaw)
// without changing the core business logic.
type KernelInterface interface {
	// Initialize establishes connection to the kernel backend
	Initialize(ctx context.Context, config *KernelConfig) error

	// StreamChat sends a chat message and returns a channel for streaming responses
	StreamChat(ctx context.Context, req *ChatRequest) (<-chan ChatEvent, error)

	// CreateAgent creates a new agent in the kernel (if supported)
	CreateAgent(ctx context.Context, agentID, workspace string) error

	// StartAgent starts an existing agent (if supported)
	StartAgent(ctx context.Context, agentID string) error

	// StopAgent stops a running agent (if supported)
	StopAgent(ctx context.Context, agentID string) error

	// HealthCheck verifies the kernel is responsive
	HealthCheck(ctx context.Context) error

	// Close releases resources and closes connections
	Close() error

	// GetKernelType returns the type of this kernel (e.g., "openclaw", "qwenpaw")
	GetKernelType() string
}

// ChatRequest represents a unified chat request format across all kernels
type ChatRequest struct {
	// AgentID is the unique identifier for the agent
	AgentID string `json:"agent_id"`

	// SessionKey is the session identifier for the conversation
	SessionKey string `json:"session_key"`

	// Message is the user's input message
	Message string `json:"message"`

	// UserID is the identifier of the user sending the message
	UserID string `json:"user_id,omitempty"`

	// WorkspacePath is the agent's workspace directory path
	WorkspacePath string `json:"workspace_path,omitempty"`

	// Context contains additional metadata for the request
	Context map[string]string `json:"context,omitempty"`

	// RequestID is a unique identifier for this request (for idempotency)
	RequestID string `json:"request_id,omitempty"`
}

// ChatEvent represents a unified streaming event from the kernel
type ChatEvent struct {
	// Type indicates the event type: "delta" (incremental content),
	// "done" (stream complete), "error" (error occurred)
	Type string `json:"type"`

	// Content contains the incremental text content (for Type="delta")
	Content string `json:"content,omitempty"`

	// SessionKey identifies which session this event belongs to
	SessionKey string `json:"session_key,omitempty"`

	// Error contains error message (for Type="error")
	Error string `json:"error,omitempty"`

	// Metadata contains additional event metadata
	Metadata map[string]interface{} `json:"metadata,omitempty"`

	// Timestamp is when this event was generated
	Timestamp time.Time `json:"timestamp"`
}

// EventType constants for ChatEvent.Type
const (
	EventTypeDelta = "delta" // Incremental content chunk
	EventTypeDone  = "done"  // Stream completed successfully
	EventTypeError = "error" // Error occurred
	EventTypeStart = "start" // Stream started
)

// AgentInfo represents agent metadata
type AgentInfo struct {
	AgentID   string    `json:"agent_id"`
	Name      string    `json:"name,omitempty"`
	Workspace string    `json:"workspace,omitempty"`
	Status    string    `json:"status,omitempty"`
	CreatedAt time.Time `json:"created_at,omitempty"`
}

// KernelMetrics contains performance metrics for a kernel
type KernelMetrics struct {
	TotalRequests     int64         `json:"total_requests"`
	SuccessfulStreams int64         `json:"successful_streams"`
	FailedStreams     int64         `json:"failed_streams"`
	AverageLatency    time.Duration `json:"average_latency"`
	ActiveConnections int           `json:"active_connections"`
}

// StreamOptions contains optional parameters for streaming
type StreamOptions struct {
	// Timeout for the entire stream (0 = no timeout)
	Timeout time.Duration

	// MaxRetries for transient failures
	MaxRetries int

	// BufferSize for the event channel
	BufferSize int
}

// DefaultStreamOptions returns sensible defaults for streaming
func DefaultStreamOptions() *StreamOptions {
	return &StreamOptions{
		Timeout:    5 * time.Minute,
		MaxRetries: 3,
		BufferSize: 100,
	}
}
