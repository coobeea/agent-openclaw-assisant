# Coder 技能包支持

本目录为 Coder 提供 OpenClaw 管理技能包支持。

## 🎯 多平台支持

OpenClaw 管理助手支持以下 AI 平台：

| 平台 | 技能包目录 | 状态 |
|------|-----------|------|
| **Cursor** | `.cursor/skills/` | ✅ 已激活 |
| **Claude Desktop** | `.claude/skills/` | ✅ 已激活 |
| **Coder** | `.coder/skills/` | ✅ 已激活 |
| **Trea** | `.trae/skills/` | ✅ 已激活 |

## 📂 目录结构

```
.coder/
├── README.md           ← 本文件（平台说明）
└── skills/             ← 技能包软链接目录
    ├── README.md       ← 技能包管理说明
    ├── openclaw-manager  → ../../skills/openclaw-manager
    ├── openclaw-deploy   → ../../skills/openclaw-deploy
    ├── openclaw-plugin   → ../../skills/openclaw-plugin
    ├── openclaw-channel  → ../../skills/openclaw-channel
    ├── openclaw-model    → ../../skills/openclaw-model
    └── openclaw-agent    → ../../skills/openclaw-agent
```

## 🚀 快速使用

### 在 Coder 中使用

1. 打开 Coder
2. 连接到本项目目录
3. 直接说话：

```
"查看所有实例"
"创建一个飞书机器人"
"初始化模型配置"
```

Coder 会自动识别并使用这些技能包。

## 📋 可用技能包

所有 6 个技能包已激活：

| 技能包 | 说明 | 示例 |
|--------|------|------|
| **openclaw-manager** | 实例生命周期管理 | "创建实例" |
| **openclaw-channel** | 渠道配置（飞书/QQ/企微/钉钉） | "配置飞书" |
| **openclaw-model** | AI 模型配置 | "初始化模型" |
| **openclaw-agent** | 智能体管理 | "创建智能体" |
| **openclaw-plugin** | 插件管理 | "安装插件" |
| **openclaw-deploy** | 部署管理 | "部署到 Docker" |

## 🔧 技能包管理

所有技能包的源文件位于 `../../skills/` 目录。

`.coder/skills/` 目录中的文件都是**软链接**，指向源文件。

**修改技能包**: 请编辑 `skills/` 目录下的源文件，所有平台会自动同步。

详细说明请查看：[skills/README.md](./skills/README.md)

## 🎨 与其他平台的关系

```
源文件: skills/
    ↓
    ├─ 软链接 → .cursor/skills/  (Cursor 使用)
    ├─ 软链接 → .claude/skills/  (Claude Desktop 使用)
    ├─ 软链接 → .coder/skills/   (Coder 使用)
    └─ 软链接 → .trae/skills/    (Trae 使用)
```

**核心原则**：
- ✅ 单一数据源（源文件在 `skills/`）
- ✅ 多平台共享（通过软链接）
- ✅ 统一管理（修改一处，所有平台生效）

## 📚 更多信息

- [项目主 README](../README.md)
- [AGENTS.md](../AGENTS.md) - AI 行为规则
- [技能包源文件](../skills/)

---

**注意**: 本目录的软链接是自动生成的，请勿手动编辑链接。如需修改技能包，请编辑 `skills/` 目录下的源文件。
