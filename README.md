# OpenClaw 管理技能包集合

> 为 Cursor / Claude Desktop / Coder / Trae 打造的 OpenClaw 管理技能包仓库，提供完整的 OpenClaw 实例生命周期管理能力。

[![Version](https://img.shields.io/badge/version-v1.0.0-brightgreen)](docs/CHANGELOG.md)
[![Status](https://img.shields.io/badge/status-✅%20可用-success)](docs/STATUS.md)
[![Skills](https://img.shields.io/badge/skills-6%2F6-blue)](docs/技能包索引.md)
[![Docs](https://img.shields.io/badge/docs-14-informational)](docs/)
[![GitHub](https://img.shields.io/badge/github-openclaw%2Fopenclaw-blue)](https://github.com/openclaw/openclaw)
[![Gitee](https://img.shields.io/badge/gitee-国内镜像-red)](https://gitee.com/618lf/openclaw)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

## 🎉 项目状态

**✅ 核心功能已完成，可以立即使用！**

| 指标 | 状态 | 说明 |
|------|------|------|
| **版本** | v1.0.0 | 首个正式版本 |
| **核心功能** | ✅ 100% | 7个技能包全部完成 |
| **文档** | ✅ 100% | 40+ 篇文档 |
| **可用性** | 🟢 立即可用 | 可投入使用 |

## ✨ 核心特点

### 🎯 说人话就能用！

**不需要**:
- ❌ 记命令
- ❌ 看文档
- ❌ 懂技术

**只需要**:
- ✅ 在 AI IDE 中说话（Cursor / Claude Desktop / Coder / Trea）
- ✅ AI 自动引导
- ✅ 3分钟完成

### ⚡ 激进模式：开箱即用！

**默认配置采用"激进模式"（零门槛配置）**：
- ✅ **Control UI**：完全无需认证，直接访问！
- ✅ **渠道策略**：开放模式，无需配对即可使用
- ✅ **局域网访问**：支持局域网内其他设备访问

**技术方案**：
- **主机模式**：loopback 绑定 + auth.mode=none（仅本机访问）
- **Docker 模式**：Nginx 代理 + loopback OpenClaw（局域网可访问，完全无认证）

**这意味着**：
- 创建实例后立即可用
- **无需任何 Token**，直接访问 URL
- 添加渠道后立即可收发消息
- 无需手动批准配对请求
- 适合快速测试和开发环境

**访问示例**：
- 主机模式：`http://127.0.0.1:18800/`
- Docker 模式：`http://127.0.0.1:18900/`（或局域网 IP）

**生产环境**？查看 [openclaw配置文件完全解读.md](docs/03-技术解读/openclaw配置文件完全解读.md) 了解如何切换到安全模式。

---

## 🚀 3步上手（这就是全部！）

### 📍 第1步：初始化环境（30秒）

```bash
# macOS/Linux
bash skills/env-checker/scripts/setup.sh

# Windows
skills\env-checker\scripts\setup.bat
```

**完成！** 环境已就绪。

---

### 💬 第2步：在 AI IDE 中说话

打开 Cursor / Claude Desktop / Coder / Trea，直接说：

```
💬 "创建一个飞书机器人"
💬 "配置企业微信渠道"  
💬 "查看所有实例"
💬 "启动 openclaw-feishu-001"
```

**AI 会自动引导你，不用担心！**

---

### 🎉 第3步：开始使用

AI 完成配置后，会告诉你机器人地址。

访问地址，发消息测试 → **完成！**

---

## 💡 示例对话（你可以这样说）

### 场景 1：创建机器人

```
💬 你: "创建一个飞书机器人"

🤖 AI: "好的！需要提供：
      1. 实例名（如 openclaw-feishu-001）
      2. 飞书 App ID
      3. 飞书 App Secret
      4. API Key"
    
💬 你: [提供信息]

🤖 AI: "✅ 完成！访问 http://127.0.0.1:18800"
```

### 场景 2：查看状态

```
💬 你: "查看所有实例"
🤖 AI: [显示实例列表和运行状态]
```

### 场景 3：解决问题

```
💬 你: "飞书不回复"
🤖 AI: "✅ 已批准配对并重启，请测试"
```

**更多示例** → [快速入门.md](docs/01-使用指南/快速入门.md)

---

## 📖 这是什么项目？

这是一个专为管理 **OpenClaw**（个人AI助手）而设计的 AI IDE 技能包集合，支持 Cursor、Claude Desktop、Coder 和 Trea。

**OpenClaw**：开源的个人AI助手平台，支持飞书、QQ、企业微信、钉钉等多种消息平台。
- GitHub: https://github.com/openclaw/openclaw
- Gitee 镜像（国内）: https://gitee.com/618lf/openclaw 🇨🇳

**本项目让你**：通过自然语言与 AI IDE 交互（Cursor / Claude Desktop / Coder / Trea），即可完成 OpenClaw 的安装、部署、配置和管理。

### 支持的平台

- ✅ 飞书 (Feishu)
- ✅ QQ
- ✅ 企业微信 (WeCom)
- ✅ 钉钉 (DingTalk)

---

## 📚 更多信息（可选阅读）

### 💭 常见问题

**Q: 我不会Python怎么办？**  
A: 不需要！env-checker 会自动安装 Python，你只需要说话。

**Q: GitHub 访问很慢怎么办？** 🇨🇳  
A: 使用国内 Gitee 镜像：`https://gitee.com/618lf/openclaw.git`（速度提升 50-100 倍）

**Q: 出错了怎么办？**  
A: 告诉 AI "出错了"或"飞书不回复"，AI 会自动诊断和修复。

**Q: 支持哪些平台？**  
A: 飞书、QQ、企业微信、钉钉。

**更多问题** → [FAQ.md](docs/01-使用指南/FAQ.md)

---

### 🛠️ 详细文档

| 文档 | 用途 |
|------|------|
| [快速入门.md](docs/01-使用指南/快速入门.md) | 详细的使用示例和对话 |
| [新机器首次使用.md](docs/01-使用指南/新机器首次使用.md) | 从零开始的完整流程 |
| [FAQ.md](docs/01-使用指南/FAQ.md) | 45+ 个常见问题解答 |
| [技能包职责划分.md](docs/03-规范约定/技能包职责划分.md) | 架构说明（开发者） |

---

### 工作原理（技术说明）

本项目通过 7 个技能包自动管理 OpenClaw：
- **env-checker**: 环境检测和初始化
- **openclaw-manager**: 实例管理
- **openclaw-channel**: 渠道配置
- **openclaw-model**: AI 模型配置
- **openclaw-plugin**: 插件管理
- **openclaw-deploy**: 部署管理
- **openclaw-agent**: 智能体管理

**你不需要了解这些细节，AI 会自动处理！**

详见 [技能包索引.md](docs/技能包索引.md)

---

## 🔧 高级配置（开发者）

### 系统要求

- AI IDE（Cursor / Claude Desktop / Coder / Trea，任选其一）
- Python 3.10+（env-checker 会自动安装）
- Git（必需）
- Node.js 18+（可选，安装 OpenClaw 时需要）
- Docker（可选，容器部署时需要）

### 手动安装

#### 前置步骤：检查和创建虚拟环境

**🆕 快速检查虚拟环境**（跨平台）:
```bash
# macOS/Linux
bash skills/env-checker/scripts/check.sh

# Windows
skills\env-checker\scripts\check.bat

# 输出示例（不存在）：
#   VENV_EXISTS=false
#   SETUP_COMMAND=bash /path/to/skills/env-checker/scripts/setup.sh

# 输出示例（已存在）：
#   VENV_EXISTS=true
#   VENV_PYTHON=/path/to/.venv/bin/python
```

**🔴 如果虚拟环境不存在，创建它**:
```bash
# macOS/Linux
bash skills/env-checker/scripts/setup.sh

# Windows
skills\env-checker\scripts\setup.bat
```

**env-checker 的特殊优势** 🌟:
- ✅ 自动检测和安装Python（系统没Python也能用！）
- ✅ 全自动化，无需人工干预
- ✅ 创建隐藏的 `.venv/` 目录，不影响项目外观

---

#### 方式一：作为项目技能包（推荐）

1. 在 AI IDE（Cursor / Claude Desktop / Coder / Trea）中打开此项目
2. AI IDE 会自动识别 `.cursor/skills/`、`.claude/skills/`、`.coder/skills/` 或 `.trae/skills/` 目录下的所有技能包
3. 通过自然语言与 AI 交互即可使用

```
示例：
- "帮我初始化环境"  🔴 第一步（使用 env-checker）
- "帮我安装 OpenClaw"
- "创建一个飞书实例"
- "为实例安装飞书插件"
- "用百炼模板初始化模型" 🆕
```

**🆕 新机器首次使用**:
- 查看 [新机器首次使用指南](docs/01-使用指南/新机器首次使用.md)
- AI 会先检查虚拟环境和实例列表
- 系统没Python也能用（env-checker 自动安装）

#### 方式二：安装到个人技能包目录

```bash
# 安装所有技能包
cp -r skills/* ~/.cursor/skills/

# 或安装单个技能包
cp -r skills/openclaw-manager ~/.cursor/skills/
```

## 📚 使用示例

### 示例 1: 创建第一个 OpenClaw 实例

```
用户: 帮我安装 OpenClaw 并创建一个实例

AI 会自动:
1. 检测系统环境
2. 下载并安装 OpenClaw
3. 创建实例 openclaw-prod-01
4. 初始化工作空间
5. 返回实例信息和启动命令
```

### 示例 2: 部署到 Docker

```
用户: 把 openclaw-prod-01 部署到 Docker 容器

AI 会自动:
1. 生成 Dockerfile 和 docker-compose.yml
2. 构建 Docker 镜像
3. 启动容器
4. 配置健康检查
5. 返回容器访问信息
```

### 示例 3: 配置飞书渠道

```
用户: 为 openclaw-prod-01 配置飞书渠道，App ID 是 xxx，Secret 是 yyy

AI 会自动:
1. 安装飞书插件（如未安装）
2. 添加飞书渠道配置
3. 加密存储 App Secret
4. 测试连接
5. 返回配置状态
```

### 示例 4: 创建智能体

```
用户: 在 openclaw-prod-01 中创建一个客服智能体，使用 GPT-4，对接飞书

AI 会自动:
1. 检查模型配置（如无则提示添加）
2. 创建智能体 openclaw-prod-01-agent-customer-service
3. 绑定 GPT-4 模型
4. 配置飞书渠道路由
5. 返回智能体信息
```

## 📁 项目结构

```
agent-openclaw-assisant/
├── docs/                     # 项目文档
│   └── 需求分析.md           # 详细需求分析
├── skills/                   # 技能包集合
│   ├── openclaw-manager/     # 核心管理技能包
│   ├── openclaw-deploy/      # 部署管理
│   ├── openclaw-plugin/      # 插件管理
│   ├── openclaw-channel/     # 渠道管理
│   ├── openclaw-model/       # 模型管理
│   └── openclaw-agent/       # 智能体管理
├── workspace/                # 实例工作空间（不提交，由OpenClaw管理）
├── shared/                   # 共享资源
├── tests/                    # 测试用例
├── .cursor/                 # Cursor 技能包激活（软链接）
├── .claude/                 # Claude Desktop 技能包激活（软链接）
├── .coder/                  # Coder 技能包激活（软链接）
├── .trae/                   # Trae 技能包激活（软链接）
├── .gitignore               # Git忽略规则
├── AGENTS.md                # AI 智能助手配置（核心入口）
├── CLAUDE.md                # AI 智能助手配置（AGENTS.md 副本）
└── README.md                # 本文件
```

## 🔒 安全与隐私

### 数据保护
- ✅ 所有运行数据存储在本地 `workspace/` 目录
- ✅ 敏感信息（API密钥、Token）加密存储
- ✅ 工作空间通过 .gitignore 排除，不会提交到Git
- ✅ 支持配置文件的权限控制

### 最佳实践
- 使用环境变量存储敏感信息
- 定期备份工作空间
- 使用独立的API密钥用于测试和生产
- 定期轮换凭证

## 🛣️ 开发路线图

### Phase 1: 基础能力 ✅（已完成）
- [x] 需求分析文档
- [x] 项目结构设计
- [x] openclaw-manager 技能包
- [x] 共享工具库

### Phase 2: 部署能力 ✅（已完成）
- [x] openclaw-deploy 技能包
- [x] 主机模式部署（systemd）
- [x] 容器模式部署（Docker）
- [x] K8s 部署支持

### Phase 3: 插件与渠道 ✅（已完成）
- [x] openclaw-plugin 技能包
- [x] openclaw-channel 技能包
- [x] 四大平台集成（飞书、QQ、企业微信、钉钉）
- [x] 凭证加密管理

### Phase 4: 模型与智能体 ✅（已完成）
- [x] openclaw-model 技能包
- [x] openclaw-agent 技能包
- [x] 多模型支持（OpenAI、Anthropic、本地）
- [x] 多智能体配置

### Phase 5: 技能包激活 ✅（已完成）
- [x] .cursor/skills/ 目录创建
- [x] 软链接激活机制
- [x] 验证脚本

### Phase 6: 增强功能（待开发）
- [ ] 监控和告警系统
- [ ] 自动备份机制
- [ ] Web 管理界面（可选）
- [ ] 集群管理（可选）

## 📖 文档

### 🚨 遇到问题？

**直接查** → **[docs/02-问题解决/](docs/02-问题解决/)**

- 飞书不回复 → `02-问题解决/飞书配对-真正的解决方案.md`
- Unknown model → `02-问题解决/模型Unknown问题-解决方案.md`
- WebUI访问 → `02-问题解决/WebUI访问-改进完成.md`

---

### 📚 文档导航（按使用频率）

```
docs/
├── 快速开始.md              # 🚀 5分钟上手
├── 01-使用指南/             # 📖 日常使用
├── 02-问题解决/             # 🔧 故障排查（★核心）
├── 03-规范约定/             # 📐 必须遵守
└── 04-技术参考/             # 📚 深入理解
```

**详见**: [docs/README.md](docs/README.md)

---

### 核心文档
- ⭐ [AGENTS.md](AGENTS.md) - **智能入口配置**（意图识别+流程编排引擎）
- ⭐ [docs/02-问题解决/](docs/02-问题解决/) - **问题解决经验库**
- ⭐ [docs/01-使用指南/工具链使用指南.md](docs/01-使用指南/工具链使用指南.md) - 完整工具说明

### 入门文档
- 🚀 [快速开始](docs/快速开始.md) - 5分钟快速入门教程
- 💡 [使用示例](docs/使用示例.md) - 7个实战场景示例
- ❓ [常见问题](docs/FAQ.md) - 45+ 个常见问题解答
- 📚 [技能包索引](docs/技能包索引.md) - 所有技能包的功能和使用说明
- 🏗️ [项目结构](docs/项目结构.md) - 详细的目录结构说明

### 设计文档
- 📋 [需求分析](docs/需求分析.md) - 详细的需求分析和架构设计（v2.1）
- 🏛️ [架构设计](docs/架构设计.md) - 系统架构、数据流、设计决策
- 🧠 [智能入口设计](docs/智能入口设计.md) - AGENTS.md 的意图识别和流程编排设计 ⭐
- 🎨 [项目概览](docs/项目概览.md) - 架构全景图和设计亮点
- 📈 [开发进度](docs/开发进度.md) - 实时开发进度追踪
- 🎉 [项目完成总结](docs/项目完成总结.md) - 完成情况和交付物
- 📝 [文件清单](docs/文件清单.md) - 所有文件的完整清单

### 技术文档
- 🔬 [技术调研](docs/技术调研.md) - OpenClaw 技术调研结果（待创建）
- 🗂️ [工作空间管理](docs/工作空间管理.md) - 工作空间管理原则（重要）⭐

### 配置文档
- ⚙️ [全局配置](shared/configs/README.md) - 全局配置说明
- 📄 [配置模板](shared/configs/global.yaml.template) - 全局配置模板
- 🛠️ [工具函数](shared/utils/README.md) - 共享工具函数说明

### 重要说明
- 🗂️ [工作空间管理](docs/工作空间管理.md) - 工作空间管理原则（重要）⭐
- 📐 [工作空间设计说明](docs/工作空间设计说明.md) - 设计要点和检查清单

## 🤝 贡献

欢迎贡献代码、提出问题或建议！请阅读 [贡献指南](docs/CONTRIBUTING.md) 了解详情。

### 如何参与

- 🐛 [报告 Bug](../../issues)
- 💡 [提出建议](../../issues)
- 📖 [改进文档](../../pulls)
- 🔧 [提交代码](../../pulls)

详见 [CONTRIBUTING.md](docs/CONTRIBUTING.md)

## 📄 许可证

MIT License

---

**项目状态**: 🚧 开发中  
**最后更新**: 2026-03-10  
**维护者**: lifeng
