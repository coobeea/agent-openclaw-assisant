# 🚀 跨机器部署指南

> **核心原则**: 拿到项目就能跑，不依赖特定路径

**更新时间**: 2026-03-10  
**适用平台**: macOS, Linux, Windows

---

## 🎯 部署目标

✅ **零硬编码路径** - 所有路径都可配置  
✅ **跨平台支持** - macOS/Linux/Windows 都能用  
✅ **一拿就能用** - 按流程 3 分钟跑通  
✅ **灵活部署** - 可以部署到任意目录

---

## 📋 部署前置条件

### 必需环境

1. **Python 3.8+**
   ```bash
   python3 --version  # 应该 >= 3.8
   ```

2. **Node.js 22+**（运行 OpenClaw）
   ```bash
   node --version  # 应该 >= 22
   ```

3. **Git**（克隆项目）
   ```bash
   git --version
   ```

### OpenClaw 安装（二选一）

**选项 A: 全局安装（推荐）**
```bash
npm install -g openclaw@latest
```

**选项 B: 从源码构建**
```bash
git clone https://github.com/openclaw/openclaw.git
cd openclaw
pnpm install
pnpm build
```

---

## 🚀 快速部署（3 步）

### 第 1 步：克隆项目

```bash
# 克隆到任意目录（示例）
cd ~/projects  # 或任意你喜欢的目录
git clone <项目地址> agent-openclaw-assisant
cd agent-openclaw-assisant
```

### 第 2 步：验证环境

```bash
# 测试统一配置系统
python3 shared/configs/path_manager.py
```

**期望输出**:
```
✅ 统一配置信息
✅ OpenClaw CLI: 自动检测到...
✅ 工作空间根目录: .../test-workspace
```

### 第 3 步：创建龙虾（一步到位）

```bash
# 使用自动化编排器
python3 scripts/orchestrator.py 创建一个龙虾

# 🎉 4秒完成！自动创建、配置、启动
```

---

## 🔧 配置说明

### 配置系统架构

```
优先级（从高到低）:
1. 环境变量（临时覆盖）
2. global.yaml（持久配置）
3. 自动检测
4. 默认值
```

### 配置文件位置

**唯一配置文件**: `shared/configs/global.yaml`

```yaml
global:
  # 项目名称
  project_name: "openclaw-fleet"
  
  # 工作空间根目录
  # 支持相对路径（相对于项目根）或绝对路径
  workspace_root: "./test-workspace"
```

### 环境变量覆盖

**临时配置**（当前会话）:
```bash
# OpenClaw CLI 路径
export OPENCLAW_CLI_PATH=/custom/path/openclaw/dist/index.js

# 工作空间路径
export OPENCLAW_ASSISTANT_WORKSPACE=/data/openclaw-workspace

# 是否使用 Node 前缀
export OPENCLAW_USE_NODE=true
```

**持久配置**（当前终端）:
```bash
# 添加到 ~/.zshrc 或 ~/.bashrc
echo 'export OPENCLAW_CLI_PATH=/path/to/openclaw' >> ~/.zshrc
source ~/.zshrc
```

### 自动检测机制

如果未配置，系统会自动按顺序检测：

1. ✅ 全局命令 `openclaw`
2. ✅ `../openclaw/dist/index.js`（项目相邻目录）
3. ✅ `~/git/git_agents/openclaw/dist/index.js`
4. ✅ `~/openclaw/dist/index.js`

**95%的情况下无需任何配置** ✨

---

## 📂 目录结构说明

### 项目目录

```
agent-openclaw-assisant/
├── shared/configs/          # 配置管理
│   ├── global.yaml         # 唯一配置文件
│   └── path_manager.py     # 统一路径管理器
├── scripts/                # 工具脚本
│   └── orchestrator.py     # 自动化编排器
├── skills/                 # 技能包
├── test-workspace/         # 测试工作空间（默认）
└── workspace/              # 生产工作空间（可选）
```

### 工作空间结构

工作空间由 OpenClaw 自动创建和管理：

```
{workspace_root}/
├── lobsters/               # 所有实例
│   ├── openclaw-test-01/   # 实例工作空间
│   │   ├── .openclaw/      # OpenClaw 自动创建
│   │   │   └── openclaw.json
│   │   └── ...             # OpenClaw 管理的其他文件
│   └── ...
├── data/                   # 共享数据
│   ├── agents.jsonl        # 实例记录
│   ├── models.json         # 模型配置
│   └── channels.jsonl      # 渠道配置
└── logs/                   # 日志
    └── openclaw-test-01.log
```

---

## 🌍 跨平台部署

### macOS

```bash
# 1. 克隆项目
cd ~/projects
git clone <repo> agent-openclaw-assisant
cd agent-openclaw-assisant

# 2. 创建龙虾（自动化）
python3 scripts/orchestrator.py 创建一个龙虾

# 🎉 完成！
```

### Linux

```bash
# 1. 克隆项目
cd ~/projects
git clone <repo> agent-openclaw-assisant
cd agent-openclaw-assisant

# 2. 创建龙虾（自动化）
python3 scripts/orchestrator.py 创建一个龙虾

# 🎉 完成！
```

### Windows

```powershell
# 1. 克隆项目
cd C:\Projects
git clone <repo> agent-openclaw-assisant
cd agent-openclaw-assisant

# 2. 创建龙虾（自动化）
python scripts/orchestrator.py 创建一个龙虾

# 🎉 完成！
```

---

## ✅ 部署验证

### 检查清单

- [ ] Python 3.8+ 已安装
- [ ] Node.js 22+ 已安装
- [ ] OpenClaw 已安装（全局或源码）
- [ ] 项目已克隆
- [ ] 配置系统正常（运行 `python3 shared/configs/path_manager.py`）
- [ ] 能成功创建龙虾（运行 `python3 scripts/orchestrator.py 创建一个龙虾`）
- [ ] Web UI 可访问（http://127.0.0.1:端口号/）

### 故障排查

**问题 1: OpenClaw CLI 找不到**
```bash
# 检查是否安装
which openclaw

# 如果未安装，全局安装
npm install -g openclaw@latest

# 或设置源码路径
export OPENCLAW_CLI_PATH=/path/to/openclaw/dist/index.js
```

**问题 2: 权限错误**
```bash
# 确保工作空间目录可写
chmod -R 755 test-workspace
```

**问题 3: 端口冲突**
```bash
# 查看已占用端口
lsof -i :18800

# 使用其他端口
python3 skills/openclaw-manager/scripts/instance_manager.py create test-01 --port 19000
```

---

## 🎯 使用场景

### 场景 1: 开发测试（本地单机）

```bash
# 一键创建测试实例
python3 scripts/orchestrator.py 创建一个龙虾

# Web UI 访问
open http://127.0.0.1:18800/
```

### 场景 2: 生产部署（独立服务器）

```bash
# 1. 修改 global.yaml，使用生产工作空间
nano shared/configs/global.yaml
# workspace_root: "/data/openclaw-production"

# 2. 创建生产实例
python3 scripts/orchestrator.py 创建一个龙虾

# 3. 配置飞书渠道
python3 skills/openclaw-channel/scripts/channel_manager.py add \
  --name feishu-prod \
  --platform feishu \
  --app-id xxx \
  --app-secret yyy

# 4. 完成！
```

### 场景 3: 多机器部署（团队协作）

**机器 A（开发）**:
```bash
cd ~/dev
git clone <repo> agent-openclaw-assisant
cd agent-openclaw-assisant
# 使用默认 test-workspace
python3 scripts/orchestrator.py 创建一个龙虾
```

**机器 B（测试）**:
```bash
cd /opt/testing
git clone <repo> agent-openclaw-assisant
cd agent-openclaw-assisant
# 自定义工作空间
export OPENCLAW_ASSISTANT_WORKSPACE=/var/openclaw-test
python3 scripts/orchestrator.py 创建一个龙虾
```

**机器 C（生产）**:
```bash
cd /srv
git clone <repo> agent-openclaw-assisant
cd agent-openclaw-assisant
# 编辑 global.yaml
echo 'global:
  workspace_root: "/data/openclaw-prod"' > shared/configs/global.yaml
python3 scripts/orchestrator.py 创建一个龙虾
```

---

## 📖 更多信息

- **快速开始**: [快速入门.md](快速入门.md)
- **配置参考**: [shared/configs/README.md](shared/configs/README.md)
- **技能包索引**: [docs/技能包索引.md](docs/技能包索引.md)
- **FAQ**: [docs/FAQ.md](docs/FAQ.md)

---

**文档版本**: v2.0（统一配置系统）  
**更新时间**: 2026-03-10
