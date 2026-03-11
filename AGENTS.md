# AGENTS 配置 - OpenClaw 管理助手

> **这是什么**: 项目能力说明书，告诉 AI 助手本项目的功能、结构和使用方法  
> **目标用户**: Cursor IDE 中的 AI 助手  
> **作用**: 让 AI 理解项目，提供正确的帮助

---

## 🎯 项目简介

这是一个 **OpenClaw 管理技能包集合**，通过自然语言与 AI 交互，完成 OpenClaw（个人AI助手）的安装、部署、配置和管理。

**核心价值**:
- 🦞 管理多个 OpenClaw 实例（"龙虾军团"）
- 🔌 配置多平台集成（飞书、QQ、企业微信、钉钉）
- 🤖 管理 AI 模型和智能体
- 🚀 支持多种部署方式（主机、Docker、K8s）

---

## ⚠️ 重要提示 - AI 助手必读

### 🔴 必须使用虚拟环境！

**强制规范**: **所有 Python 脚本必须在项目虚拟环境中运行**

**使用 env-checker 技能包** 🌟

**正确的命令格式**:
```bash
# ✅ 使用虚拟环境中的 Python（绝对路径）
/path/to/agent-openclaw-assisant/.venv/bin/python \
  skills/openclaw-manager/scripts/instance_manager.py list

# ❌ 不要使用系统 Python
python3 skills/openclaw-manager/scripts/instance_manager.py list
```

**虚拟环境路径**:
1. **macOS/Linux**: `<项目根目录>/.venv/bin/python`
2. **Windows**: `<项目根目录>\.venv\Scripts\python.exe`

**注意**: 是 `.venv`（带点，隐藏目录），不是 `venv`

---

**虚拟环境不存在时，使用 env-checker 创建**:

```bash
# macOS/Linux
bash skills/env-checker/scripts/setup.sh

# Windows
skills\env-checker\scripts\setup.bat
```

**env-checker 的优势** 🌟:
- ✅ **自动检测和安装Python** - 系统没Python也能用！
- ✅ **全自动化** - 无需人工干预
- ✅ **自动验证** - 确保所有依赖可用
- ✅ **跨平台** - macOS/Linux/Windows

**详细文档**: [虚拟环境管理规范.md](docs/03-规范约定/虚拟环境管理规范.md)

**记住**: 
- ✅ AI 执行所有 Python 脚本时，必须使用 `.venv/bin/python`
- ✅ 虚拟环境目录是 `.venv`（隐藏目录）
- ✅ 使用 env-checker 创建虚拟环境
- ❌ 禁止使用 `python3` 或系统 Python
- ❌ 禁止在根目录创建 `venv/` 目录

---

### 🚨 不要假设用户已有实例！

**问题**: 文档中的示例命令（如 `openclaw-feishu-2774`）仅作**示例**，不代表用户机器上有该实例。

**正确做法**:
1. 🔍 **先检查实例是否存在**:
   ```bash
   /path/to/.venv/bin/python skills/openclaw-manager/scripts/instance_manager.py list
   ```

2. 📋 **如果列表为空**:
   - 说明是新机器或未创建实例
   - 引导用户创建实例
   - 询问实例名称、平台类型

3. 📋 **如果列表有实例**:
   - 使用列表中实际存在的实例名
   - 不要使用文档示例中的名称

**示例对话**:
```
错误方式:
用户: "帮我配置飞书"
AI: "好的，我为 openclaw-feishu-2774 配置飞书..."  ❌ (假设存在)

正确方式:
用户: "帮我配置飞书"
AI: "让我先检查现有实例..."
    [执行 instance_manager.py list]
    "您还没有创建实例，我帮您创建一个吗？请提供:"
    "1. 实例名称（如 openclaw-feishu-001）"
    "2. 飞书 App ID 和 Secret"  ✅
```

---

## 📦 技能包总览

本项目包含 **7个技能包**，每个技能包都是独立的功能模块：

### 0. 🐍 env-checker（环境初始化）⭐ 必须先执行

**位置**: `skills/env-checker/`  
**功能**: 全自动Python环境检测、安装和虚拟环境初始化  
**主要脚本**: 
- `skills/env-checker/scripts/setup.sh` (macOS/Linux)
- `skills/env-checker/scripts/setup.bat` (Windows)
- `skills/env-checker/scripts/verify.py` (验证)

**能力**:
- 检测系统Python版本
- **自动下载和安装Python**（如果系统没有）🌟
- 创建项目虚拟环境（`.venv/`）
- 安装所有技能包依赖
- 自动验证环境可用性

**使用场景**:
```
用户: "帮我初始化环境"
用户: "创建虚拟环境"
用户: "系统没有Python怎么办"
```

**重要**: 所有其他技能包的脚本都必须在 env-checker 创建的虚拟环境中运行！

---

### 1. 🔧 openclaw-manager（核心）

**位置**: `skills/openclaw-manager/`  
**功能**: OpenClaw 的安装、实例创建和生命周期管理  
**主要脚本**: `skills/openclaw-manager/scripts/instance_manager.py`

**能力**:
- 安装 OpenClaw
- 创建/删除实例
- 启动/停止/重启实例
- 查看实例状态和日志
- ⭐ **健康检查**（命名规范、模型配置、配对状态）

**使用场景**:
```
用户: "帮我安装 OpenClaw"
用户: "创建一个飞书实例"
用户: "启动实例"
用户: "查看所有实例状态"
用户: "检查实例健康状况"
```

**命令格式**:
```bash
# 健康检查（所有实例）
.venv/bin/python skills/openclaw-manager/scripts/instance_manager.py health-check

# 健康检查（单个实例）
.venv/bin/python skills/openclaw-manager/scripts/instance_manager.py health-check <实例名>
```

---

### 2. 🚀 openclaw-deploy

**位置**: `skills/openclaw-deploy/`  
**功能**: 部署管理（主机模式、Docker、K8s）  
**主要脚本**: `skills/openclaw-deploy/scripts/deploy_*.sh`

**能力**:
- Systemd 服务部署
- Docker 容器部署
- Kubernetes 部署
- 健康检查配置

**使用场景**:
```
用户: "把实例部署为 Systemd 服务"
用户: "把实例部署到 Docker"
```

---

### 3. 🔌 openclaw-plugin

**位置**: `skills/openclaw-plugin/`  
**功能**: 插件安装和管理  
**主要脚本**: `skills/openclaw-plugin/scripts/plugin_manager.py`

**能力**:
- 列出可用插件
- 安装/卸载插件
- 更新插件
- 查看插件状态

**支持的插件**: 飞书、QQ、企业微信、钉钉

**使用场景**:
```
用户: "为实例安装飞书插件"
用户: "查看所有可用插件"
```

---

### 4. 📡 openclaw-channel

**位置**: `skills/openclaw-channel/`  
**功能**: 渠道配置和凭证管理  
**主要脚本**: `skills/openclaw-channel/scripts/channel_manager.py`

**能力**:
- 添加/删除渠道
- 加密存储凭证（App ID、Secret）
- 测试渠道连接
- 列出已配置渠道
- ⭐ **批准配对请求**（飞书、QQ等）

**使用场景**:
```
用户: "为实例配置飞书渠道"
     "App ID 是 cli_xxxxx，Secret 是 yyyyy"
用户: "批准飞书配对请求"
```

**命令格式**:
```bash
# 批准配对（自动重启）
python skills/openclaw-channel/scripts/channel_manager.py approve-pairing \
  --instance <实例名> \
  --platform feishu

# 批准配对（不自动重启）
python skills/openclaw-channel/scripts/channel_manager.py approve-pairing \
  --instance <实例名> \
  --platform feishu \
  --no-restart
```

---

### 5. 🤖 openclaw-model

**位置**: `skills/openclaw-model/`  
**功能**: AI 模型配置和管理  
**主要脚本**: `skills/openclaw-model/scripts/model_manager.py`

**能力**:
- 添加/删除模型
- 配置 API Key（加密存储）
- 测试模型连接
- 设置默认模型
- ⭐ **修复模型配置**（批量修复 "Unknown model" 问题）
- ⭐ **模板初始化**（一键导入常用模型配置） 🆕

**支持的模型**: OpenAI GPT-4/3.5、Anthropic Claude、百炼等

**使用场景**:
```
用户: "为实例添加 GPT-4 模型，API Key 是 sk-xxxxx"
用户: "设置默认模型为 bailian/qwen3.5-plus"
用户: "修复所有实例的模型配置"
用户: "用百炼模板初始化模型配置" 🆕
```

**命令格式**:
```bash
# 🆕 一键初始化（推荐！）
python skills/openclaw-model/scripts/model_manager.py init-from-template \
  bailian-coding-models \
  <your-api-key> \
  --instance <实例名>

# 查看可用模板
python skills/openclaw-model/scripts/model_manager.py list-templates

# 修复所有实例
python skills/openclaw-model/scripts/model_manager.py fix-config

# 修复单个实例
python skills/openclaw-model/scripts/model_manager.py fix-config <实例名>
```

---

### 6. 👥 openclaw-agent

**位置**: `skills/openclaw-agent/`  
**功能**: 智能体创建和路由配置  
**主要脚本**: `skills/openclaw-agent/scripts/agent_manager.py`

**能力**:
- 创建/删除智能体
- 绑定模型
- 配置渠道路由
- 管理多智能体

**使用场景**:
```
用户: "创建一个客服智能体，使用 GPT-4，对接飞书"
```

---

## 📁 项目结构

```
agent-openclaw-assisant/
│
├── README.md                    # 项目主README
├── AGENTS.md                    # 本文件（能力说明书）
│
├── skills/                      # ⭐ 技能包（完整功能）
│   ├── openclaw-manager/        # 实例管理（含健康检查）
│   │   ├── SKILL.md            # 技能说明
│   │   └── scripts/            # 核心脚本
│   │       └── instance_manager.py
│   ├── openclaw-deploy/         # 部署管理
│   ├── openclaw-plugin/         # 插件管理
│   ├── openclaw-channel/        # 渠道管理（含配对批准）
│   ├── openclaw-model/          # 模型管理（含配置修复）
│   └── openclaw-agent/          # 智能体管理
│
├── docs/                        # 📚 项目文档
│   ├── README.md               # 文档总索引
│   ├── 02-问题解决/             # ⭐⭐⭐⭐⭐ 核心！问题解决经验库
│   │   ├── README.md           # 问题索引
│   │   ├── 飞书配对-真正的解决方案.md
│   │   └── 处理问题-必读指南.md
│   ├── 01-使用指南/             # 日常使用
│   ├── 03-规范约定/             # 必须遵守
│   └── 04-技术参考/             # 深入理解
│
├── workspace/                   # 实例工作空间
│   └── lobsters/               # 所有龙虾实例
│       └── <实例名>/           # 如: openclaw-feishu-2774
│
└── shared/                      # 共享资源
```

---

## 🚨 处理问题前必读

**每次处理问题或用户咨询时，必须先查经验库**：

### 第1步: 查问题解决目录

```
路径: docs/02-问题解决/README.md
目的: 查找是否有相关经验
```

### 第2步: 如果找到相关经验

- 完整阅读经验文档
- 理解根本原因和源码逻辑
- 按文档步骤操作

### 第3步: 如果没有相关经验

- 排查问题并记录新经验
- 更新问题解决索引

**为什么必须这样做**：
- ✅ 避免重复犯错（如飞书配对问题反复出现）
- ✅ 快速定位问题（节省80%时间）
- ✅ 积累知识（团队共享）

**重点文档**：
- 📚 [02-问题解决/README.md](docs/02-问题解决/README.md) - 问题索引
- 🎯 [处理问题-必读指南](docs/02-问题解决/处理问题-必读指南.md) - 标准流程
- ⭐ [飞书配对-真正的解决方案](docs/02-问题解决/飞书配对-真正的解决方案.md) - 高频问题

---

## 📐 规范约定

### 1. 文档编写规范

**文档**: [docs/03-规范约定/文档编写规范.md](docs/03-规范约定/文档编写规范.md)

**核心原则**：
- ✅ 所有文档必须放在 `docs/` 的子目录下
- ❌ **禁止**在项目根目录创建文档文件
- ✅ 按类型分类：01-使用指南/02-问题解决/03-规范约定/04-技术参考

**根目录只允许**：
- `README.md` - 项目主README
- `AGENTS.md` - 本文件
- 配置文件（.gitignore, requirements.txt等）

**常见错误**：
- ❌ 在根目录创建 `快速入门.md`, `DEPLOYMENT.md`, `分析报告.md`
- ✅ 应该放在 `docs/01-使用指南/`, `docs/04-技术参考/`, `docs/99-历史归档/`

---

### 2. 龙虾命名规范

**文档**: [docs/03-规范约定/龙虾命名规范.md](docs/03-规范约定/龙虾命名规范.md)

**格式**: `openclaw-{platform}-{sequence}`

**示例**:
- ✅ `openclaw-feishu-2774` (飞书实例)
- ✅ `openclaw-qq-001` (QQ实例)
- ✅ `openclaw-wecom-100` (企业微信实例)
- ❌ `my-bot` (不符合规范)
- ❌ `OpenClaw-Feishu-2774` (大写字母)

---

### 3. 跨平台要求

**禁止**：
- ❌ Shell 脚本（.sh, .bash）
- ❌ Windows 批处理（.bat, .cmd）
- ❌ 平台特定的命令

**使用**：
- ✅ Python 3.8+ 脚本
- ✅ 跨平台的工具

**原因**: Windows 无法运行 Shell 脚本

---

### 4. 文件操作

- 使用 `json.load/dump` 处理JSON
- 使用 `with open()` 确保文件关闭
- 使用 `ensure_ascii=False` 支持中文

---

## 🎯 使用指南

### 工作流程

当用户请求时：

1. **🔍 检查现状** - 先执行 `instance_manager.py list` 查看是否有实例
2. **理解需求** - 用户想做什么？
3. **确定技能包** - 需要哪个技能包？
4. **查看文档** - 阅读对应的 SKILL.md（如需要）
5. **执行操作** - 调用对应的脚本
6. **验证结果** - 确认操作成功

### 示例 1：新机器首次使用

```
用户: "创建一个飞书客服机器人"

AI 的正确流程：
0. 🐍 **检查虚拟环境**:
   检查: ls -la .venv/bin/python
   如果不存在: 引导创建
     "您还没有创建虚拟环境，我先帮您初始化环境..."
     macOS/Linux: bash skills/env-checker/scripts/setup.sh
     Windows: skills\env-checker\scripts\setup.bat
   确定 Python 路径: <项目根>/.venv/bin/python

1. 🔍 **先检查现状**:
   执行: <.venv/bin/python> skills/openclaw-manager/scripts/instance_manager.py list
   结果: 总计: 0 个实例

2. ✅ **确认是新环境，引导创建**:
   "您还没有创建实例，我帮您创建一个飞书机器人实例。"
   
3. 📝 **询问必要信息**:
   - "实例名称（建议格式: openclaw-feishu-XXX）"
   - "飞书 App ID"
   - "飞书 App Secret"
   - "API Key（用于百炼模型）"

4. 🚀 **执行创建流程**（所有命令使用 .venv/bin/python）:
   Step 1: <.venv/bin/python> instance_manager.py create <用户提供的名称>
   Step 2: <.venv/bin/python> init-from-template bailian-coding-models <apikey> --instance <名称>
   Step 3: <.venv/bin/python> plugin_manager.py install feishu <名称>
   Step 4: <.venv/bin/python> channel_manager.py add <名称> feishu --app-id <id> --app-secret <secret>
   Step 5: <.venv/bin/python> instance_manager.py start <名称>

5. ✅ **验证并报告**:
   - 查看实例状态
   - 提供访问地址
```

### 示例 2：已有实例的场景

```
用户: "配置飞书渠道"

AI 的正确流程：
0. 🐍 **确保使用虚拟环境 Python**:
   Python 路径: <项目根>/.venv/bin/python

1. 🔍 **先检查现状**:
   执行: <.venv/bin/python> skills/openclaw-manager/scripts/instance_manager.py list
   结果: 
   - openclaw-feishu-2774 (已有)
   - openclaw-qq-001 (已有)

2. ✅ **使用实际存在的实例**:
   "您有 2 个实例，请问要为哪个实例配置飞书？"
   或："我看到您有实例 openclaw-feishu-2774，要为它配置吗？"

3. 📝 **询问缺失信息**:
   - "请提供飞书 App ID"
   - "请提供飞书 App Secret"

4. 🚀 **执行配置**（使用 .venv/bin/python）:
   使用用户选择的实例名
```

---

## ✨ 技能包功能完整

所有功能都已整合到技能包中，**不再需要外部脚本**！

| 技能包 | 核心功能 | 新增功能 |
|--------|---------|---------|
| openclaw-manager | 创建、启动、停止、日志 | ⭐ **健康检查** |
| openclaw-deploy | Systemd、Docker、K8s | - |
| openclaw-plugin | 安装、卸载、更新插件 | - |
| openclaw-channel | 添加、删除、测试渠道 | ⭐ **配对批准** |
| openclaw-model | 添加、删除、测试模型 | ⭐ **配置修复**、⭐ **模板初始化** 🆕 |
| openclaw-agent | 创建、绑定智能体 | - |

**架构原则**:
- ✅ 技能包自包含，功能完整
- ✅ 不依赖外部脚本
- ✅ 所有功能统一入口

---

## 📚 文档导航

### 遇到问题？

**第一步：查经验库**
- 📚 [docs/02-问题解决/README.md](docs/02-问题解决/README.md)

**高频问题**:
- 飞书不回复 → [飞书配对-真正的解决方案](docs/02-问题解决/飞书配对-真正的解决方案.md)
- Unknown model → [模型Unknown问题-解决方案](docs/02-问题解决/模型Unknown问题-解决方案.md)
- WebUI访问 → [WebUI访问-改进完成](docs/02-问题解决/WebUI访问-改进完成.md)

---

### 日常使用

- 📖 [docs/01-使用指南/工具链使用指南.md](docs/01-使用指南/工具链使用指南.md)
- 📖 [docs/01-使用指南/FAQ.md](docs/01-使用指南/FAQ.md)
- 📖 [docs/01-使用指南/快速入门.md](docs/01-使用指南/快速入门.md)

---

### 规范约定

- 📐 [docs/03-规范约定/README.md](docs/03-规范约定/README.md)
- 📐 **[docs/03-规范约定/Python版本要求.md](docs/03-规范约定/Python版本要求.md)** 🆕 Python版本定义
- 📐 **[docs/03-规范约定/虚拟环境管理规范.md](docs/03-规范约定/虚拟环境管理规范.md)** 🔴 必读！
- 📐 [docs/03-规范约定/文档编写规范.md](docs/03-规范约定/文档编写规范.md)
- 📐 [docs/03-规范约定/龙虾命名规范.md](docs/03-规范约定/龙虾命名规范.md)

---

### 技术参考

- 📚 [docs/04-技术参考/架构设计.md](docs/04-技术参考/架构设计.md)
- 📚 [docs/04-技术参考/项目概览.md](docs/04-技术参考/项目概览.md)
- 📚 [docs/04-技术参考/DEPLOYMENT.md](docs/04-技术参考/DEPLOYMENT.md)

---

## 💡 记住这些

### 核心原则

1. **🔴 强制使用虚拟环境** - 所有 Python 脚本必须用 `venv/bin/python` 执行
2. **先查经验库** - 避免重复犯错
3. **优先用技能包** - 不要直接调用根目录脚本
4. **理解项目结构** - 知道每个技能包的作用
5. **遵守规范** - 文档编写、命名、跨平台
6. **记录经验** - 解决问题后更新经验库

---

### 快速参考

**⚠️ 重要**: 所有命令必须使用虚拟环境中的 Python: `.venv/bin/python` (或 Windows: `.venv\Scripts\python.exe`)

| 需求 | 使用技能包 | 命令示例 |
|------|-----------|---------|
| **初始化环境** 🔴 | env-checker | `bash skills/env-checker/scripts/setup.sh` |
| **验证环境** | env-checker | `.venv/bin/python skills/env-checker/scripts/verify.py` |
| 创建实例 | openclaw-manager | `.venv/bin/python ...instance_manager.py create <实例名>` |
| 查看实例列表 | openclaw-manager | `.venv/bin/python ...instance_manager.py list` |
| 健康检查 | openclaw-manager | `.venv/bin/python ...instance_manager.py health-check [实例名]` |
| 部署服务 | openclaw-deploy | `deploy_systemd.sh <实例名>` |
| 安装插件 | openclaw-plugin | `.venv/bin/python ...plugin_manager.py install <插件> <实例名>` |
| 配置渠道 | openclaw-channel | `.venv/bin/python ...channel_manager.py add <实例名> <平台>` |
| 飞书配对 | openclaw-channel | `.venv/bin/python ...channel_manager.py approve-pairing --instance <实例名>` |
| **一键初始化模型** 🆕 | openclaw-model | `.venv/bin/python ...model_manager.py init-from-template <模板> <apikey> --instance <实例名>` |
| 添加模型 | openclaw-model | `.venv/bin/python ...model_manager.py add <提供商> <模型ID> <apikey>` |
| 修复模型配置 | openclaw-model | `.venv/bin/python ...model_manager.py fix-config [实例名]` |
| 创建智能体 | openclaw-agent | `.venv/bin/python ...agent_manager.py create <名称> <模型>` |

**注**: 
- `...` 代表脚本的完整路径，如 `skills/openclaw-manager/scripts/`
- `.venv` 是隐藏目录（带点），不是 `venv`

---

## 🎉 总结

这个项目是一个 **完整的 OpenClaw 管理系统**：

- **6个技能包** - 覆盖所有核心功能
- **完整的文档** - 包括问题解决经验库
- **严格的规范** - 确保跨平台兼容
- **自动化工具** - 提高效率，减少错误

**作为 AI 助手，你应该**：
1. **🔴 强制使用虚拟环境** - 所有命令用 `.venv/bin/python` 执行
2. **🔴 使用 env-checker 创建虚拟环境** - 不要手动创建
3. **🔴 虚拟环境是 `.venv`（隐藏目录）** - 不是 `venv`
4. 理解项目结构和技能包
5. 查经验库，避免重复犯错
6. 优先使用技能包，而不是直接执行脚本
7. 遵守规范约定
8. 记录新经验

---

**最后更新**: 2026-03-11  
**维护者**: OpenClaw Assistant Team
