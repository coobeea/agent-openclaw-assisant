# 模型配置模板

## 📋 简介

模型配置模板让您可以**一键导入**常用的模型配置，无需手动逐个添加模型。

---

## 🚀 快速使用

### 1. 查看可用模板

```bash
python skills/openclaw-model/scripts/model_manager.py list-templates
```

### 2. 使用模板初始化

```bash
# 初始化全局配置（所有实例共享）
python skills/openclaw-model/scripts/model_manager.py init-from-template \
  bailian-coding-models \
  sk-sp-your-api-key-here

# 初始化并应用到指定实例
python skills/openclaw-model/scripts/model_manager.py init-from-template \
  bailian-coding-models \
  sk-sp-your-api-key-here \
  --instance <实例名>

# 初始化但不设置默认模型
python skills/openclaw-model/scripts/model_manager.py init-from-template \
  bailian-coding-models \
  sk-sp-your-api-key-here \
  --no-default
```

### 3. 重启实例（如果指定了实例）

```bash
python skills/openclaw-manager/scripts/instance_manager.py restart <实例名>
```

---

## 📦 可用模板

### bailian-coding-models

**提供商**: 百炼（阿里云）  
**API 地址**: `https://coding.dashscope.aliyuncs.com/v1`  
**模型数量**: 9 个

**推荐模型**（支持图片理解）:
- ✅ `qwen3.5-plus` - 1M上下文，65K输出
- ✅ `kimi-k2.5` - 262K上下文，32K输出
- ✅ `glm-5` - 131K上下文，32K输出
- ✅ `MiniMax-M2.5` - 1M上下文，65K输出
- ✅ `deepseek-v3.2` - 262K上下文，65K输出（纯文本）

**更多模型**（纯文本）:
- `qwen3-max-2026-01-23`
- `qwen3-coder-next`
- `qwen3-coder-plus`
- `glm-4.7`

---

## 🎯 使用场景

### 场景 1: 新建实例时初始化

```bash
# 1. 创建实例
python skills/openclaw-manager/scripts/instance_manager.py create openclaw-feishu-2774

# 2. 从模板初始化模型
python skills/openclaw-model/scripts/model_manager.py init-from-template \
  bailian-coding-models \
  sk-sp-your-api-key \
  --instance openclaw-feishu-2774

# 3. 重启实例
python skills/openclaw-manager/scripts/instance_manager.py restart openclaw-feishu-2774
```

### 场景 2: 更新 API Key

```bash
# 使用新 API Key 重新初始化
python skills/openclaw-model/scripts/model_manager.py init-from-template \
  bailian-coding-models \
  sk-sp-new-api-key \
  --instance openclaw-feishu-2774

# 重启实例
python skills/openclaw-manager/scripts/instance_manager.py restart <实例名>
```

### 场景 3: 添加新模型到现有配置

```bash
# 更新模板文件 templates/bailian-coding-models.json
# 然后重新初始化
python skills/openclaw-model/scripts/model_manager.py init-from-template \
  bailian-coding-models \
  sk-sp-your-api-key \
  --instance openclaw-feishu-2774
```

---

## 📝 创建自定义模板

您可以创建自己的模板文件：

**模板格式** (`templates/your-template.json`):

```json
{
  "name": "您的模板名称",
  "description": "模板描述",
  "provider": "bailian",
  "baseUrl": "https://your-api-endpoint.com/v1",
  "api": "openai-completions",
  "models": [
    {
      "id": "model-id",
      "name": "模型显示名称",
      "reasoning": false,
      "input": ["text", "image"],
      "cost": { "input": 0, "output": 0, "cacheRead": 0, "cacheWrite": 0 },
      "contextWindow": 131072,
      "maxTokens": 32768,
      "description": "模型描述"
    }
  ]
}
```

---

## 💡 优势

✅ **快速部署** - 一条命令导入所有模型  
✅ **避免错误** - 使用经过验证的配置  
✅ **易于维护** - 统一管理模型列表  
✅ **可复用** - 模板可在多个实例间共享

---

## 🔧 技术细节

### 自动完成的操作

1. **更新全局配置** (`workspace/data/models.json`)
2. **更新实例配置** (`workspace/lobsters/{instance}/.openclaw/openclaw.json`)
3. **设置默认模型** (可选)
4. **自动添加到智能体可用模型列表**

### 不会覆盖的配置

- 其他 provider 的配置
- 实例的其他配置（channels、plugins等）
- 已有的备份文件

---

## 📚 相关文档

- [模型管理完整文档](../../SKILL.md)
- [实例管理](../../openclaw-manager/SKILL.md)
- [配置修复](../scripts/model_manager.py) - `fix-config` 命令
