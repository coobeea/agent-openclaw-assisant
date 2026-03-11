---
name: openclaw-plugin
description: >-
  Install and manage OpenClaw plugins for Feishu, QQ, WeCom, and DingTalk.
  Use when installing plugins, configuring messaging platforms, managing plugin
  lifecycle, or checking plugin status.
---

# OpenClaw Plugin Manager

OpenClaw 插件管理技能包，支持飞书、QQ、企业微信、钉钉四大平台插件。

## 快速开始

```
用户: 为 openclaw-prod-01 安装飞书插件
```

AI 会自动安装飞书插件并配置。

---

## 核心功能

### 1. 列出可用插件

```bash
python scripts/plugin_manager.py list-available
```

### 2. 安装插件

```bash
python scripts/plugin_manager.py install <plugin-name> --instance <instance-id>
```

**支持的插件**:
- `feishu` - 飞书
- `qq` - QQ
- `wecom` - 企业微信
- `dingtalk` - 钉钉

### 3. 卸载插件

```bash
python scripts/plugin_manager.py uninstall <plugin-name> --instance <instance-id>
```

### 4. 更新插件

```bash
python scripts/plugin_manager.py update <plugin-name> --instance <instance-id>
```

### 5. 插件状态

```bash
python scripts/plugin_manager.py status --instance <instance-id>
```

---

## 支持的平台

### 飞书 (Feishu)

详见 [reference/feishu.md](reference/feishu.md)

**配置要求**:
- App ID
- App Secret

### QQ

详见 [reference/qq.md](reference/qq.md)

**配置要求**:
- QQ Bot Token

### 企业微信 (WeCom)

详见 [reference/wecom.md](reference/wecom.md)

**配置要求**:
- Corp ID
- Corp Secret

### 钉钉 (DingTalk)

详见 [reference/dingtalk.md](reference/dingtalk.md)

**配置要求**:
- App Key
- App Secret

---

## 使用示例

```
用户: 为 openclaw-prod-01 安装飞书和企业微信插件

AI 会:
1. 安装飞书插件
2. 安装企业微信插件
3. 返回安装结果
```

---

## 相关文档

- [飞书插件](reference/feishu.md)
- [QQ插件](reference/qq.md)
- [企业微信插件](reference/wecom.md)
- [钉钉插件](reference/dingtalk.md)
