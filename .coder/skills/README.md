# Coder 技能包激活目录

本目录通过**软链接**的方式激活项目中的技能包。

## 📂 软链接说明

所有技能包的源文件位于 `../../skills/`，这里只是链接：

```
.coder/skills/
├── openclaw-manager  → ../../skills/openclaw-manager
├── openclaw-deploy   → ../../skills/openclaw-deploy
├── openclaw-plugin   → ../../skills/openclaw-plugin
├── openclaw-channel  → ../../skills/openclaw-channel
├── openclaw-model    → ../../skills/openclaw-model
└── openclaw-agent    → ../../skills/openclaw-agent
```

## 🎯 为什么使用软链接？

### 优势
1. **单一数据源**: 技能包源文件在 `skills/` 目录，统一管理
2. **Coder 识别**: `.coder/skills/` 目录会被 Coder 自动识别
3. **版本控制友好**: 只需提交 `skills/` 目录的源文件
4. **便于开发**: 修改源文件，Coder 立即生效

### 工作原理

```
开发/修改
    ↓
skills/openclaw-manager/SKILL.md  (源文件)
    ↓
    │ (软链接)
    ↓
.coder/skills/openclaw-manager/SKILL.md
    ↓
Coder AI 读取并使用
```

## 🔧 管理软链接

### 查看软链接

```bash
ls -la .coder/skills/
```

### 添加新技能包

```bash
cd .coder/skills
ln -s ../../skills/new-skill-name new-skill-name
```

### 删除软链接（不影响源文件）

```bash
rm .coder/skills/openclaw-manager
```

**注意**: 这只删除链接，源文件 `skills/openclaw-manager/` 不受影响。

### 重新创建所有链接

```bash
cd .coder/skills
rm -f openclaw-*

ln -s ../../skills/openclaw-manager openclaw-manager
ln -s ../../skills/openclaw-deploy openclaw-deploy
ln -s ../../skills/openclaw-plugin openclaw-plugin
ln -s ../../skills/openclaw-channel openclaw-channel
ln -s ../../skills/openclaw-model openclaw-model
ln -s ../../skills/openclaw-agent openclaw-agent
```

## 📋 技能包状态

所有 6 个技能包已激活：

- ✅ openclaw-manager（核心）
- ✅ openclaw-deploy（部署）
- ✅ openclaw-plugin（插件）
- ✅ openclaw-channel（渠道）
- ✅ openclaw-model（模型）
- ✅ openclaw-agent（智能体）

## 🎨 Coder 使用

Coder 会自动识别 `.coder/skills/` 目录下的所有技能包。

打开项目后，直接用自然语言交互：

```
"帮我安装 OpenClaw"
"创建一个实例"
"部署到 Docker"
```

Coder AI 会自动调用相应的技能包。

---

**重要**: 这个目录的内容是自动生成的软链接，不要手动编辑。  
**修改技能包**: 请编辑 `skills/` 目录下的源文件。
