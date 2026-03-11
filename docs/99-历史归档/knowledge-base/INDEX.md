# 🔍 知识库快速索引

> 快速找到问题解决方案

**更新时间**: 2026-03-11 07:50  
**状态**: ✅ 已实施自动化预防措施

---

## 🚨 紧急问题（优先级最高）

| 症状 | 问题 | 解决方案 |
|------|------|---------|
| AI 对话失败，显示 "Unknown model" | 模型 Provider 配置错误 | [模型Provider配置](./critical-issues/模型Provider配置.md) |
| Web UI 显示 "device identity required" | Token URL 格式错误 | [Web-UI访问问题](./critical-issues/Web-UI访问问题.md) |
| 龙虾启动后立即退出 | 配置文件格式错误 | [配置文件格式](./critical-issues/配置文件格式.md) |
| 飞书机器人要求配对，批准后没反应 | 配对后未重启实例 | [飞书配对问题](../飞书配对问题-完整解决方案.md) |

---

## 📋 按问题类型查找

### 启动问题

| 症状 | 文档 |
|------|------|
| Process 模式启动失败 | [故障排查流程](./quick-fixes/故障排查流程.md) #1 |
| Docker 容器立即退出 | [故障排查流程](./quick-fixes/故障排查流程.md) #2 |
| 端口被占用 | [常见错误码](./quick-fixes/常见错误码.md) #EADDRINUSE |
| 配置文件不存在 | [故障排查流程](./quick-fixes/故障排查流程.md) #3 |

### 访问问题

| 症状 | 文档 |
|------|------|
| Web UI 显示 "device identity required" | [Web-UI访问问题](./critical-issues/Web-UI访问问题.md) |
| 刷新后 Token 丢失 | [Web-UI访问问题](./critical-issues/Web-UI访问问题.md) |
| 无法访问 localhost | [Web-UI访问问题](./critical-issues/Web-UI访问问题.md) |

### 模型问题

| 症状 | 文档 |
|------|------|
| AI 对话无响应 | [模型Provider配置](./critical-issues/模型Provider配置.md) |
| 显示 "Unknown model" | [模型Provider配置](./critical-issues/模型Provider配置.md) |
| 显示 "Model not found" | [模型Provider配置](./critical-issues/模型Provider配置.md) |
| 显示 "API key invalid" | [模型Provider配置](./critical-issues/模型Provider配置.md) |

### 配置问题

| 症状 | 文档 |
|------|------|
| 配置验证失败 | [配置文件格式](./critical-issues/配置文件格式.md) |
| 模型名称格式错误 | [配置文件格式](./critical-issues/配置文件格式.md) |
| Provider 配置缺失 | [模型Provider配置](./critical-issues/模型Provider配置.md) |

---

## 📖 按文档类型查找

### ⚠️ 关键问题（必读！）

1. [模型Provider配置](./critical-issues/模型Provider配置.md) ⭐⭐⭐⭐⭐
   - 最严重问题，已修复 2-3 轮仍反复出现
   - 必须使用官方 provider 名称 `bailian`
   - 不能自造名称如 `dashscope-subscription`

2. [Web-UI访问问题](./critical-issues/Web-UI访问问题.md) ⭐⭐⭐⭐
   - 几乎每个新用户都会遇到
   - 必须用 `#token=` 不是 `?token=`
   - Hash Fragment vs Query Parameter

3. [配置文件格式](./critical-issues/配置文件格式.md) ⭐⭐⭐
   - 模型名称用 `/` 不是 `|`
   - API 类型用 `openai-completions`
   - models 必须是数组

### ✅ 最佳实践

1. [创建龙虾检查清单](./best-practices/创建龙虾检查清单.md)
   - 创建前必须检查
   - 创建后必须验证
   - 避免常见错误

2. [配置管理规范](./best-practices/配置管理规范.md)
   - 配置文件结构
   - 字段命名规范
   - 默认值设置

3. [命名规范](./best-practices/命名规范.md)
   - 龙虾命名规则
   - Provider 命名规则
   - 文件命名规则

### 🔧 快速修复

1. [常见错误码](./quick-fixes/常见错误码.md)
   - EADDRINUSE - 端口占用
   - ENOENT - 文件不存在
   - 其他错误码

2. [故障排查流程](./quick-fixes/故障排查流程.md)
   - 启动问题排查
   - 访问问题排查
   - 配置问题排查

### 📖 配置参考

1. [openclaw.json完整示例](./config-reference/openclaw.json完整示例.md)
   - 完整配置示例
   - 所有字段说明
   - 推荐配置

2. [字段说明](./config-reference/字段说明.md)
   - 每个字段的作用
   - 可选值说明
   - 默认值

---

## 🔗 快速链接

### 从 agent-openclaws 参考

- [历史问题记录](/Users/lifeng/git/git-claw/agent-openclaws/docs/历史记录/)
- [常见问题FAQ](/Users/lifeng/git/git-claw/agent-openclaws/docs/常见问题.md)
- [配置说明](/Users/lifeng/git/git-claw/agent-openclaws/docs/配置说明.md)

### 本项目文档

- [测试计划](../testing/测试计划.md)
- [经验积累](../testing/经验积累.md)
- [整合方案](../testing/整合方案.md)

---

## 🎯 使用建议

### 遇到问题时

```
1. 看症状 → 找索引表 → 找对应文档
2. 按步骤修复
3. 验证结果
4. 记录新经验（如果是新问题）
```

### 开始工作前

```
1. 阅读"关键问题"部分
2. 查看"最佳实践"
3. 遵循检查清单
```

### 持续改进

```
1. 遇到新问题 → 立即记录
2. 找到解决方案 → 更新文档
3. 提取经验 → 添加到索引
```

---

**返回**: [知识库总览](./README.md)
