package websocket

import (
	"encoding/json"
	"fmt"
	"log"
	"sync"
	"time"

	"github.com/gorilla/websocket"
)

// Pool WebSocket 连接池
type Pool struct {
	conns map[string]*websocket.Conn
	mu    sync.RWMutex
}

// NewPool 创建连接池
func NewPool() *Pool {
	return &Pool{
		conns: make(map[string]*websocket.Conn),
	}
}

// GetConn 获取或创建 WebSocket 连接（复用已有连接）
func (p *Pool) GetConn(podIP string) (*websocket.Conn, error) {
	// 1. 尝试获取已有连接
	p.mu.RLock()
	if conn, ok := p.conns[podIP]; ok && conn != nil {
		// 检查连接是否有效（发送 ping）
		err := conn.WriteControl(websocket.PingMessage, []byte{}, time.Now().Add(time.Second))
		if err == nil {
			p.mu.RUnlock()
			log.Printf("♻️  [WSPool] 复用连接: %s", podIP)
			return conn, nil
		}
		// 连接已断开
		log.Printf("⚠️  [WSPool] 连接已断开: %s, 将重建", podIP)
	}
	p.mu.RUnlock()

	// 2. 创建新连接
	p.mu.Lock()
	defer p.mu.Unlock()

	// 再次检查（防止并发重复创建）
	if conn, ok := p.conns[podIP]; ok && conn != nil {
		return conn, nil
	}

	url := fmt.Sprintf("ws://%s:18789", podIP)
	log.Printf("🔌 [WSPool] 建立新连接: %s", url)

	dialer := websocket.Dialer{
		HandshakeTimeout: 10 * time.Second,
	}
	
	conn, _, err := dialer.Dial(url, nil)
	if err != nil {
		return nil, fmt.Errorf("连接失败: %v", err)
	}

	// 🔑 关键修复：连接打开后，不要主动发送任何消息！
	// OpenClaw 会主动发送 connect.challenge 事件，我们只需要等待接收

	// 等待服务器发送 connect.challenge 事件
	log.Printf("⏳ [WSPool] 等待服务器发送 connect.challenge...")
	
	var challengeResp map[string]interface{}
	conn.SetReadDeadline(time.Now().Add(10 * time.Second))
	if err := conn.ReadJSON(&challengeResp); err != nil {
		conn.Close()
		return nil, fmt.Errorf("等待 challenge 失败: %v", err)
	}

	// 处理 connect.challenge
	respType, _ := challengeResp["type"].(string)
	if respType == "event" {
		event, _ := challengeResp["event"].(string)
		if event == "connect.challenge" {
			payload, _ := challengeResp["payload"].(map[string]interface{})
			nonce, _ := payload["nonce"].(string)
			
			log.Printf("⚠️  [WSPool] 收到 connect.challenge，nonce: %s（使用最简认证）", nonce)
			
			// 参考 Control UI 的 connect 请求格式（完全匹配）
			// 注意：Control UI 中如果 auth/device 是 undefined，JSON.stringify 会忽略它们
			// 在 Go 中我们需要显式地不添加这些字段，而不是设为 nil
			params := map[string]interface{}{
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
				// 添加认证 token（匹配 OpenClaw 配置）
				"auth": map[string]interface{}{
					"token": "openclaw-internal-k8s-token",
				},
			}
			
			// Control UI 会添加这些可选字段（如果有的话）
			// 我们暂不添加 auth 和 device，依赖 auth.mode=none
			
			connectReq := map[string]interface{}{
				"type":   "req",
				"id":     "connect-1",
				"method": "connect",
				"params": params,
			}
			
			// 手动序列化 JSON（确保格式正确）
			jsonBytes, err := json.Marshal(connectReq)
			if err != nil {
				conn.Close()
				return nil, fmt.Errorf("JSON 序列化失败: %v", err)
			}
			
			log.Printf("📤 [WSPool] 发送 connect 请求 JSON: %s", string(jsonBytes))
			
			// 使用 WriteMessage 而不是 WriteJSON，确保完全控制格式
			if err := conn.WriteMessage(websocket.TextMessage, jsonBytes); err != nil {
				conn.Close()
				return nil, fmt.Errorf("发送 connect 请求失败: %v", err)
			}
			
			log.Printf("✅ [WSPool] connect 请求已发送，等待响应...")
			
			// 等待最终的 HelloOk 响应
			var finalResp map[string]interface{}
			if err := conn.ReadJSON(&finalResp); err != nil {
				conn.Close()
				return nil, fmt.Errorf("握手响应失败: %v", err)
			}
			
			// 详细打印响应内容
			respJSON, _ := json.MarshalIndent(finalResp, "", "  ")
			log.Printf("📥 [WSPool] 收到响应:\n%s", string(respJSON))
			
			finalType, _ := finalResp["type"].(string)
			if finalType == "res" {
				ok, _ := finalResp["ok"].(bool)
				if !ok {
					// 打印详细的错误信息
					if errData, ok := finalResp["error"].(map[string]interface{}); ok {
						errJSON, _ := json.MarshalIndent(errData, "", "  ")
						log.Printf("❌ [WSPool] 服务器错误:\n%s", string(errJSON))
						if msg, ok := errData["message"].(string); ok {
							conn.Close()
							return nil, fmt.Errorf("握手失败: %s", msg)
						}
					}
					conn.Close()
					return nil, fmt.Errorf("握手失败: %+v", finalResp)
				}
				log.Printf("✅ [WSPool] HelloOk 收到，连接成功")
			} else {
				conn.Close()
				return nil, fmt.Errorf("握手失败，收到未知响应类型: %s", finalType)
			}
		}
	} else if respType != "hello-ok" {
		conn.Close()
		errMsg, _ := json.Marshal(challengeResp)
		return nil, fmt.Errorf("握手失败: %s", errMsg)
	}
	
	conn.SetReadDeadline(time.Time{}) // 取消超时

	log.Printf("✅ [WSPool] 连接成功: %s", url)

	// 保存连接
	p.conns[podIP] = conn

	// 启动后台监听（检测断开）
	go p.monitorConnection(podIP, conn)

	return conn, nil
}

// monitorConnection 监听连接断开
func (p *Pool) monitorConnection(podIP string, conn *websocket.Conn) {
	defer func() {
		p.mu.Lock()
		delete(p.conns, podIP)
		p.mu.Unlock()
		conn.Close()
		log.Printf("🔌 [WSPool] 连接已关闭: %s", podIP)
	}()

	// 设置 pong 处理器
	conn.SetPongHandler(func(string) error {
		conn.SetReadDeadline(time.Now().Add(60 * time.Second))
		return nil
	})

	// 设置读超时
	conn.SetReadDeadline(time.Now().Add(60 * time.Second))

	// 启动心跳
	ticker := time.NewTicker(30 * time.Second)
	defer ticker.Stop()

	go func() {
		for range ticker.C {
			if err := conn.WriteControl(websocket.PingMessage, []byte{}, time.Now().Add(10*time.Second)); err != nil {
				log.Printf("⚠️  [WSPool] Ping 失败: %s, %v", podIP, err)
				return
			}
		}
	}()

	// 持续读取消息（由具体业务处理）
	// 这里只是保持连接活跃，不处理业务消息
	for {
		_, _, err := conn.ReadMessage()
		if err != nil {
			log.Printf("⚠️  [WSPool] 连接断开: %s, 错误: %v", podIP, err)
			return
		}
	}
}

// Close 关闭指定连接
func (p *Pool) Close(podIP string) {
	p.mu.Lock()
	defer p.mu.Unlock()

	if conn, ok := p.conns[podIP]; ok {
		conn.Close()
		delete(p.conns, podIP)
		log.Printf("🔌 [WSPool] 关闭连接: %s", podIP)
	}
}

// CloseAll 关闭所有连接
func (p *Pool) CloseAll() {
	p.mu.Lock()
	defer p.mu.Unlock()

	for podIP, conn := range p.conns {
		conn.Close()
		log.Printf("🔌 [WSPool] 关闭连接: %s", podIP)
	}
	p.conns = make(map[string]*websocket.Conn)
}

// GetStats 获取连接池统计
func (p *Pool) GetStats() map[string]interface{} {
	p.mu.RLock()
	defer p.mu.RUnlock()

	return map[string]interface{}{
		"total_connections": len(p.conns),
		"pod_ips":           getKeys(p.conns),
	}
}

func getKeys(m map[string]*websocket.Conn) []string {
	keys := make([]string, 0, len(m))
	for k := range m {
		keys = append(keys, k)
	}
	return keys
}
