---
name: openclaw-model
description: >-
  Configure and manage AI models for OpenClaw agents. Use when adding AI models
  like GPT-4 or Claude, configuring model parameters, managing API keys, or
  switching between different models.
---

# OpenClaw Model Manager

OpenClaw 模型管理技能包，管理 AI 模型配置和 API 密钥。

## 快速开始

```
用户: 为 openclaw-prod-01 添加 GPT-4 模型，API Key 是 sk-xxxxx
```

AI 会加密存储 API Key 并配置模型。

---

## 核心功能

### 1. 添加模型

```bash
python scripts/model_manager.py add \
  --instance <instance-id> \
  --model gpt-4 \
  --provider openai \
  --api-key <key>
```

### 2. 列出模型

```bash
python scripts/model_manager.py list --instance <instance-id>
```

### 3. 测试模型

```bash
python scripts/model_test.py <instance-id> <model-name>
```

### 4. 设置默认模型

```bash
python scripts/model_manager.py set-default \
  --instance <instance-id> \
  --model gpt-4
```

### 5. 删除模型

```bash
python scripts/model_manager.py remove \
  --instance <instance-id> \
  --model <model-name>
```

---

## 支持的模型

### OpenAI

- GPT-4
- GPT-4 Turbo
- GPT-3.5 Turbo

详见 [reference/supported-models.md](reference/supported-models.md)

### Anthropic

- Claude 3 Opus
- Claude 3 Sonnet
- Claude 3 Haiku

### 本地模型

- Ollama
- LM Studio
- 其他兼容 OpenAI API 的模型

---

## API 密钥管理

### 加密存储

所有 API 密钥自动加密存储，使用 Fernet 算法。

### 密钥轮换

```bash
python scripts/model_manager.py rotate-key \
  --instance <instance-id> \
  --model gpt-4 \
  --new-key <new-key>
```

详见 [reference/api-keys.md](reference/api-keys.md)

---

## 模型配置

### 基础配置

```yaml
model:
  name: gpt-4
  provider: openai
  api_key: <encrypted>
```

### 高级参数

```yaml
parameters:
  temperature: 0.7
  max_tokens: 2000
  top_p: 1.0
```

详见 [reference/model-config.md](reference/model-config.md)

---

## 使用示例

```
用户: 添加 Claude 3 Sonnet 模型，API Key 是 sk-ant-xxxxx，设置为默认模型

AI 会:
1. 加密 API Key
2. 添加模型配置
3. 测试连接
4. 设置为默认
5. 返回配置结果
```

---

## 相关文档

- [模型配置](reference/model-config.md)
- [支持的模型](reference/supported-models.md)
- [API密钥管理](reference/api-keys.md)
