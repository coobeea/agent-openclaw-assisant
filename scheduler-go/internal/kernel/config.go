// Package kernel provides configuration structures for kernel backends
package kernel

import (
	"fmt"
	"time"
)

// KernelType represents the type of kernel backend
type KernelType string

const (
	// KernelTypeOpenClaw represents OpenClaw kernel
	KernelTypeOpenClaw KernelType = "openclaw"

	// KernelTypeQwenPaw represents QwenPaw kernel
	KernelTypeQwenPaw KernelType = "qwenpaw"
)

// KernelConfig contains configuration for a kernel backend
type KernelConfig struct {
	// Type specifies which kernel to use ("openclaw" | "qwenpaw")
	Type KernelType `json:"type"`

	// Endpoint is the network address of the kernel (e.g., "10.1.2.3:3000")
	Endpoint string `json:"endpoint"`

	// Auth contains authentication configuration
	Auth *AuthConfig `json:"auth,omitempty"`

	// Timeout is the default timeout for operations (in seconds)
	Timeout int `json:"timeout"`

	// Extra contains kernel-specific configuration
	Extra map[string]string `json:"extra,omitempty"`

	// RetryPolicy defines retry behavior
	RetryPolicy *RetryPolicy `json:"retry_policy,omitempty"`

	// ConnectionPool defines connection pool settings
	ConnectionPool *ConnectionPoolConfig `json:"connection_pool,omitempty"`
}

// AuthConfig contains authentication settings
type AuthConfig struct {
	// Type specifies auth method: "token", "basic", "none"
	Type string `json:"type"`

	// Token for token-based authentication
	Token string `json:"token,omitempty"`

	// User for basic authentication
	User string `json:"user,omitempty"`

	// Pass for basic authentication
	Pass string `json:"pass,omitempty"`

	// Extra contains auth-specific parameters
	Extra map[string]string `json:"extra,omitempty"`
}

// RetryPolicy defines retry behavior for failed operations
type RetryPolicy struct {
	// MaxRetries is the maximum number of retry attempts
	MaxRetries int `json:"max_retries"`

	// InitialBackoff is the initial backoff duration
	InitialBackoff time.Duration `json:"initial_backoff"`

	// MaxBackoff is the maximum backoff duration
	MaxBackoff time.Duration `json:"max_backoff"`

	// BackoffMultiplier is the multiplier for exponential backoff
	BackoffMultiplier float64 `json:"backoff_multiplier"`
}

// ConnectionPoolConfig defines connection pool settings
type ConnectionPoolConfig struct {
	// MaxConnections is the maximum number of connections in the pool
	MaxConnections int `json:"max_connections"`

	// MinIdleConnections is the minimum number of idle connections to maintain
	MinIdleConnections int `json:"min_idle_connections"`

	// MaxIdleTime is the maximum time a connection can be idle
	MaxIdleTime time.Duration `json:"max_idle_time"`

	// ConnectionTimeout is the timeout for establishing a new connection
	ConnectionTimeout time.Duration `json:"connection_timeout"`

	// HealthCheckInterval is the interval for connection health checks
	HealthCheckInterval time.Duration `json:"health_check_interval"`
}

// Validate checks if the kernel configuration is valid
func (c *KernelConfig) Validate() error {
	if c.Type == "" {
		return fmt.Errorf("kernel type is required")
	}

	if c.Type != KernelTypeOpenClaw && c.Type != KernelTypeQwenPaw {
		return fmt.Errorf("invalid kernel type: %s (must be 'openclaw' or 'qwenpaw')", c.Type)
	}

	if c.Endpoint == "" {
		return fmt.Errorf("kernel endpoint is required")
	}

	if c.Timeout <= 0 {
		return fmt.Errorf("kernel timeout must be positive, got: %d", c.Timeout)
	}

	// Validate auth config if present
	if c.Auth != nil {
		if err := c.Auth.Validate(); err != nil {
			return fmt.Errorf("invalid auth config: %w", err)
		}
	}

	return nil
}

// Validate checks if the auth configuration is valid
func (a *AuthConfig) Validate() error {
	validTypes := map[string]bool{
		"token": true,
		"basic": true,
		"none":  true,
	}

	if !validTypes[a.Type] {
		return fmt.Errorf("invalid auth type: %s (must be 'token', 'basic', or 'none')", a.Type)
	}

	if a.Type == "token" && a.Token == "" {
		return fmt.Errorf("token is required for token-based auth")
	}

	if a.Type == "basic" && (a.User == "" || a.Pass == "") {
		return fmt.Errorf("user and pass are required for basic auth")
	}

	return nil
}

// DefaultKernelConfig returns a default kernel configuration
func DefaultKernelConfig(kernelType KernelType, endpoint string) *KernelConfig {
	return &KernelConfig{
		Type:     kernelType,
		Endpoint: endpoint,
		Timeout:  60,
		Auth: &AuthConfig{
			Type: "none",
		},
		RetryPolicy: &RetryPolicy{
			MaxRetries:        3,
			InitialBackoff:    1 * time.Second,
			MaxBackoff:        30 * time.Second,
			BackoffMultiplier: 2.0,
		},
		ConnectionPool: &ConnectionPoolConfig{
			MaxConnections:      10,
			MinIdleConnections:  2,
			MaxIdleTime:         5 * time.Minute,
			ConnectionTimeout:   10 * time.Second,
			HealthCheckInterval: 30 * time.Second,
		},
		Extra: make(map[string]string),
	}
}

// DefaultOpenClawConfig returns a default OpenClaw configuration
func DefaultOpenClawConfig(endpoint, token string) *KernelConfig {
	config := DefaultKernelConfig(KernelTypeOpenClaw, endpoint)
	config.Auth = &AuthConfig{
		Type:  "token",
		Token: token,
	}
	// OpenClaw-specific defaults
	config.Extra["protocol"] = "websocket"
	config.Extra["port"] = "3000"
	return config
}

// DefaultQwenPawConfig returns a default QwenPaw configuration
func DefaultQwenPawConfig(endpoint string) *KernelConfig {
	config := DefaultKernelConfig(KernelTypeQwenPaw, endpoint)
	config.Auth = &AuthConfig{
		Type: "none", // QwenPaw may not require auth in local deployment
	}
	// QwenPaw-specific defaults
	config.Extra["protocol"] = "http"
	config.Extra["port"] = "8088"
	return config
}

// Clone creates a deep copy of the configuration
func (c *KernelConfig) Clone() *KernelConfig {
	clone := &KernelConfig{
		Type:     c.Type,
		Endpoint: c.Endpoint,
		Timeout:  c.Timeout,
		Extra:    make(map[string]string),
	}

	if c.Auth != nil {
		clone.Auth = &AuthConfig{
			Type:  c.Auth.Type,
			Token: c.Auth.Token,
			User:  c.Auth.User,
			Pass:  c.Auth.Pass,
			Extra: make(map[string]string),
		}
		for k, v := range c.Auth.Extra {
			clone.Auth.Extra[k] = v
		}
	}

	for k, v := range c.Extra {
		clone.Extra[k] = v
	}

	if c.RetryPolicy != nil {
		clone.RetryPolicy = &RetryPolicy{
			MaxRetries:        c.RetryPolicy.MaxRetries,
			InitialBackoff:    c.RetryPolicy.InitialBackoff,
			MaxBackoff:        c.RetryPolicy.MaxBackoff,
			BackoffMultiplier: c.RetryPolicy.BackoffMultiplier,
		}
	}

	if c.ConnectionPool != nil {
		clone.ConnectionPool = &ConnectionPoolConfig{
			MaxConnections:      c.ConnectionPool.MaxConnections,
			MinIdleConnections:  c.ConnectionPool.MinIdleConnections,
			MaxIdleTime:         c.ConnectionPool.MaxIdleTime,
			ConnectionTimeout:   c.ConnectionPool.ConnectionTimeout,
			HealthCheckInterval: c.ConnectionPool.HealthCheckInterval,
		}
	}

	return clone
}
