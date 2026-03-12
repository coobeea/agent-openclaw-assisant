# 🔧 问题解决

> **遇到问题？直接来这里查！**

---

## 🚨 必读

**处理任何问题前，先看这个**：
- **[处理问题-必读指南.md](./处理问题-必读指南.md)** - 标准流程

---

## 🔥 高频问题（按重要性排序）

### 0. 🚨🚨🚨 API 密钥泄露处理 🆕 紧急！

**症状**: API 密钥被提交到 git 历史中

**风险等级**: ⚠️⚠️⚠️⚠️⚠️ 极高危

**泄露情况**:
- 🔴 飞书 App ID + Secret（2个提交）
- 🔴 百炼 API Keys x2（3个提交）
- ✅ 工作区已 100% 清理
- ❌ Git历史待清理

**立即行动**:
1. 🔥 **撤销泄露的密钥**（飞书 + 百炼）
2. 🧹 **清理 git 历史**（推荐：重建仓库）
3. 🚀 **强制推送更新**
4. 📢 **通知协作者重新克隆**

**详细文档**:
- **[API密钥泄露-最终检查报告.md](./API密钥泄露-最终检查报告.md)** 🆕 完整检查结果
- **[API密钥泄露-处理指南.md](./API密钥泄露-处理指南.md)** - 完整处理流程（3种清理方案）

---

### 1. ⭐⭐⭐⭐⭐ 网络问题 - GitHub 访问慢 🆕

**症状**: GitHub 克隆速度慢 / 连接超时 / 无法访问

**解决方案**: 使用 Gitee 国内镜像

**国内镜像地址**: `https://gitee.com/618lf/openclaw.git`

**快速操作**:
```bash
# ✅ 使用 Gitee 镜像（国内，速度快）
git clone https://gitee.com/618lf/openclaw.git openclaw

# 原 GitHub 地址（国外）
git clone https://github.com/openclaw/openclaw.git
```

**相关文档**:
- **[网络问题-国内镜像.md](./网络问题-国内镜像.md)** 🆕 完整说明和使用指南

**速度提升**: 50-100倍 🚀

---

### 2. ⭐⭐⭐⭐⭐ 虚拟环境管理 🆕

**症状**: 跨机器环境不一致 / 系统没有Python / 依赖冲突

**解决方案**: 使用 env-checker 技能包

**快速操作**:
```bash
# macOS/Linux
bash skills/env-checker/scripts/setup.sh

# Windows
skills\env-checker\scripts\setup.bat
```

**独特优势**: 
- ✅ 自动检测和安装Python（系统没Python也能用）🌟
- ✅ 创建 `.venv/` 隐藏目录（不影响项目外观）
- ✅ 统一依赖管理
- ✅ 全自动化

**详细文档**:
- **[虚拟环境-env-checker使用.md](./虚拟环境-env-checker使用.md)** - env-checker 使用指南（新增）
- [虚拟环境管理规范.md](../03-规范约定/虚拟环境管理规范.md) - 详细规范
- [虚拟环境-快速上手.md](../01-使用指南/虚拟环境-快速上手.md) - 快速上手

---

### 1. ⭐⭐⭐⭐⭐ 飞书配对问题

**症状**: 飞书bot不回复 / 一直要求配对

**根本原因**: OpenClaw使用 `credentials/feishu-default-allowFrom.json`，不是 `paired.json`

**快速解决**:
```bash
python3 scripts/approve_feishu_pairing.py <instance-name>
```

**详细文档**:
- **[飞书配对-真正的解决方案.md](./飞书配对-真正的解决方案.md)** - 完整方案（最新）
- [飞书配对问题-完整解决方案.md](./飞书配对问题-完整解决方案.md) - 旧版本（部分过时）
- ~~[飞书配对-核心要点.md](./飞书配对-核心要点.md)~~ - 已过时

---

### 2. ⭐⭐⭐⭐ Unknown model 错误

**症状**: AI回复时报 "Unknown model: bailian/xxx"

**根本原因**: 实例的 `openclaw.json` 缺少 `models.providers` 配置

**快速解决**:
```bash
python3 scripts/fix_all_models.py
python3 skills/openclaw-manager/scripts/instance_manager.py restart <name>
```

**详细文档**:
- [模型Unknown问题-解决方案.md](./模型Unknown问题-解决方案.md)

---

### 3. ⭐⭐⭐ WebUI 无法访问

**症状**: 浏览器显示 "unauthorized: gateway token missing"

**根本原因**: 访问URL缺少token参数

**快速解决**:
```bash
# 使用 status 命令，会自动显示带token的完整URL
python3 skills/openclaw-manager/scripts/instance_manager.py status <name>
```

**详细文档**:
- [WebUI访问-改进完成.md](./WebUI访问-改进完成.md)
- [WebUI访问-Token问题解决.md](./WebUI访问-Token问题解决.md)

---

### 4. ⭐⭐⭐⭐ AI 助手假设实例存在 🆕

**症状**: 新机器上使用时，AI 自动使用不存在的实例名（如 openclaw-feishu-demo）

**根本原因**: 文档中硬编码了示例实例名，AI 误以为是真实实例

**解决方案**:
- ✅ AGENTS.md 已添加"先检查实例"的警告
- ✅ 所有文档改用通用占位符 `<实例名>`
- ✅ 新增《新机器首次使用指南》

**详细文档**:
- [AI助手假设实例存在-解决方案.md](./AI助手假设实例存在-解决方案.md) 🆕

---

## 🛠️ 工具和脚本

| 工具 | 解决什么问题 | 命令 |
|------|-------------|------|
| `approve_feishu_pairing.py` | 飞书配对 | `python3 scripts/approve_feishu_pairing.py <name>` |
| `fix_all_models.py` | Unknown model | `python3 scripts/fix_all_models.py` |
| `health_check.py` | 健康检查 | `python3 scripts/health_check.py [name]` |
| `instance_manager.py` | 实例管理 | `python3 skills/openclaw-manager/scripts/instance_manager.py <cmd> <name>` |

---

## 📖 辅助文档

| 文档 | 用途 |
|------|------|
| [系统健康检查报告-20260311.md](./系统健康检查报告-20260311.md) | 健康检查示例 |
| [预防措施-实施完成.md](./预防措施-实施完成.md) | 自动化预防机制 |
| [自动化预防措施-总结.md](./自动化预防措施-总结.md) | 预防措施总结 |
| [经验积累-实施总结.md](./经验积累-实施总结.md) | 经验库建立过程 |
| [经验库-建立说明.md](./经验库-建立说明.md) | 经验库价值说明 |
| [经验库-建立完成.md](./经验库-建立完成.md) | 经验库完成报告 |
| [经验库-使用检查清单.md](./经验库-使用检查清单.md) | 操作检查清单 |

---

## 🔍 快速查找

### 按关键词搜索

```bash
# 搜索问题相关文档
grep -r "关键词" docs/02-问题解决/

# 或使用 rg
rg "关键词" docs/02-问题解决/
```

### 常用关键词

- **配对** / **pairing** → 飞书配对问题
- **Unknown model** → 模型错误
- **token** / **unauthorized** → WebUI访问
- **启动** / **start** / **failed** → 启动问题

---

## 💡 使用技巧

1. **先看文档标题** - 快速定位相关文档
2. **看"快速解决"** - 直接运行命令
3. **看"根本原因"** - 理解为什么
4. **运行自动化工具** - 一键解决
