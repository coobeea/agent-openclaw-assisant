# ⚠️⚠️⚠️ 模型 Provider 配置 - 极其关键！

> **严重程度**: ⭐⭐⭐⭐⭐  
> **发生频率**: 已修复 2-3 轮，仍反复出现！  
> **影响范围**: 所有 AI 功能失效  
> **来源**: agent-openclaws 项目历史经验

---

## 🚨 核心问题

**我们自己起的名字** vs **官方规范名称**

### 错误示例（❌ 绝对不要这样！）

```json
{
  "agents": {
    "defaults": {
      "model": {
        "primary": "dashscope-subscription/qwen3-max-2026-01-23"  // ❌ 自造名称
      }
    }
  },
  "models": {
    "providers": {
      "dashscope-subscription": {  // ❌ 自造名称
        "api": "openai-compatible",  // ❌ OpenClaw 不支持
        "models": {}  // ❌ 不能是对象
      }
    }
  }
}
```

### 正确示例（✅ 必须这样！）

```json
{
  "models": {
    "providers": {
      "bailian": {  // ✅ 官方名称！
        "baseUrl": "https://coding.dashscope.aliyuncs.com/v1",
        "apiKey": "sk-sp-YOUR_API_KEY",
        "api": "openai-completions",  // ✅ OpenClaw 支持
        "models": [  // ✅ 必须是数组
          {
            "id": "qwen3.5-plus",
            "name": "qwen3.5-plus",
            "reasoning": false,
            "input": ["text", "image"],
            "cost": { "input": 0, "output": 0, "cacheRead": 0, "cacheWrite": 0 },
            "contextWindow": 1000000,
            "maxTokens": 65536
          },
          {
            "id": "kimi-k2.5",
            "name": "kimi-k2.5",
            "reasoning": false,
            "input": ["text", "image"],
            "cost": { "input": 0, "output": 0, "cacheRead": 0, "cacheWrite": 0 },
            "contextWindow": 262144,
            "maxTokens": 32768
          }
        ]
      }
    }
  },
  "agents": {
    "defaults": {
      "model": {
        "primary": "bailian/qwen3.5-plus"  // ✅ 使用官方名称
      },
      "models": {
        "bailian/qwen3.5-plus": {},
        "bailian/kimi-k2.5": {},
        "bailian/glm-5": {},
        "bailian/MiniMax-M2.5": {}
      }
    }
  }
}
```

---

## 🔍 问题详解

### 1. Provider 名称必须用官方规范

| 我们的名称 | 官方名称 | 正确性 |
|----------|---------|--------|
| `dashscope-subscription` | `bailian` | ❌ 自造名称 |
| `dashscope` | `bailian` | ❌ 可能混淆 |
| `bailian` | `bailian` | ✅ 官方名称 |

**为什么必须用 `bailian`**:
1. ✅ 这是阿里云百炼平台的官方名称
2. ✅ 与官方文档一致
3. ✅ 避免歧义和混淆
4. ✅ 减少出错概率

### 2. API 类型必须正确

| 我们的配置 | OpenClaw 需要 | 正确性 |
|----------|-------------|--------|
| `openai-compatible` | `openai-completions` | ❌ OpenClaw 不认识 |
| `openai` | `openai-completions` | ❌ 不完整 |
| `openai-completions` | `openai-completions` | ✅ 正确 |

**OpenClaw 支持的 API 类型**:
- `openai-completions` - 标准 OpenAI `/v1/chat/completions`
- `anthropic-messages` - Anthropic `/v1/messages`
- `google-generative-ai` - Google Gemini
- `ollama` - Ollama 本地模型

### 3. models 字段必须是数组

```json
// ❌ 错误：对象
"models": {
  "qwen3.5-plus": "Qwen3.5 Plus"
}

// ✅ 正确：数组
"models": [
  {
    "id": "qwen3.5-plus",
    "name": "Qwen3.5 Plus"
  }
]
```

---

## 🎯 完整配置要求

### 必需字段

```json
{
  "models": {
    "providers": {
      "bailian": {
        "baseUrl": "https://coding.dashscope.aliyuncs.com/v1",  // 必需
        "apiKey": "sk-sp-YOUR_API_KEY",  // 必需
        "api": "openai-completions",  // 必需，且必须是 OpenClaw 支持的类型
        "models": [  // 必需，且必须是数组
          {
            "id": "qwen3.5-plus",  // 必需，模型 ID
            "name": "qwen3.5-plus"  // 必需，显示名称
          }
        ]
      }
    }
  }
}
```

### 推荐字段（完整配置）

```json
{
  "id": "qwen3.5-plus",
  "name": "qwen3.5-plus",
  "reasoning": false,  // 是否支持推理
  "input": ["text", "image"],  // 支持的输入类型
  "cost": {  // 成本信息
    "input": 0,
    "output": 0,
    "cacheRead": 0,
    "cacheWrite": 0
  },
  "contextWindow": 1000000,  // 上下文窗口
  "maxTokens": 65536  // 最大输出 tokens
}
```

---

## 🎓 推荐模型

### 主力模型（支持图片理解）

1. **bailian/qwen3.5-plus** ⭐ 推荐！
   - 100万 token 上下文
   - 支持图片理解
   - 最大输出 65536 tokens

2. **bailian/kimi-k2.5** ⭐ 推荐！
   - 26万 token 上下文
   - 支持图片理解
   - 最大输出 32768 tokens

### 其他模型

3. **bailian/glm-5**
   - 20万 token 上下文
   - 纯文本

4. **bailian/MiniMax-M2.5**
   - 20万 token 上下文
   - 纯文本
   - 最大输出 131072 tokens

---

## 🔧 快速验证

### 检查配置

```bash
# 查看当前模型配置
cat test-workspace/lobsters/*/openclaw/openclaw.json | \
python3 -c "
import sys, json
config = json.load(sys.stdin)

# 检查 provider 名称
model = config.get('agents', {}).get('defaults', {}).get('model', {}).get('primary', '')
print(f'当前模型: {model}')

if 'bailian/' in model:
    print('✅ 使用官方 provider 名称')
elif 'dashscope' in model:
    print('❌ 使用自造名称！请立即改为 bailian')
    exit(1)

# 检查 provider 配置
providers = config.get('models', {}).get('providers', {})
if 'bailian' not in providers:
    print('❌ 缺少 bailian provider 配置！')
    exit(1)

bailian = providers['bailian']

# 检查 API 类型
api_type = bailian.get('api', '')
if api_type != 'openai-completions':
    print(f'❌ API 类型错误：{api_type}，应该是 openai-completions')
    exit(1)

# 检查 models 字段
models = bailian.get('models', None)
if not isinstance(models, list):
    print(f'❌ models 字段类型错误：应该是数组，实际是 {type(models).__name__}')
    exit(1)

print('✅ 所有检查通过！')
"
```

### 自动修复脚本

```python
#!/usr/bin/env python3
"""
自动修复模型 Provider 配置
"""
import json
from pathlib import Path

def fix_provider_config(config_file: Path):
    """修复 provider 配置"""
    with open(config_file, 'r') as f:
        config = json.load(f)
    
    # 1. 修复 provider 名称
    primary_model = config.get('agents', {}).get('defaults', {}).get('model', {}).get('primary', '')
    if 'dashscope' in primary_model and 'bailian/' not in primary_model:
        # 替换为官方名称
        new_model = primary_model.replace('dashscope-subscription/', 'bailian/')
        new_model = new_model.replace('dashscope/', 'bailian/')
        config['agents']['defaults']['model']['primary'] = new_model
        print(f'✅ 修复模型名称: {primary_model} → {new_model}')
    
    # 2. 修复 API 类型
    providers = config.get('models', {}).get('providers', {})
    for provider_name, provider_config in providers.items():
        api_type = provider_config.get('api', '')
        if api_type == 'openai-compatible':
            provider_config['api'] = 'openai-completions'
            print(f'✅ 修复 {provider_name} API 类型: openai-compatible → openai-completions')
    
    # 3. 保存
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    print(f'✅ 配置已修复: {config_file}')

if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        print('用法: python fix_provider.py <config.json>')
        sys.exit(1)
    
    fix_provider_config(Path(sys.argv[1]))
```

---

## 📋 创建龙虾检查清单

创建龙虾后，**必须确认**:

- [ ] ✅ 使用官方 provider 名称（`bailian`，不是 `dashscope-subscription`）
- [ ] ✅ 模型名称格式：`bailian/model`（用 `/` 不是 `|`）
- [ ] ✅ `models.providers.bailian` 存在且配置完整
- [ ] ✅ `models.providers.bailian.api` 是 `"openai-completions"`
- [ ] ✅ `models.providers.bailian.models` 是数组且包含完整元数据
- [ ] ✅ `agents.defaults.models` 包含所有可用模型
- [ ] ✅ API Key 正确配置

---

## 🛡️ 预防措施

### 1. ✅ 自动化配置同步（已实施 - 2026-03-11）

**状态**: ✅ **已完成**

**实施内容**:
- 在 `instance_manager.py` 中添加 `_sync_models_config()` 方法
- 创建实例时自动从 `workspace/data/models.json` 同步配置
- 自动注入到实例的 `.openclaw/openclaw.json`

**效果**: 🎯 新创建的实例自动拥有完整的 models 配置

**详细文档**: [预防措施-实施完成.md](../../预防措施-实施完成.md)

---

### 2. ✅ 健康检查机制（已实施 - 2026-03-11）

**状态**: ✅ **已完成**

**工具**: `scripts/health_check.py`

**检查项**:
- 命名规范
- 模型配置完整性
- 配置文件格式

**使用方法**:
```bash
python3 scripts/health_check.py
```

**详细文档**: [工具链使用指南.md](../../工具链使用指南.md#健康检查)

---

### 3. ✅ 批量修复工具（已实施 - 2026-03-11）

**状态**: ✅ **已完成**

**工具**: `scripts/fix_all_models.py`

**功能**:
- 扫描所有实例
- 检测配置缺失
- 自动注入完整配置
- 自动备份

**使用方法**:
```bash
python3 scripts/fix_all_models.py
```

**详细文档**: [工具链使用指南.md](../../工具链使用指南.md#批量修复)

---

### 4. 在配置模板中固化

```python
# config.py
DEFAULT_MODEL = 'bailian/qwen3.5-plus'  # ✅ 使用官方名称

BAILIAN_PROVIDER_CONFIG = {
    "baseUrl": "https://coding.dashscope.aliyuncs.com/v1",
    "api": "openai-completions",  # ✅ 正确的 API 类型
    "models": [  # ✅ 数组
        {
            "id": "qwen3.5-plus",
            "name": "qwen3.5-plus"
        }
    ]
}
```

---

## 🎉 总结

### 核心原则

> **必须遵循官方规范！自造名称会导致歧义和频繁出错！**

### 三条铁律

1. ✅ Provider 名称：`bailian`（不是 `dashscope-subscription`）
2. ✅ API 类型：`openai-completions`（不是 `openai-compatible`）
3. ✅ models 字段：数组（不是对象）

### 预防策略

1. ✅ 在模板中固化正确配置
2. ✅ 在工具中验证和检测
3. ✅ 在文档中明确强调
4. ✅ 在测试中自动验证

---

**来源**: agent-openclaws 项目，已修复 2-3 轮的严重问题  
**更新**: 2026-03-10  
**重要程度**: ⭐⭐⭐⭐⭐ 极其关键！
