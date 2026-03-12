---
name: openclaw-channel
description: >-
  Manage messaging platform channels and credentials for OpenClaw instances.
  Use when configuring Feishu/QQ/WeCom/DingTalk channels, managing credentials,
  encrypting secrets, or checking channel connection status.
---

# OpenClaw Channel Manager

OpenClaw 渠道管理技能包，管理消息平台的渠道配置和凭证。

## 🎯 核心交互规则：渠道与智能体绑定

当用户请求配置渠道（如飞书、QQ）时，AI 必须遵循以下交互逻辑：

1. **默认行为**：如果不做特殊说明，新配置的渠道默认由实例的 `main` 智能体处理。
2. **主动告知多账号能力**：如果用户配置飞书等支持多账号的平台，主动告知："您可以配置默认账号，也可以配置多个账号（比如客服机器人、HR机器人）。"
3. **主动告知路由能力**：配置完成后，主动告知："目前该渠道的消息默认由 `main` 智能体处理。如果您想让其他智能体来处理，可以告诉我帮您创建一个新智能体并绑定到这个渠道。"

---

## 快速开始

```
用户: 为 openclaw-prod-01 配置飞书渠道
App ID: cli_xxxxx
App Secret: yyyyy
```

AI 会加密存储凭证并配置渠道。

---

## 核心功能

### 1. 添加渠道 (支持多账号)

```bash
python scripts/channel_manager.py add \
  --instance <instance-id> \
  --platform feishu \
  --app-id <app-id> \
  --app-secret <secret> \
  --account-id <optional-account-id>
```

**说明**：如果提供了 `--account-id`（例如 `bot_kefu`），配置将写入 `channels.feishu.accounts.bot_kefu`，从而支持同渠道多账号。

### 2. 列出渠道

```bash
python scripts/channel_manager.py list --instance <instance-id>
```

### 3. 测试连接

```bash
python scripts/connection_test.py <instance-id> <channel-name>
```

### 4. 删除渠道

```bash
python scripts/channel_manager.py remove \
  --instance <instance-id> \
  --channel <channel-name> \
  --account-id <optional-account-id>
```

---

## 凭证管理

### 加密存储

所有敏感信息（App Secret、Token）自动加密存储。

```bash
# 加密工具
python scripts/credential_encrypt.py encrypt <plaintext>
python scripts/credential_encrypt.py decrypt <encrypted>
```

使用 Fernet 加密算法，密钥存储在 `workspace/.keyfile`。

### 凭证显示

查看渠道时，敏感信息会遮罩显示：

```
App ID: cli_xxxxx
App Secret: yyy...zzz (已加密)
```

---

## 平台配置

### 飞书配置

详见 [reference/platform-guides/feishu-setup.md](reference/platform-guides/feishu-setup.md)

### QQ配置

详见 [reference/platform-guides/qq-setup.md](reference/platform-guides/qq-setup.md)

### 企业微信配置

详见 [reference/platform-guides/wecom-setup.md](reference/platform-guides/wecom-setup.md)

### 钉钉配置

详见 [reference/platform-guides/dingtalk-setup.md](reference/platform-guides/dingtalk-setup.md)

---

## 使用示例

```
用户: 配置飞书渠道，App ID 是 cli_abc123，Secret 是 secret_xyz789

AI 会:
1. 检查飞书插件是否已安装
2. 加密 App Secret
3. 添加渠道配置（默认账号）
4. 测试连接
5. 告知用户："配置成功！默认由 main 智能体处理。如果您需要，我也可以帮您创建专门的客服智能体来接管这个飞书。"
```

---

## 相关文档

- [渠道配置](reference/channel-config.md)
- [凭证管理](reference/credential-management.md)
- [平台配置指南](reference/platform-guides/)
