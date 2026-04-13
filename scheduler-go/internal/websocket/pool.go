package websocket

import (
	"encoding/json"
	"fmt"
	"log"
	"time"

	"github.com/gorilla/websocket"
)

// Pool WebSocket 连接池
type Pool struct {
}

// NewPool 创建连接池
func NewPool() *Pool {
	return &Pool{}
}

// GetConn 获取 WebSocket 连接
func (p *Pool) GetConn(podIP string) (*websocket.Conn, error) {
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

	return conn, nil
}

// Close 关闭指定连接
func (p *Pool) Close(podIP string) {
	log.Printf("🔌 [WSPool] Close 跳过: %s", podIP)
}

// CloseAll 关闭所有连接
func (p *Pool) CloseAll() {
	log.Printf("🔌 [WSPool] CloseAll 跳过")
}

// GetStats 获取连接池统计
func (p *Pool) GetStats() map[string]interface{} {
	return map[string]interface{}{
		"mode": "per_request",
	}
}
