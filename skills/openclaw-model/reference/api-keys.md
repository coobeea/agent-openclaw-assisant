# API 密钥管理

## 获取 API 密钥

### OpenAI
1. 访问 https://platform.openai.com/api-keys
2. 创建新的 API 密钥
3. 复制密钥（只显示一次）

### Anthropic
1. 访问 https://console.anthropic.com/settings/keys
2. 创建新的 API 密钥
3. 复制密钥

## 密钥存储

所有 API 密钥自动加密存储。

### 查看密钥（遮罩）

```bash
python scripts/model_manager.py list --instance openclaw-prod-01
```

输出示例：
```
• gpt-4 (openai)
  API Key: sk-...xyz123 (已加密)
```

## 密钥轮换

定期更换 API 密钥：

```bash
python scripts/model_manager.py rotate-key \
  --instance openclaw-prod-01 \
  --model gpt-4 \
  --new-key sk-new-key-here
```

## 安全建议

1. 使用独立的密钥用于测试和生产
2. 定期轮换密钥（建议每3个月）
3. 监控 API 使用量，发现异常及时禁用
4. 不要在日志中记录密钥
