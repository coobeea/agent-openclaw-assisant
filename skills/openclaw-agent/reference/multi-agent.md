# 多智能体管理

## 使用场景

### 按职能划分

```
实例: openclaw-prod-01
  ├── customer-service (客服)
  ├── tech-support (技术支持)
  └── sales (销售)
```

### 按渠道划分

```
实例: openclaw-prod-01
  ├── feishu-agent (飞书专用)
  ├── wecom-agent (企业微信专用)
  └── qq-agent (QQ专用)
```

### 按语言划分

```
实例: openclaw-prod-01
  ├── chinese-agent (中文)
  └── english-agent (英文)
```

## 智能体协作

### 转接机制

```yaml
agent: customer-service
handoff:
  - condition: technical_issue
    target: tech-support
  - condition: sales_inquiry
    target: sales
```

### 共享知识库

多个智能体共享同一个知识库。

## 资源分配

### 模型分配

```
customer-service → gpt-3.5-turbo (快速)
tech-support → gpt-4 (专业)
sales → claude-3-sonnet (平衡)
```

### 并发控制

控制每个智能体的并发会话数。
