---
name: openclaw-agent
description: >-
  Create and manage agents within OpenClaw instances, configure agent-channel routing
  and agent-model binding. Use when creating agents, assigning agents to channels,
  configuring agent behavior, or managing multi-agent setups.
---

# OpenClaw Agent Manager

OpenClaw 智能体管理技能包，创建和管理智能体，配置路由。

## 快速开始

```
用户: 在 openclaw-prod-01 创建客服智能体，使用 GPT-4，对接飞书
```

AI 会创建智能体并配置模型和渠道绑定。

---

## 核心功能

### 1. 创建智能体

```bash
python scripts/agent_manager.py create \
  --instance <instance-id> \
  --name <agent-name> \
  --description "智能体描述"
```

**智能体命名**: `{instance-id}-agent-{agent-name}`

示例: `openclaw-prod-01-agent-customer-service`

### 2. 绑定模型

```bash
python scripts/agent_manager.py bind-model \
  --instance <instance-id> \
  --agent <agent-name> \
  --model gpt-4
```

### 3. 绑定渠道

```bash
python scripts/agent_manager.py bind-channel \
  --instance <instance-id> \
  --agent <agent-name> \
  --channel feishu
```

### 4. 列出智能体

```bash
python scripts/agent_manager.py list --instance <instance-id>
```

### 5. 删除智能体

```bash
python scripts/agent_manager.py delete \
  --instance <instance-id> \
  --agent <agent-name>
```

---

## 智能体配置

### 基础属性

- 名称（name）
- 描述（description）
- 角色（role/personality）
- 使用的模型
- 对接的渠道

### 高级配置

- 系统提示词（system prompt）
- 知识库
- 工具集
- 会话记忆配置

详见 [reference/agent-config.md](reference/agent-config.md)

---

## 路由配置

### 单智能体单渠道

最简单的配置：

```
实例: openclaw-prod-01
  └── Agent: main
        └── 渠道: 飞书
```

### 多智能体多渠道

高级配置：

```
实例: openclaw-prod-01
  ├── Agent: customer-service
  │     └── 渠道: 飞书
  ├── Agent: tech-support
  │     └── 渠道: 企业微信
  └── Agent: sales
        └── 渠道: 钉钉
```

详见 [reference/agent-routing.md](reference/agent-routing.md)

---

## 使用示例

```
用户: 创建三个智能体：
1. 客服 - GPT-4 - 飞书
2. 技术支持 - Claude - 企业微信  
3. 销售 - GPT-4 - 钉钉

AI 会:
1. 创建三个智能体
2. 分别绑定指定的模型
3. 分别绑定指定的渠道
4. 返回配置结果
```

---

## 相关文档

- [智能体配置](reference/agent-config.md)
- [智能体路由](reference/agent-routing.md)
- [多智能体管理](reference/multi-agent.md)
