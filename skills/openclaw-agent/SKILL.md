---
name: openclaw-agent
description: >-
  Create and manage agents within OpenClaw instances, configure agent-channel routing
  and agent-model binding. Use when creating agents, assigning agents to channels,
  configuring agent behavior, or managing multi-agent setups.
---

# OpenClaw Agent Manager

OpenClaw 智能体管理技能包，创建和管理智能体，配置路由。

## 🎯 核心理念：多智能体与多渠道

OpenClaw 原生支持**多智能体**和**多渠道多账号**的精确路由绑定。

- **默认行为**：实例创建后，会自带一个默认的 `main` 智能体。配置渠道时，默认绑定到 `main`。
- **高级用法**：用户可以在同一个实例中创建多个智能体（如：客服、HR），并分别绑定到不同的渠道或同一个渠道的不同账号（如：飞书的客服机器人、飞书的HR机器人）。

> **AI 规则**：当用户要求创建智能体时，主动告知用户："OpenClaw 支持在同一个实例中创建多个智能体，您可以将它们分别绑定到不同的渠道（比如飞书、QQ），甚至同一个渠道的不同机器人账号上。"

---

## 快速开始

```
用户: 在 openclaw-prod-01 创建客服智能体，对接飞书
```

AI 会创建智能体并在 `openclaw.json` 中配置路由绑定。

---

## 核心功能

### 1. 创建智能体

```bash
python scripts/agent_manager.py create \
  --instance <instance-id> \
  --name <agent-name> \
  --description "智能体描述"
```

**说明**：这会在实例的 `agents/` 目录下创建一个新的智能体文件夹，并在 `openclaw.json` 的 `agents.list` 中注册。

### 2. 绑定模型

```bash
python scripts/agent_manager.py bind-model \
  --instance <instance-id> \
  --agent <agent-name> \
  --model gpt-4
```

### 3. 配置路由绑定（核心）

将智能体绑定到特定渠道或账号。

```bash
python scripts/agent_manager.py bind-channel \
  --instance <instance-id> \
  --agent <agent-name> \
  --channel feishu \
  --account-id <optional-account-id>
```

**底层实现**：这会在 `openclaw.json` 的 `bindings` 数组中追加一条路由规则：
```json
"bindings": [
  {
    "agentId": "<agent-name>",
    "match": { 
      "channel": "feishu",
      "accountId": "<optional-account-id>"
    }
  }
]
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

## 路由配置示例

### 单智能体单渠道（默认）

最简单的配置，所有消息都交给 `main`：

```json
"bindings": [] // 留空，默认走 main
```

### 多智能体多渠道

飞书交给客服，QQ交给销售：

```json
"bindings": [
  { "agentId": "customer-service", "match": { "channel": "feishu" } },
  { "agentId": "sales", "match": { "channel": "qq" } }
]
```

### 同渠道多账号（高级）

飞书上有两个机器人，分别交给不同的智能体：

```json
"bindings": [
  { "agentId": "customer-service", "match": { "channel": "feishu", "accountId": "bot_kefu" } },
  { "agentId": "hr-assistant", "match": { "channel": "feishu", "accountId": "bot_hr" } }
]
```

---

## 使用示例

```
用户: 创建一个"技术支持"智能体，并绑定到飞书的 tech_bot 账号。

AI 会:
1. 调用 create 创建 tech-support 智能体
2. 调用 bind-channel 将 tech-support 绑定到 feishu 渠道的 tech_bot 账号
3. 告诉用户配置已生效，飞书 tech_bot 的消息现在由技术支持智能体处理了。
```

---

## 相关文档

- [智能体配置](reference/agent-config.md)
- [智能体路由](reference/agent-routing.md)
- [多智能体管理](reference/multi-agent.md)
