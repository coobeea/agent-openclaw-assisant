package db

import (
	"database/sql"
	"fmt"
	"log"
	"os"
	"time"

	_ "github.com/lib/pq"
	"openclaw-scheduler/internal/models"
)

var DB *sql.DB

// InitDB 初始化数据库连接
func InitDB() error {
	host := getEnv("POSTGRES_HOST", "postgres")
	port := getEnv("POSTGRES_PORT", "5432")
	dbName := getEnv("POSTGRES_DB", "openclaw")
	user := getEnv("POSTGRES_USER", "postgres")
	password := getEnv("POSTGRES_PASSWORD", "openclaw123")

	dsn := fmt.Sprintf("host=%s port=%s user=%s password=%s dbname=%s sslmode=disable",
		host, port, user, password, dbName)

	var err error
	// 重试连接
	for i := 0; i < 30; i++ {
		DB, err = sql.Open("postgres", dsn)
		if err == nil {
			err = DB.Ping()
			if err == nil {
				log.Println("✅ 数据库连接成功")
				return createTables()
			}
		}
		log.Printf("⏳ 等待数据库就绪... (%d/30)", i+1)
		time.Sleep(2 * time.Second)
	}

	return fmt.Errorf("无法连接到数据库: %v", err)
}

// createTables 创建数据库表
func createTables() error {
	queries := []string{
		`CREATE TABLE IF NOT EXISTS users (
			id SERIAL PRIMARY KEY,
			username VARCHAR(100) UNIQUE NOT NULL,
			password VARCHAR(255) NOT NULL,
			created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
		)`,
		`CREATE TABLE IF NOT EXISTS agents (
			id SERIAL PRIMARY KEY,
			agent_id VARCHAR(100) UNIQUE NOT NULL,
			user_id INTEGER REFERENCES users(id),
			name VARCHAR(200) NOT NULL,
			description TEXT,
			workspace_path VARCHAR(500),
			created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
			updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
		)`,
		`CREATE TABLE IF NOT EXISTS conversations (
			id SERIAL PRIMARY KEY,
			agent_id VARCHAR(100) REFERENCES agents(agent_id),
			user_message TEXT NOT NULL,
			agent_response TEXT,
			created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
		)`,
	}

	for _, query := range queries {
		if _, err := DB.Exec(query); err != nil {
			return fmt.Errorf("创建表失败: %v", err)
		}
	}

	log.Println("✅ 数据库表初始化成功")
	return nil
}

// ========== 用户相关 ==========

// CreateUser 创建用户
func CreateUser(username, password string) (*models.User, error) {
	var user models.User
	err := DB.QueryRow(
		"INSERT INTO users (username, password) VALUES ($1, $2) RETURNING id, username, created_at",
		username, password,
	).Scan(&user.ID, &user.Username, &user.CreatedAt)
	
	if err != nil {
		return nil, err
	}
	return &user, nil
}

// GetUserByCredentials 根据用户名密码获取用户
func GetUserByCredentials(username, password string) (*models.User, error) {
	var user models.User
	err := DB.QueryRow(
		"SELECT id, username, created_at FROM users WHERE username = $1 AND password = $2",
		username, password,
	).Scan(&user.ID, &user.Username, &user.CreatedAt)
	
	if err != nil {
		return nil, err
	}
	return &user, nil
}

// ========== 智能体相关 ==========

// CreateAgent 创建智能体
func CreateAgent(agentID string, userID int, name, description, workspacePath string) (*models.Agent, error) {
	return CreateAgentWithKernel(agentID, userID, name, description, workspacePath, "openclaw")
}

// CreateAgentWithKernel 创建智能体（支持内核选择）
func CreateAgentWithKernel(agentID string, userID int, name, description, workspacePath, kernelType string) (*models.Agent, error) {
	// 构建 config JSON
	configJSON := fmt.Sprintf(`{"kernel_type": "%s"}`, kernelType)
	
	var agent models.Agent
	var configStr sql.NullString
	
	err := DB.QueryRow(
		`INSERT INTO agents (agent_id, user_id, name, description, workspace_path, config)
		VALUES ($1, $2, $3, $4, $5, $6::jsonb)
		RETURNING id, agent_id, user_id, name, description, workspace_path, config, created_at, updated_at`,
		agentID, userID, name, description, workspacePath, configJSON,
	).Scan(&agent.ID, &agent.AgentID, &agent.UserID, &agent.Name,
		&agent.Description, &agent.WorkspacePath, &configStr, &agent.CreatedAt, &agent.UpdatedAt)
	
	if err != nil {
		return nil, err
	}
	
	// 解析 config
	if configStr.Valid {
		agent.Config = configStr.String
	}
	
	return &agent, nil
}

// ListAgents 列出智能体
func ListAgents(userID int) ([]models.Agent, error) {
	query := "SELECT id, agent_id, user_id, name, description, workspace_path, config, created_at, updated_at FROM agents"
	args := []interface{}{}
	
	if userID > 0 {
		query += " WHERE user_id = $1"
		args = append(args, userID)
	}
	query += " ORDER BY created_at DESC"

	rows, err := DB.Query(query, args...)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var agents []models.Agent
	for rows.Next() {
		var agent models.Agent
		var configStr sql.NullString
		
		err := rows.Scan(&agent.ID, &agent.AgentID, &agent.UserID, &agent.Name,
			&agent.Description, &agent.WorkspacePath, &configStr, &agent.CreatedAt, &agent.UpdatedAt)
		if err != nil {
			continue
		}
		
		// 解析 config
		if configStr.Valid {
			agent.Config = configStr.String
		}
		
		agents = append(agents, agent)
	}
	
	return agents, nil
}

// ========== 对话相关 ==========

// CreateConversation 创建对话记录
func CreateConversation(agentID, userMessage, agentResponse string) (*models.Conversation, error) {
	var conv models.Conversation
	err := DB.QueryRow(
		`INSERT INTO conversations (agent_id, user_message, agent_response)
		VALUES ($1, $2, $3)
		RETURNING id, agent_id, user_message, agent_response, created_at`,
		agentID, userMessage, agentResponse,
	).Scan(&conv.ID, &conv.AgentID, &conv.UserMessage, &conv.AgentResponse, &conv.CreatedAt)
	
	if err != nil {
		return nil, err
	}
	return &conv, nil
}

// GetConversationHistory 获取对话历史
func GetConversationHistory(agentID string, limit int) ([]models.Conversation, error) {
	if limit <= 0 {
		limit = 50
	}

	rows, err := DB.Query(
		`SELECT id, agent_id, user_message, agent_response, created_at
		FROM conversations
		WHERE agent_id = $1
		ORDER BY created_at DESC
		LIMIT $2`,
		agentID, limit,
	)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var history []models.Conversation
	for rows.Next() {
		var conv models.Conversation
		err := rows.Scan(&conv.ID, &conv.AgentID, &conv.UserMessage,
			&conv.AgentResponse, &conv.CreatedAt)
		if err != nil {
			continue
		}
		history = append(history, conv)
	}
	
	// 反转顺序（最早的在前）
	for i, j := 0, len(history)-1; i < j; i, j = i+1, j-1 {
		history[i], history[j] = history[j], history[i]
	}
	
	return history, nil
}

// getEnv 获取环境变量，带默认值
func getEnv(key, defaultValue string) string {
	if value := os.Getenv(key); value != "" {
		return value
	}
	return defaultValue
}
