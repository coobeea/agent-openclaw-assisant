# QQ 插件配置指南

## 前置条件

1. QQ 开放平台账号
2. 创建 QQ Bot
3. 获取 Bot Token

## 配置步骤

### 1. 安装插件

```bash
python scripts/plugin_manager.py install qq --instance openclaw-prod-01
```

### 2. 配置渠道

```bash
python ../openclaw-channel/scripts/channel_manager.py add \
  --instance openclaw-prod-01 \
  --platform qq \
  --app-id <bot-id> \
  --app-secret <bot-token>
```

## 权限配置

需要的权限：
- 接收群消息
- 发送消息
- @机器人
