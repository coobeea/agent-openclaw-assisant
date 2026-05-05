package models

import "time"

// User 用户模型
type User struct {
	ID        int       `json:"id" db:"id"`
	Username  string    `json:"username" db:"username"`
	Password  string    `json:"password,omitempty" db:"password"`
	CreatedAt time.Time `json:"created_at" db:"created_at"`
}

// Agent 智能体模型
type Agent struct {
	ID            int       `json:"id" db:"id"`
	AgentID       string    `json:"agent_id" db:"agent_id"`
	UserID        int       `json:"user_id" db:"user_id"`
	Name          string    `json:"name" db:"name"`
	Description   string    `json:"description" db:"description"`
	Config        string    `json:"config" db:"config"`  // JSONB 字段，包含 kernel_type 等配置
	WorkspacePath string    `json:"workspace_path" db:"workspace_path"`
	CreatedAt     time.Time `json:"created_at" db:"created_at"`
	UpdatedAt     time.Time `json:"updated_at" db:"updated_at"`
}

// Conversation 对话记录
type Conversation struct {
	ID            int       `json:"id" db:"id"`
	AgentID       string    `json:"agent_id" db:"agent_id"`
	UserMessage   string    `json:"user_message" db:"user_message"`
	AgentResponse string    `json:"agent_response" db:"agent_response"`
	CreatedAt     time.Time `json:"created_at" db:"created_at"`
}

// ContainerStatus 容器状态
type ContainerStatus struct {
	PodName   string `json:"pod"`
	Status    string `json:"status"`    // idle, busy
	AgentID   string `json:"agent_id"`
	Phase     string `json:"phase"`     // Running, Pending
	IP        string `json:"ip"`
	Node      string `json:"node"`
}
