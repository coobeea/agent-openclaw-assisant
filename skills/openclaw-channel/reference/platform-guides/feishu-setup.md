# 飞书平台配置完整指南

## 1. 创建飞书应用

### 步骤
1. 访问 [飞书开放平台](https://open.feishu.cn/)
2. 进入"开发者后台"
3. 创建企业自建应用
4. 记录 App ID 和 App Secret

## 2. 配置应用权限

在"权限管理"中开通：
- ✅ 获取与发送单聊、群组消息
- ✅ 读取用户基础信息
- ✅ 以应用身份发送消息

## 3. 配置事件订阅

1. 在"事件订阅"中配置请求地址：
   ```
   http://your-server:3000/webhook/feishu
   ```

2. 订阅事件：
   - 接收消息 v2.0
   - 群聊@机器人

## 4. 发布版本

创建版本并发布到企业。

## 5. 配置到 OpenClaw

```bash
python scripts/channel_manager.py add \
  --instance openclaw-prod-01 \
  --platform feishu \
  --app-id cli_xxxxxxxxxxxxx \
  --app-secret your_secret_here
```

## 测试

在飞书中 @机器人 发送消息测试。
