# 智能体配置说明

## 智能体配置结构

```yaml
agent:
  id: openclaw-prod-01-agent-customer-service
  name: customer-service
  description: 客服智能体
  enabled: true
  model: gpt-4
  channels:
    - feishu
  personality:
    role: 客服助手
    tone: 专业友好
  memory:
    enabled: true
    max_history: 100
```

## 配置项说明

### 基础配置
- `name`: 智能体名称（英文）
- `description`: 描述
- `enabled`: 是否启用

### 模型配置
- `model`: 使用的AI模型
- `temperature`: 温度参数
- `max_tokens`: 最大token数

### 渠道配置
- `channels`: 对接的渠道列表
- 支持一个智能体对接多个渠道

### 个性化配置
- `personality.role`: 角色定位
- `personality.tone`: 语气风格
- `system_prompt`: 系统提示词

### 记忆配置
- `memory.enabled`: 是否启用记忆
- `memory.max_history`: 历史记录数
