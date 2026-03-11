# 渠道配置说明

## 渠道配置结构

每个渠道包含以下配置：

```yaml
channel:
  name: feishu-main
  platform: feishu
  enabled: true
  credentials:
    app_id: cli_xxxxx
    app_secret: <encrypted>
  settings:
    webhook_url: http://server:3000/webhook/feishu
    timeout: 30
```

## 平台特定配置

### 飞书
- app_id: 应用ID
- app_secret: 应用密钥
- encrypt_key: 加密密钥（可选）

### QQ
- bot_id: 机器人ID
- bot_token: 机器人Token

### 企业微信
- corp_id: 企业ID
- corp_secret: 应用密钥
- agent_id: 应用AgentID

### 钉钉
- app_key: 应用Key
- app_secret: 应用密钥

## 渠道状态

- `enabled`: 启用/禁用
- `connected`: 连接状态
- `last_active`: 最后活跃时间
