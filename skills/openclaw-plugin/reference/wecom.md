# 企业微信插件配置指南

## 前置条件

1. 企业微信管理员账号
2. 创建企业自建应用
3. 获取 Corp ID 和 Corp Secret

## 配置步骤

### 1. 安装插件

```bash
python scripts/plugin_manager.py install wecom --instance openclaw-prod-01
```

### 2. 配置渠道

```bash
python ../openclaw-channel/scripts/channel_manager.py add \
  --instance openclaw-prod-01 \
  --platform wecom \
  --app-id <corp-id> \
  --app-secret <corp-secret>
```

## 配置回调

在企业微信后台配置：
- URL: `http://your-server:3000/webhook/wecom`
- Token: 由 OpenClaw 生成
- EncodingAESKey: 由 OpenClaw 生成
