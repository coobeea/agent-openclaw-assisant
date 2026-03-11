---
name: openclaw-channel
description: >-
  Manage messaging platform channels and credentials for OpenClaw instances.
  Use when configuring Feishu/QQ/WeCom/DingTalk channels, managing credentials,
  encrypting secrets, or checking channel connection status.
---

# OpenClaw Channel Manager

OpenClaw 渠道管理技能包，管理消息平台的渠道配置和凭证。

## 快速开始

```
用户: 为 openclaw-prod-01 配置飞书渠道
App ID: cli_xxxxx
App Secret: yyyyy
```

AI 会加密存储凭证并配置渠道。

---

## 核心功能

### 1. 添加渠道

```bash
python scripts/channel_manager.py add \
  --instance <instance-id> \
  --platform feishu \
  --app-id <app-id> \
  --app-secret <secret>
```

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
  --channel <channel-name>
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
3. 添加渠道配置
4. 测试连接
5. 返回配置结果
```

---

## 相关文档

- [渠道配置](reference/channel-config.md)
- [凭证管理](reference/credential-management.md)
- [平台配置指南](reference/platform-guides/)
