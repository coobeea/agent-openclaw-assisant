# .cursor 目录说明

这是 Cursor IDE 的项目配置目录。

## 📂 目录结构

```
.cursor/
├── skills/              # 技能包目录（软链接）
│   ├── openclaw-manager → ../../skills/openclaw-manager
│   ├── openclaw-deploy  → ../../skills/openclaw-deploy
│   ├── openclaw-plugin  → ../../skills/openclaw-plugin
│   ├── openclaw-channel → ../../skills/openclaw-channel
│   ├── openclaw-model   → ../../skills/openclaw-model
│   └── openclaw-agent   → ../../skills/openclaw-agent
└── README.md            # 本文件
```

## 🎯 技能包激活机制

### 软链接方式

本项目使用**软链接**将 `skills/` 目录下的技能包激活到 Cursor 工作环境：

```bash
# 源文件位置（版本控制）
skills/openclaw-manager/

# Cursor 识别位置（软链接）
.cursor/skills/openclaw-manager/ → ../../skills/openclaw-manager/
```

### 优势

1. **统一管理**: 技能包源文件在 `skills/` 目录，便于版本控制
2. **Cursor 兼容**: `.cursor/skills/` 被 Cursor 自动识别
3. **实时生效**: 修改源文件后，Cursor 立即生效，无需同步
4. **多项目共享**: 可以将 `skills/` 中的技能包复制到其他项目

## 🔄 软链接维护

### 创建软链接

```bash
cd .cursor/skills
ln -s ../../skills/openclaw-manager openclaw-manager
```

### 验证软链接

```bash
ls -la .cursor/skills/
# 应该看到指向 ../../skills/ 的箭头
```

### 测试软链接

```bash
# 读取源文件
cat skills/openclaw-manager/SKILL.md

# 通过软链接读取（应该相同）
cat .cursor/skills/openclaw-manager/SKILL.md
```

## ⚠️ 注意事项

### Git 提交

`.cursor/` 目录**应该提交**到 Git，因为：
- 软链接本身很小（只有链接信息）
- 其他协作者克隆项目后可以直接使用
- 保持项目的完整性

### 跨平台兼容性

软链接在 Unix/Linux/macOS 上原生支持。

Windows 需要：
- Windows 10+ 开发者模式
- 或使用 Git Bash/WSL

## 🚀 使用方法

在 Cursor 中打开项目后，直接与 AI 对话：

```
"帮我安装 OpenClaw"
"创建一个生产实例"
"部署到 Docker"
```

Cursor AI 会自动识别并使用 `.cursor/skills/` 中的技能包。

## 📖 更多信息

- [技能包源文件](../skills/)
- [技能包索引](../docs/技能包索引.md)
- [快速开始](../docs/快速开始.md)

---

**目录作用**: Cursor 技能包激活  
**维护方式**: 通过软链接指向源文件  
**源文件位置**: `../../skills/`
