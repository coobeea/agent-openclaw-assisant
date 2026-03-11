# 钉钉插件配置指南

## 前置条件

1. 钉钉开放平台账号
2. 创建企业内部应用
3. 获取 App Key 和 App Secret

## 配置步骤

### 1. 安装插件

```bash
python scripts/plugin_manager.py install dingtalk --instance openclaw-prod-01
```

### 2. 配置渠道

```bash
python ../openclaw-channel/scripts/channel_manager.py add \
  --instance openclaw-prod-01 \
  --platform dingtalk \
  --app-id <app-key> \
  --app-secret <app-secret>
```

## 配置回调

在钉钉开放平台配置：
- 请求URL: `http://your-server:3000/webhook/dingtalk`
- 加密方式: 由 OpenClaw 配置
