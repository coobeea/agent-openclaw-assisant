---
name: openclaw-manager
description: >-
  Manage OpenClaw instances lifecycle including installation, creation, starting,
  stopping, and monitoring. Use when installing OpenClaw, creating new instances,
  managing instance lifecycle, or checking instance status.
---

# OpenClaw Manager

OpenClaw 实例管理技能包，提供 OpenClaw 的安装、实例创建和生命周期管理能力。

## 快速开始

### 安装 OpenClaw

```
用户: 帮我安装 OpenClaw
```

AI 会自动检测系统环境并安装 OpenClaw 的最新版本。

### 创建实例

```
用户: 创建一个生产实例 openclaw-prod-01
```

AI 会创建实例并初始化工作空间。

### 管理实例

```
用户: 启动/停止/重启 openclaw-prod-01
用户: 查看所有实例的状态
用户: 查看 openclaw-prod-01 的日志
```

---

## 核心功能

### 1. 安装 OpenClaw

**命令**: `install`

使用安装脚本自动安装 OpenClaw：

```bash
bash scripts/install_openclaw.sh [version]
```

**说明**:
- 自动检测系统环境（npm/yarn/pnpm）
- 优先使用官方打包版本
- 支持指定版本号或使用最新版
- 详见 [reference/installation.md](reference/installation.md)

### 2. 创建实例

**命令**: `create`

使用实例管理工具创建新实例：

```bash
python scripts/instance_manager.py create <instance-id>
```

**说明**:
- 验证实例 ID 格式（openclaw-{name}）
- 创建工作空间目录（从配置读取路径）
- 调用 OpenClaw 初始化
- 生成实例配置
- 详见 [reference/instance-management.md](reference/instance-management.md)

### 3. 启动/停止实例

**命令**: `start`, `stop`, `restart`

```bash
python scripts/instance_manager.py start <instance-id>
python scripts/instance_manager.py stop <instance-id>
python scripts/instance_manager.py restart <instance-id>
```

### 4. 查看实例状态

**命令**: `status`, `list`

```bash
# 查看单个实例
python scripts/instance_manager.py status <instance-id>

# 列出所有实例
python scripts/instance_manager.py list
```

### 5. 查看日志

**命令**: `logs`

```bash
python scripts/instance_manager.py logs <instance-id> [--follow] [--lines 100]
```

### 6. 删除实例

**命令**: `delete`

```bash
python scripts/instance_manager.py delete <instance-id>
```

**警告**: 删除操作会清除所有数据，请先备份！

---

## 工作空间管理

### 重要原则 ⚠️

1. **路径可配置**: 工作空间路径通过 `shared/configs/global.yaml` 配置
2. **结构不预定义**: 我们只创建实例顶层目录，内部结构由 OpenClaw 管理
3. **通过命令操作**: 使用 OpenClaw 命令行工具，不直接操作文件

### 工作空间路径配置

```yaml
# shared/configs/global.yaml
global:
  workspace_root: "./workspace"    # 相对路径
  # 或 "/data/openclaw"            # 绝对路径
```

详见 [reference/workspace-management.md](reference/workspace-management.md)

---

## 实例命名规范

**格式**: `openclaw-{environment}-{number}` 或 `openclaw-{name}`

**示例**:
- `openclaw-prod-01` - 生产环境实例1
- `openclaw-dev-01` - 开发环境实例1
- `openclaw-test-01` - 测试环境实例1
- `openclaw-demo` - 演示实例

**规则**:
- 必须以 `openclaw-` 开头
- 使用英文标识
- 小写字母、数字、连字符

---

## 使用示例

### 完整工作流

```
1. 用户: 安装 OpenClaw
   → AI 调用 install_openclaw.sh
   → 返回：✅ OpenClaw v2026.3.8 安装成功

2. 用户: 创建实例 openclaw-prod-01
   → AI 调用 instance_manager.py create
   → 创建工作空间目录
   → 调用 OpenClaw 初始化
   → 返回：✅ 实例创建成功

3. 用户: 启动 openclaw-prod-01
   → AI 调用 instance_manager.py start
   → 返回：✅ 实例已启动，运行在端口 3000

4. 用户: 查看状态
   → AI 调用 instance_manager.py list
   → 返回：
     • openclaw-prod-01 [运行中] 端口:3000 运行时间:2小时
```

---

## 错误处理

### 常见错误

**实例已存在**:
```
错误: 实例 openclaw-prod-01 已存在
建议: 使用不同的名称，或删除现有实例
```

**端口被占用**:
```
错误: 端口 3000 已被占用
建议: 停止占用端口的进程，或使用其他端口
```

**OpenClaw 未安装**:
```
错误: OpenClaw 未安装
建议: 运行 'bash scripts/install_openclaw.sh'
```

---

## 工具脚本

### install_openclaw.sh

安装 OpenClaw 到系统。

**用法**:
```bash
bash scripts/install_openclaw.sh          # 安装最新版
bash scripts/install_openclaw.sh 2026.3.8  # 安装指定版本
```

### instance_manager.py

实例管理主程序。

**用法**:
```bash
python scripts/instance_manager.py <command> [options]

命令:
  create <id>       创建实例
  start <id>        启动实例
  stop <id>         停止实例
  restart <id>      重启实例
  delete <id>       删除实例
  status <id>       查看实例状态
  list              列出所有实例
  logs <id>         查看实例日志

选项:
  --workspace-root  指定工作空间路径（覆盖配置）
  --follow          持续跟踪日志（仅用于 logs）
  --lines N         显示最后 N 行日志（仅用于 logs）
```

### workspace_init.sh

工作空间初始化脚本（内部使用）。

---

## 配置模板

### instance.config.yaml

实例配置模板（如果 OpenClaw 需要）。

### env.template

环境变量模板。

```bash
# 复制模板
cp templates/env.template workspace/openclaw-prod-01/.env

# 编辑配置
# 填入实际的值
```

---

## 依赖要求

### Python 依赖

详见 `scripts/requirements.txt`:
- pyyaml
- python-dotenv
- click
- rich
- psutil

### 系统要求

- Node.js 18+ 或 OpenClaw 支持的运行时
- Python 3.8+
- Bash 4.0+

---

## 技术调研

在使用本技能包前，建议先进行技术调研了解：
- OpenClaw 的实际安装方式
- OpenClaw 的命令行工具
- OpenClaw 的配置方式
- OpenClaw 的工作空间结构

参考文档：
- [OpenClaw GitHub](https://github.com/openclaw/openclaw)
- [技术调研文档](../../docs/技术调研.md)（待创建）

---

## 相关文档

- [安装指南](reference/installation.md) - 详细的安装说明
- [实例管理](reference/instance-management.md) - 实例管理详细文档
- [工作空间管理](reference/workspace-management.md) - 工作空间管理原则
- [工作空间设计说明](../../docs/工作空间管理.md) - 项目级工作空间管理文档
