# 🎓 OpenClaw 知识库

> **来源**: 从现有 lobster-manager 项目提取的宝贵经验  
> **目的**: 避免重复犯错，一步到位解决问题  
> **更新**: 2026-03-10

---

## 📚 知识库结构

```
knowledge-base/
├── README.md                  # 本文件：知识库总览
├── INDEX.md                   # 快速索引：问题→解决方案
├── critical-issues/           # ⚠️ 关键问题（反复出现的严重问题）
│   ├── 模型Provider配置.md     # 最严重！已修复2-3轮仍出现
│   ├── Web-UI访问问题.md       # 高频问题
│   └── 配置文件格式.md          # 常见错误
├── best-practices/            # ✅ 最佳实践
│   ├── 创建龙虾检查清单.md
│   ├── 配置管理规范.md
│   └── 命名规范.md
├── quick-fixes/               # 🔧 快速修复
│   ├── 常见错误码.md
│   └── 故障排查流程.md
└── config-reference/          # 📖 配置参考
    ├── openclaw.json完整示例.md
    └── 字段说明.md
```

---

## ⚠️ 极其关键的问题（必读！）

### 问题 #1: 模型 Provider 名称必须用官方规范

**严重程度**: ⭐⭐⭐⭐⭐  
**发生频率**: 已修复 2-3 轮，仍反复出现！  
**影响范围**: 所有 AI 功能失效

**错误示例**:
```json
{
  "agents": {
    "defaults": {
      "model": {
        "primary": "dashscope-subscription/qwen3.5-plus"  // ❌ 自造名称
      }
    }
  }
}
```

**正确做法**:
```json
{
  "models": {
    "providers": {
      "bailian": {  // ✅ 官方名称！
        "baseUrl": "https://coding.dashscope.aliyuncs.com/v1",
        "apiKey": "YOUR_API_KEY",
        "api": "openai-completions",  // ⚠️ 不是 "openai-compatible"
        "models": [...]
      }
    }
  },
  "agents": {
    "defaults": {
      "model": {
        "primary": "bailian/qwen3.5-plus"  // ✅ 使用官方名称
      }
    }
  }
}
```

**详细文档**: [critical-issues/模型Provider配置.md](./critical-issues/模型Provider配置.md)

### 问题 #2: Web UI 访问必须用 `#token=`

**严重程度**: ⭐⭐⭐⭐  
**发生频率**: 几乎每个新用户都会遇到  
**症状**: 显示 "device identity required"

**错误示例**:
```
❌ http://127.0.0.1:19410/?token=abc123  (用 ? 不是 #)
```

**正确做法**:
```
✅ http://127.0.0.1:19410/#token=abc123  (用 # 不是 ?)
```

**为什么**:
- `?token=` 是 Query 参数，刷新时会丢失
- `#token=` 是 Hash Fragment，刷新时保留
- OpenClaw Web UI 设计使用 Hash Fragment

**详细文档**: [critical-issues/Web-UI访问问题.md](./critical-issues/Web-UI访问问题.md)

### 问题 #3: 配置文件格式常见错误

**严重程度**: ⭐⭐⭐  
**常见错误**:

1. **模型名称格式**:
   ```
   ✅ bailian/qwen3.5-plus   (用 / 分隔)
   ❌ bailian|qwen3.5-plus   (不能用 |)
   ❌ qwen3.5-plus           (缺少 provider)
   ```

2. **API 类型**:
   ```
   ✅ "api": "openai-completions"
   ❌ "api": "openai-compatible"  (OpenClaw 不支持)
   ```

3. **models 字段必须是数组**:
   ```json
   ✅ "models": []
   ❌ "models": {}  (不能是对象)
   ```

**详细文档**: [critical-issues/配置文件格式.md](./critical-issues/配置文件格式.md)

---

## 🎯 使用方式

### 1. 遇到问题时

1. **先查索引**: [INDEX.md](./INDEX.md)
2. **找对应文档**: 根据问题类型查看相应文档
3. **按步骤修复**: 跟随文档中的修复步骤
4. **验证结果**: 确保问题已解决

### 2. 创建龙虾前

**必读**: [best-practices/创建龙虾检查清单.md](./best-practices/创建龙虾检查清单.md)

### 3. 开发过程中

**参考**: [best-practices/配置管理规范.md](./best-practices/配置管理规范.md)

---

## 📊 知识来源

### 来自 agent-openclaws 项目

- 27 个 Python 管理工具的实践经验
- 86+ 份历史文档
- 多次问题修复的记录
- 真实生产环境的经验

### 关键贡献者

- 用户实际使用中发现的问题
- AI 助手在多轮修复中积累的经验
- OpenClaw 官方文档和最佳实践

---

## 🔄 持续更新

### 更新原则

1. **遇到新问题**:
   - 立即记录到 knowledge-base
   - 分析根本原因
   - 提供解决方案
   - 添加预防措施

2. **发现最佳实践**:
   - 记录到 best-practices
   - 更新检查清单
   - 完善配置模板

3. **验证有效性**:
   - 在测试中验证
   - 在文档中更新
   - 在工具中体现

### 更新日志

- 2026-03-10: 创建知识库，从 agent-openclaws 提取经验
- （后续更新记录）

---

## 🎓 学习路径

### 新手必读
1. [创建龙虾检查清单](./best-practices/创建龙虾检查清单.md)
2. [Web UI 访问问题](./critical-issues/Web-UI访问问题.md)
3. [常见错误码](./quick-fixes/常见错误码.md)

### 进阶学习
1. [模型 Provider 配置](./critical-issues/模型Provider配置.md)
2. [配置管理规范](./best-practices/配置管理规范.md)
3. [openclaw.json 完整示例](./config-reference/openclaw.json完整示例.md)

### 问题排查
1. [故障排查流程](./quick-fixes/故障排查流程.md)
2. [常见错误码](./quick-fixes/常见错误码.md)
3. [配置文件格式](./critical-issues/配置文件格式.md)

---

## 💡 核心原则

### 1. 遵循官方规范
- ✅ 使用官方 provider 名称（`bailian`，不是 `dashscope-subscription`）
- ✅ 使用官方 API 类型（`openai-completions`）
- ✅ 遵循官方配置格式

### 2. 从源头预防
- ✅ 在模板文件中固化正确配置
- ✅ 在创建工具中使用正确默认值
- ✅ 在诊断工具中自动检测问题

### 3. 持续改进
- ✅ 记录每个问题和解决方案
- ✅ 提取最佳实践
- ✅ 更新工具和文档

### 4. 一步到位
- ✅ 问题发现后立即修复
- ✅ 修复后立即记录
- ✅ 记录后立即应用到工具和文档

---

**下一步**: 查看 [INDEX.md](./INDEX.md) 快速定位问题解决方案
