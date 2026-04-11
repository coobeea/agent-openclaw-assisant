package main

import (
	"log"

	"github.com/gin-contrib/cors"
	"github.com/gin-gonic/gin"

	"openclaw-scheduler/internal/api"
	"openclaw-scheduler/internal/db"
	"openclaw-scheduler/internal/k8s"
)

func main() {
	log.Println("🚀 启动 OpenClaw 调度服务...")

	// 初始化数据库
	if err := db.InitDB(); err != nil {
		log.Fatalf("数据库初始化失败: %v", err)
	}

	// 初始化 K8s 客户端
	if err := k8s.InitK8s(); err != nil {
		log.Fatalf("K8s 客户端初始化失败: %v", err)
	}

	// 创建 Gin 路由
	r := gin.Default()

	// 配置 CORS（支持 SSE 流式传输）
	config := cors.DefaultConfig()
	config.AllowOrigins = []string{"*"}
	config.AllowMethods = []string{"GET", "POST", "PUT", "DELETE", "OPTIONS"}
	config.AllowHeaders = []string{"Origin", "Content-Type", "Authorization", "Cache-Control", "X-Requested-With"}
	config.ExposeHeaders = []string{"Content-Type", "Cache-Control", "X-Accel-Buffering"}
	config.AllowCredentials = false
	r.Use(cors.New(config))

	// 注册路由
	api.RegisterRoutes(r)

	log.Println("✅ 调度服务启动成功")
	log.Println("📍 监听端口: 8080")
	log.Println("📂 智能体工作空间: /data/agents")

	// 启动服务
	if err := r.Run(":8080"); err != nil {
		log.Fatalf("服务启动失败: %v", err)
	}
}
