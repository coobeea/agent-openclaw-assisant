import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 300000 // 增加超时时间到 300 秒 (5分钟)
})

// 用户相关
export const register = (data) => api.post('/users/register', data)
export const login = (data) => api.post('/users/login', data)

// 智能体相关
export const createAgent = (data) => api.post('/agents/create', data)
export const listAgents = (params) => api.get('/agents/list', { params })

// 对话相关
export const chat = (data) => api.post('/chat', data)
export const getChatHistory = (params) => api.get('/chat/history', { params })

// 容器相关
export const getContainerStatus = () => api.get('/containers/status')

export default api
