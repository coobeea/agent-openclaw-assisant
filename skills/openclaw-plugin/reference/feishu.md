# 飞书插件配置指南

## 前置条件

1. 飞书开放平台账号
2. 创建企业自建应用
3. 获取 App ID 和 App Secret

## 配置步骤

### 1. 安装插件

```bash
python scripts/plugin_manager.py install feishu --instance openclaw-prod-01
```

### 2. 配置渠道

使用 `openclaw-channel` 技能包：

```bash
python ../openclaw-channel/scripts/channel_manager.py add \
  --instance openclaw-prod-01 \
  --platform feishu \
  --app-id cli_xxxxxxxxxxxxx \
  --app-secret your_secret_here
```

### 3. 配置回调地址

在飞书开放平台配置：
- 请求地址: `http://your-server:3000/webhook/feishu`
- 验证Token: 由 OpenClaw 生成

## 权限配置

需要开通的权限：
- 接收消息
- 发送消息
- 获取用户信息

## 测试连接

```bash
python ../openclaw-channel/scripts/connection_test.py openclaw-prod-01 feishu
```
