# 模型配置说明

## 模型配置结构

```yaml
model:
  name: gpt-4
  provider: openai
  enabled: true
  credentials:
    api_key: <encrypted>
  parameters:
    temperature: 0.7
    max_tokens: 2000
    top_p: 1.0
  limits:
    max_requests_per_minute: 100
```

## 参数说明

### temperature
- 范围: 0.0 - 2.0
- 默认: 0.7
- 说明: 控制随机性，越低越确定

### max_tokens
- 范围: 1 - 模型上限
- 默认: 2000
- 说明: 最大生成token数

### top_p
- 范围: 0.0 - 1.0
- 默认: 1.0
- 说明: 核采样参数

## 按场景推荐配置

### 客服场景
```yaml
temperature: 0.3  # 稳定准确
max_tokens: 1000
```

### 创意场景
```yaml
temperature: 0.9  # 更有创意
max_tokens: 2000
```
