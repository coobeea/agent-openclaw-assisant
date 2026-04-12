<template>
  <div id="app">
    <!-- 顶部导航 -->
    <div class="header">
      <div class="header-content">
        <div class="logo-section">
          <div class="logo-icon">🤖</div>
          <div class="logo-text">
            <h1>OpenClaw</h1>
            <span class="subtitle">智能体管理平台</span>
          </div>
        </div>
        <div class="user-info" v-if="userInfo">
          <div class="user-avatar">{{ userInfo.username.charAt(0).toUpperCase() }}</div>
          <span class="username">{{ userInfo.username }}</span>
          <el-button class="logout-btn" size="small" @click="logout" round>退出</el-button>
        </div>
      </div>
    </div>

    <!-- 登录/注册界面 -->
    <div v-if="!userInfo" class="login-container">
      <div class="login-card">
        <div class="login-header">
          <div class="login-icon">🚀</div>
          <h2>{{ isLogin ? '欢迎回来' : '创建账号' }}</h2>
          <p>{{ isLogin ? '登录您的 OpenClaw 账户' : '开始您的智能体之旅' }}</p>
        </div>
        
        <el-form :model="authForm" class="login-form">
          <el-form-item>
            <el-input 
              v-model="authForm.username" 
              placeholder="用户名" 
              size="large"
              prefix-icon="User"
            ></el-input>
          </el-form-item>
          <el-form-item>
            <el-input 
              v-model="authForm.password" 
              type="password" 
              placeholder="密码" 
              size="large"
              prefix-icon="Lock"
              @keyup.enter="handleAuth"
            ></el-input>
          </el-form-item>
          <el-form-item>
            <el-button 
              type="primary" 
              @click="handleAuth" 
              size="large"
              class="auth-btn"
              :loading="authenticating"
            >
              {{ isLogin ? '登录' : '注册' }}
            </el-button>
          </el-form-item>
          <div class="switch-auth">
            <span @click="isLogin = !isLogin">
              {{ isLogin ? '没有账号？立即注册' : '已有账号？立即登录' }}
            </span>
          </div>
        </el-form>
      </div>
      
      <!-- 装饰背景 -->
      <div class="bg-decoration">
        <div class="bubble bubble-1"></div>
        <div class="bubble bubble-2"></div>
        <div class="bubble bubble-3"></div>
      </div>
    </div>

    <!-- 主内容区 -->
    <div v-else class="main-container">
      <el-container>
        <!-- 左侧智能体列表 -->
        <el-aside width="320px" class="aside">
          <div class="aside-header">
            <div class="aside-title">
              <span class="title-icon">🎯</span>
              <h3>我的智能体</h3>
            </div>
            <el-button 
              type="primary" 
              size="small" 
              @click="dialogVisible = true"
              class="create-btn"
              round
            >
              <el-icon><Plus /></el-icon>
              <span>创建</span>
            </el-button>
          </div>
          
          <div class="agents-list-wrapper">
            <el-scrollbar class="agents-scrollbar">
              <div class="agents-list">
              <div 
                v-for="agent in agents" 
                :key="agent.agent_id"
                class="agent-card"
                :class="{ active: currentAgent?.agent_id === agent.agent_id }"
                @click="selectAgent(agent)"
              >
                <div class="agent-avatar">{{ agent.name.charAt(0) }}</div>
                <div class="agent-info">
                  <div class="agent-name">{{ agent.name }}</div>
                  <div class="agent-desc">{{ agent.description || '暂无描述' }}</div>
                </div>
                <div class="agent-status" :class="{ active: currentAgent?.agent_id === agent.agent_id }">
                  <span class="status-dot"></span>
                </div>
              </div>
              
              <el-empty 
                v-if="agents.length === 0" 
                description="还没有智能体"
                class="empty-agents"
              >
                <el-button type="primary" @click="dialogVisible = true" round>
                  创建第一个智能体
                </el-button>
              </el-empty>
            </div>
            </el-scrollbar>
          </div>
        </el-aside>

        <!-- 右侧对话区 -->
        <el-main class="main">
          <div v-if="!currentAgent" class="empty-chat">
            <div class="empty-chat-content">
              <div class="empty-icon">💬</div>
              <h3>开始对话</h3>
              <p>请选择或创建一个智能体</p>
            </div>
          </div>
          
          <div v-else class="chat-container">
            <div class="chat-header">
              <div class="chat-agent-info">
                <div class="chat-avatar">{{ currentAgent.name.charAt(0) }}</div>
                <div>
                  <h3>{{ currentAgent.name }}</h3>
                  <span class="chat-agent-id">{{ currentAgent.agent_id }}</span>
                </div>
              </div>
              <div class="chat-actions">
                <el-tag type="success" effect="plain" round>在线</el-tag>
              </div>
            </div>
            
            <!-- 对话历史 -->
            <div class="chat-messages-wrapper">
              <el-scrollbar ref="scrollbar" class="chat-messages">
                <div class="messages-wrapper">
                <div 
                  v-for="(msg, index) in chatHistory" 
                  :key="msg.id"
                  class="message-group"
                  :style="{ animationDelay: `${index * 0.05}s` }"
                >
                  <div class="message user-message">
                    <div class="message-avatar">👤</div>
                    <div class="message-bubble">
                      <div class="message-text">{{ msg.user_message }}</div>
                    </div>
                  </div>
                  
                  <div class="message agent-message">
                    <div class="message-avatar">🤖</div>
                    <div class="message-bubble">
                      <!-- 思考中提示 -->
                      <div v-if="msg.isThinking" class="thinking-indicator">
                        <span class="thinking-dot"></span>
                        <span class="thinking-dot"></span>
                        <span class="thinking-dot"></span>
                        <span class="thinking-text">{{ msg.thinking || 'AI 正在思考中...' }}</span>
                      </div>
                      <!-- 思维链 -->
                      <div v-if="!msg.isThinking && msg.thinking && msg.thinking !== '思考中...'" class="thinking-section">
                        <el-collapse>
                          <el-collapse-item>
                            <template #title>
                              <span style="color: #909399; font-size: 13px;">
                                🧠 思维过程
                              </span>
                            </template>
                            <div class="thinking-content">{{ msg.thinking }}</div>
                          </el-collapse-item>
                        </el-collapse>
                      </div>
                      <!-- 正常回复 -->
                      <div v-if="!msg.isThinking" class="message-text">{{ msg.agent_response || '思考中...' }}</div>
                    </div>
                  </div>
                </div>
                
                <el-empty 
                  v-if="chatHistory.length === 0" 
                  description="还没有对话记录"
                  class="empty-history"
                >
                  <p>向智能体发送第一条消息吧！</p>
                </el-empty>
              </div>
            </el-scrollbar>
            </div>

            <!-- 输入框 -->
            <div class="chat-input-wrapper">
              <div class="chat-input">
                <el-input
                  v-model="userMessage"
                  placeholder="输入消息，按 Enter 发送..."
                  @keyup.enter="sendMessage"
                  :disabled="sending"
                  size="large"
                  class="message-input"
                >
                  <template #suffix>
                    <el-button 
                      type="primary" 
                      @click="sendMessage"
                      :loading="sending"
                      circle
                      class="send-btn"
                    >
                      <el-icon v-if="!sending"><Promotion /></el-icon>
                    </el-button>
                  </template>
                </el-input>
              </div>
            </div>
          </div>
        </el-main>
      </el-container>
    </div>

    <!-- 创建智能体对话框 -->
    <el-dialog 
      v-model="dialogVisible" 
      title="创建智能体" 
      width="500px"
      :close-on-click-modal="false"
      class="create-dialog"
    >
      <template #header>
        <div class="dialog-header">
          <span class="dialog-icon">✨</span>
          <span>创建新智能体</span>
        </div>
      </template>
      
      <el-form :model="agentForm" label-width="0px" class="agent-form">
        <el-form-item>
          <div class="form-label">智能体名称</div>
          <el-input 
            v-model="agentForm.name" 
            placeholder="例如：客服助手、编程助手..." 
            size="large"
          ></el-input>
        </el-form-item>
        <el-form-item>
          <div class="form-label">智能体描述</div>
          <el-input 
            v-model="agentForm.description" 
            type="textarea" 
            :rows="4"
            placeholder="描述这个智能体的功能和特点..."
          ></el-input>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="dialogVisible = false" size="large">取消</el-button>
        <el-button 
          type="primary" 
          @click="handleCreateAgent" 
          :loading="creating" 
          size="large"
        >
          创建智能体
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, nextTick, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus, Promotion } from '@element-plus/icons-vue'
import { register, login, createAgent, listAgents, chat, getChatHistory } from './api'

// 用户信息
const userInfo = ref(null)
const isLogin = ref(true)
const authenticating = ref(false)
const authForm = reactive({
  username: '',
  password: ''
})

// 智能体相关
const agents = ref([])
const currentAgent = ref(null)
const dialogVisible = ref(false)
const creating = ref(false)
const agentForm = reactive({
  name: '',
  description: ''
})

// 对话相关
const chatHistory = ref([])
const userMessage = ref('')
const sending = ref(false)
const scrollbar = ref(null)

// 认证处理
const handleAuth = async () => {
  if (!authForm.username || !authForm.password) {
    ElMessage.warning('请输入用户名和密码')
    return
  }

  authenticating.value = true
  try {
    if (isLogin.value) {
      const res = await login(authForm)
      userInfo.value = res.data
      ElMessage.success({
        message: '登录成功！',
        type: 'success',
        duration: 2000
      })
      loadAgents()
    } else {
      await register(authForm)
      ElMessage.success({
        message: '注册成功！请登录',
        type: 'success',
        duration: 2000
      })
      isLogin.value = true
      authForm.password = ''
    }
  } catch (error) {
    ElMessage.error(error.response?.data?.error || '操作失败')
  } finally {
    authenticating.value = false
  }
}

// 退出登录
const logout = () => {
  userInfo.value = null
  agents.value = []
  currentAgent.value = null
  chatHistory.value = []
  ElMessage.info('已退出登录')
}

// 加载智能体列表
const loadAgents = async () => {
  try {
    const res = await listAgents({ user_id: userInfo.value.user_id })
    agents.value = res.data.agents || []
  } catch (error) {
    ElMessage.error('加载智能体列表失败')
  }
}

// 创建智能体
const handleCreateAgent = async () => {
  if (!agentForm.name) {
    ElMessage.warning('请输入智能体名称')
    return
  }

  creating.value = true
  try {
    await createAgent({
      user_id: userInfo.value.user_id,
      name: agentForm.name,
      description: agentForm.description
    })
    ElMessage.success({
      message: '创建成功！',
      type: 'success',
      duration: 2000
    })
    dialogVisible.value = false
    agentForm.name = ''
    agentForm.description = ''
    loadAgents()
  } catch (error) {
    ElMessage.error('创建失败')
  } finally {
    creating.value = false
  }
}

// 选择智能体
const selectAgent = async (agent) => {
  currentAgent.value = agent
  await loadChatHistory(agent.agent_id)
}

// 加载对话历史
const loadChatHistory = async (agentId) => {
  try {
    const res = await getChatHistory({ agent_id: agentId })
    chatHistory.value = res.data.history || []
    await nextTick()
    scrollToBottom()
  } catch (error) {
    ElMessage.error('加载对话历史失败')
  }
}

// 发送消息（流式）
const sendMessage = async () => {
  if (!userMessage.value.trim()) return
  
  const message = userMessage.value
  userMessage.value = ''
  sending.value = true

  // 添加用户消息和空的助手回复
  const newMessage = {
    id: Date.now(),
    user_message: message,
    agent_response: '',
    thinking: '',
    isThinking: true // 添加思考状态
  }
  chatHistory.value.push(newMessage)
  await nextTick()
  scrollToBottom()
  
  // 思考动画（每 500ms 更新一次）
  let thinkingDots = 0
  const thinkingInterval = setInterval(() => {
    if (!newMessage.isThinking) {
      clearInterval(thinkingInterval)
      return
    }
    thinkingDots = (thinkingDots + 1) % 4
    newMessage.thinking = '思考中' + '.'.repeat(thinkingDots)
    chatHistory.value = [...chatHistory.value]
  }, 500)

  try {
    // 使用 XMLHttpRequest 支持 SSE 流式传输（比 fetch 更可靠）
    const xhr = new XMLHttpRequest()
    xhr.open('POST', '/api/chat/stream', true)
    xhr.setRequestHeader('Content-Type', 'application/json')
    xhr.setRequestHeader('Cache-Control', 'no-cache')
    
    let lastIndex = 0
    
    xhr.onprogress = function() {
      // 获取新增的数据
      const newData = xhr.responseText.substring(lastIndex)
      lastIndex = xhr.responseText.length
      
      // 按行分割
      const lines = newData.split('\n')
      
      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const dataStr = line.substring(6).trim()
          
          if (dataStr === '') continue
          
          try {
            const data = JSON.parse(dataStr)
            
            // 收到实际内容，停止思考动画
            if (data.choices && data.choices[0]?.delta?.content) {
              newMessage.isThinking = false
              const content = data.choices[0].delta.content
              newMessage.agent_response += content
            } else if (data.type === 'heartbeat') {
              // 心跳事件，保持连接
              console.log('💓 心跳')
            } else if (data.type === 'thinking' || data.type === 'thinking_complete') {
              // 思维链内容
              newMessage.thinking += (data.content || '')
            } else if (data.type === 'content') {
              // 正常回复内容
              newMessage.isThinking = false
              newMessage.agent_response += (data.content || '')
            } else if (data.type === 'done') {
              // 完成
              console.log('流式传输完成')
            }
            
            // 强制更新和滚动
            chatHistory.value = [...chatHistory.value]
            setTimeout(() => scrollToBottom(), 0)
            
          } catch (e) {
            console.warn('解析 SSE 数据失败:', dataStr, e)
          }
        }
      }
    }
    
    xhr.onload = function() {
      console.log('请求完成', xhr.status)
      if (xhr.status !== 200) {
        throw new Error(`请求失败: ${xhr.status}`)
      }
      
      // 如果没有收到任何内容
      if (!newMessage.agent_response && !newMessage.thinking) {
        newMessage.agent_response = '[无回复]'
      }
      
      sending.value = false
    }
    
    xhr.onerror = function() {
      console.error('请求错误')
      ElMessage.error('发送失败')
      newMessage.agent_response = '[发送失败]'
      sending.value = false
    }
    
    xhr.ontimeout = function() {
      console.error('请求超时')
      ElMessage.error('请求超时')
      newMessage.agent_response = '[请求超时]'
      sending.value = false
    }
    
    xhr.timeout = 300000 // 5分钟超时
    
    // 发送请求
    xhr.send(JSON.stringify({
      agent_id: currentAgent.value.agent_id,
      message: message
    }))

  } catch (error) {
    console.error('发送消息失败:', error)
    ElMessage.error(error.message || '发送失败')
    newMessage.agent_response = '[发送失败]'
    sending.value = false
  }
}

// 滚动到底部
const scrollToBottom = () => {
  if (scrollbar.value) {
    const wrap = scrollbar.value.$el.querySelector('.el-scrollbar__wrap')
    if (wrap) {
      wrap.scrollTop = wrap.scrollHeight
    }
  }
}

onMounted(() => {
  const saved = localStorage.getItem('userInfo')
  if (saved) {
    userInfo.value = JSON.parse(saved)
    loadAgents()
  }
})

watch(() => userInfo.value, (val) => {
  if (val) {
    localStorage.setItem('userInfo', JSON.stringify(val))
  } else {
    localStorage.removeItem('userInfo')
  }
})
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Hiragino Sans GB', 
    'Microsoft YaHei', 'Helvetica Neue', Arial, sans-serif;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  overflow: hidden;
}

#app {
  height: 100vh;
  display: flex;
  flex-direction: column;
}

/* ==================== 顶部导航 ==================== */

.header {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  padding: 0 30px;
  z-index: 100;
  flex-shrink: 0;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 70px;
}

.logo-section {
  display: flex;
  align-items: center;
  gap: 15px;
}

.logo-icon {
  font-size: 40px;
  animation: float 3s ease-in-out infinite;
}

@keyframes float {
  0%, 100% { transform: translateY(0px); }
  50% { transform: translateY(-10px); }
}

.logo-text h1 {
  font-size: 24px;
  font-weight: 700;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  margin: 0;
  line-height: 1;
}

.subtitle {
  font-size: 12px;
  color: #999;
  display: block;
  margin-top: 4px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 16px;
}

.username {
  font-weight: 500;
  color: #333;
}

.logout-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  color: white;
}

/* ==================== 登录界面 ==================== */

.login-container {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
}

.login-card {
  width: 420px;
  padding: 50px 40px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-radius: 24px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  position: relative;
  z-index: 10;
  animation: slideUp 0.6s ease-out;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.login-header {
  text-align: center;
  margin-bottom: 40px;
}

.login-icon {
  font-size: 60px;
  margin-bottom: 20px;
  animation: bounce 2s ease-in-out infinite;
}

@keyframes bounce {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.1); }
}

.login-header h2 {
  font-size: 28px;
  font-weight: 700;
  color: #333;
  margin-bottom: 10px;
}

.login-header p {
  color: #666;
  font-size: 14px;
}

.login-form {
  margin-top: 30px;
}

.login-form .el-form-item {
  margin-bottom: 20px;
}

.auth-btn {
  width: 100%;
  height: 48px;
  font-size: 16px;
  font-weight: 600;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  border-radius: 12px;
  transition: all 0.3s;
}

.auth-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 30px rgba(102, 126, 234, 0.4);
}

.switch-auth {
  text-align: center;
  margin-top: 20px;
}

.switch-auth span {
  color: #667eea;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.3s;
}

.switch-auth span:hover {
  color: #764ba2;
  text-decoration: underline;
}

/* 背景装饰 */
.bg-decoration {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  overflow: hidden;
  z-index: 1;
}

.bubble {
  position: absolute;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.1);
  animation: float-bubble 20s ease-in-out infinite;
}

.bubble-1 {
  width: 300px;
  height: 300px;
  top: 10%;
  left: 10%;
  animation-delay: 0s;
}

.bubble-2 {
  width: 200px;
  height: 200px;
  top: 60%;
  right: 15%;
  animation-delay: 2s;
}

.bubble-3 {
  width: 150px;
  height: 150px;
  bottom: 20%;
  left: 60%;
  animation-delay: 4s;
}

@keyframes float-bubble {
  0%, 100% {
    transform: translateY(0) scale(1);
    opacity: 0.3;
  }
  50% {
    transform: translateY(-30px) scale(1.1);
    opacity: 0.5;
  }
}

/* ==================== 主内容区 ==================== */

.main-container {
  flex: 1;
  overflow: hidden;
  margin: 20px;
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
  display: flex;
}

.main-container > .el-container {
  flex: 1;
  height: 100%;
  overflow: hidden;
}

/* ==================== 左侧智能体列表 ==================== */

.aside {
  background: transparent;
  border-right: 1px solid rgba(0, 0, 0, 0.06);
  padding: 20px;
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow: hidden;
}

.aside-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 2px solid rgba(102, 126, 234, 0.1);
  flex-shrink: 0;
}

.aside-title {
  display: flex;
  align-items: center;
  gap: 10px;
}

.title-icon {
  font-size: 24px;
}

.aside-title h3 {
  font-size: 18px;
  font-weight: 600;
  color: #333;
}

.create-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  color: white;
  font-weight: 500;
}

.agents-list-wrapper {
  flex: 1;
  overflow: hidden;
}

.agents-scrollbar {
  height: 100%;
}

.agents-list {
  padding: 5px;
}

.agent-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  margin-bottom: 12px;
  background: white;
  border-radius: 16px;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  border: 2px solid transparent;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.agent-card:hover {
  transform: translateX(8px);
  box-shadow: 0 8px 24px rgba(102, 126, 234, 0.15);
  border-color: rgba(102, 126, 234, 0.2);
}

.agent-card.active {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  box-shadow: 0 8px 24px rgba(102, 126, 234, 0.4);
  transform: translateX(8px) scale(1.02);
}

.agent-avatar {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  font-weight: 700;
  color: #333;
  flex-shrink: 0;
}

.agent-card.active .agent-avatar {
  background: rgba(255, 255, 255, 0.3);
  color: white;
}

.agent-info {
  flex: 1;
  min-width: 0;
}

.agent-name {
  font-weight: 600;
  font-size: 15px;
  margin-bottom: 4px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.agent-desc {
  font-size: 13px;
  opacity: 0.7;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.agent-status {
  width: 12px;
  height: 12px;
  position: relative;
}

.status-dot {
  display: block;
  width: 8px;
  height: 8px;
  background: #ddd;
  border-radius: 50%;
  transition: all 0.3s;
}

.agent-status.active .status-dot {
  background: #52c41a;
  box-shadow: 0 0 10px rgba(82, 196, 26, 0.6);
  animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.3); }
}

.empty-agents {
  margin-top: 100px;
}

/* ==================== 对话区 ==================== */

.main {
  background: #fafbfc;
  padding: 0;
  display: flex;
  flex-direction: column;
  height: 100%;
  flex: 1;
  overflow: hidden;
}

.empty-chat {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.empty-chat-content {
  text-align: center;
}

.empty-icon {
  font-size: 80px;
  margin-bottom: 20px;
  animation: float 3s ease-in-out infinite;
}

.empty-chat-content h3 {
  font-size: 24px;
  color: #333;
  margin-bottom: 10px;
}

.empty-chat-content p {
  color: #999;
  font-size: 14px;
}

.chat-container {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: white;
  flex: 1;
  overflow: hidden;
}

.chat-header {
  padding: 20px 30px;
  background: white;
  border-bottom: 1px solid rgba(0, 0, 0, 0.06);
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-shrink: 0;
}

.chat-agent-info {
  display: flex;
  align-items: center;
  gap: 15px;
}

.chat-avatar {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  font-weight: 700;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.chat-agent-info h3 {
  font-size: 18px;
  font-weight: 600;
  color: #333;
  margin: 0;
}

.chat-agent-id {
  font-size: 12px;
  color: #999;
  font-family: 'Monaco', 'Courier New', monospace;
}

.chat-messages-wrapper {
  flex: 1;
  overflow: hidden;
  background: linear-gradient(to bottom, #fafbfc 0%, #f5f7fa 100%);
}

.chat-messages {
  height: 100%;
}

.messages-wrapper {
  padding: 30px;
  max-width: 900px;
  margin: 0 auto;
}

.message-group {
  margin-bottom: 30px;
  animation: fadeIn 0.4s ease-out both;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.message {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  margin-bottom: 16px;
}

.user-message {
  flex-direction: row-reverse;
}

.message-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  flex-shrink: 0;
  background: white;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.message-bubble {
  max-width: 70%;
  position: relative;
}

.message-text {
  padding: 14px 18px;
  border-radius: 18px;
  font-size: 15px;
  line-height: 1.6;
  word-wrap: break-word;
  position: relative;
  animation: scaleIn 0.3s ease-out;
}

@keyframes scaleIn {
  from {
    opacity: 0;
    transform: scale(0.9);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

.user-message .message-text {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
  border-bottom-right-radius: 4px;
}

.agent-message .message-text {
  background: white;
  color: #333;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  border: 1px solid rgba(0, 0, 0, 0.06);
  border-bottom-left-radius: 4px;
}

/* 思维链样式 */
.thinking-section {
  margin-bottom: 12px;
  background: rgba(102, 126, 234, 0.05);
  border-radius: 12px;
  overflow: hidden;
}

.thinking-section :deep(.el-collapse) {
  border: none;
  background: transparent;
}

.thinking-section :deep(.el-collapse-item__header) {
  background: transparent;
  border: none;
  padding: 10px 15px;
  font-size: 13px;
  color: #909399;
  transition: all 0.3s;
}

.thinking-section :deep(.el-collapse-item__header:hover) {
  background: rgba(102, 126, 234, 0.08);
}

.thinking-section :deep(.el-collapse-item__wrap) {
  border: none;
  background: transparent;
}

.thinking-section :deep(.el-collapse-item__content) {
  padding: 0 15px 15px 15px;
}

.thinking-content {
  font-size: 13px;
  color: #666;
  line-height: 1.8;
  white-space: pre-wrap;
  word-break: break-word;
  background: white;
  padding: 12px;
  border-radius: 8px;
  border: 1px solid rgba(102, 126, 234, 0.1);
}

.empty-history {
  margin-top: 100px;
}

/* ==================== 思考中动画 ==================== */

.thinking-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  background: rgba(102, 126, 234, 0.05);
  border-radius: 12px;
  animation: pulse-bg 2s ease-in-out infinite;
}

@keyframes pulse-bg {
  0%, 100% {
    background: rgba(102, 126, 234, 0.05);
  }
  50% {
    background: rgba(102, 126, 234, 0.1);
  }
}

.thinking-dot {
  width: 8px;
  height: 8px;
  background: #667eea;
  border-radius: 50%;
  animation: thinking-bounce 1.4s infinite ease-in-out;
}

.thinking-dot:nth-child(1) {
  animation-delay: -0.32s;
}

.thinking-dot:nth-child(2) {
  animation-delay: -0.16s;
}

@keyframes thinking-bounce {
  0%, 80%, 100% {
    transform: scale(0);
    opacity: 0.5;
  }
  40% {
    transform: scale(1);
    opacity: 1;
  }
}

.thinking-text {
  font-size: 13px;
  color: #667eea;
  font-weight: 500;
}

/* ==================== 输入框 ==================== */

.chat-input-wrapper {
  background: white;
  border-top: 1px solid rgba(0, 0, 0, 0.06);
  padding: 20px 30px;
  flex-shrink: 0;
}

.chat-input {
  max-width: 900px;
  margin: 0 auto;
}

.message-input {
  border-radius: 24px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.message-input .el-input__wrapper {
  border-radius: 24px;
  padding: 12px 20px;
  box-shadow: none;
  background: #fafbfc;
  border: 2px solid transparent;
  transition: all 0.3s;
}

.message-input .el-input__wrapper:hover {
  border-color: rgba(102, 126, 234, 0.3);
}

.message-input .el-input__wrapper.is-focus {
  border-color: #667eea;
  background: white;
  box-shadow: 0 0 0 4px rgba(102, 126, 234, 0.1);
}

.send-btn {
  width: 40px;
  height: 40px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  transition: all 0.3s;
}

.send-btn:hover {
  transform: scale(1.1) rotate(15deg);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.send-btn:active {
  transform: scale(0.95);
}

/* ==================== 创建对话框 ==================== */

.create-dialog .el-dialog {
  border-radius: 20px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.dialog-header {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 20px;
  font-weight: 600;
}

.dialog-icon {
  font-size: 24px;
}

.agent-form {
  padding: 10px 0;
}

.form-label {
  font-weight: 600;
  color: #333;
  margin-bottom: 8px;
  font-size: 14px;
}

.agent-form .el-input__wrapper,
.agent-form .el-textarea__inner {
  border-radius: 12px;
  border: 2px solid #e6e6e6;
  transition: all 0.3s;
}

.agent-form .el-input__wrapper:hover,
.agent-form .el-textarea__inner:hover {
  border-color: rgba(102, 126, 234, 0.3);
}

.agent-form .el-input__wrapper.is-focus,
.agent-form .el-textarea__inner:focus {
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

/* ==================== 响应式 ==================== */

@media (max-width: 768px) {
  .aside {
    width: 100% !important;
  }
  
  .main-container .el-container {
    flex-direction: column;
  }
  
  .message-bubble {
    max-width: 85%;
  }
}

/* ==================== Element Plus 样式覆盖 ==================== */

.el-button--primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
}

.el-button--primary:hover {
  opacity: 0.9;
}

.el-input__inner {
  font-size: 15px;
}

.el-tag {
  font-family: 'Monaco', 'Courier New', monospace;
}

/* ==================== 滚动条美化 ==================== */

::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}

::-webkit-scrollbar-track {
  background: transparent;
}

::-webkit-scrollbar-thumb {
  background: rgba(0, 0, 0, 0.1);
  border-radius: 3px;
}

::-webkit-scrollbar-thumb:hover {
  background: rgba(0, 0, 0, 0.2);
}
</style>
