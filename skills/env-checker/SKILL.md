---
name: env-checker
description: "Python 运行环境全自动检测与初始化。检测系统是否安装 Python 3.12，未安装则自动下载安装；创建虚拟环境并一次性安装所有 Skill 的依赖库；最后自动验证环境可用性。支持 macOS 和 Windows，全程无需人工干预。当其他 Skill 需要执行 Python 脚本但环境不可用时，优先调用此 Skill。"
tags: [环境检测, Python, 初始化, 跨平台, venv, 自动化]
version: 2.0.0
author: Tax AI Team
created: 2026-02-26
---

# Python 环境全自动初始化

一键完成：检测 Python → 自动安装 → 创建虚拟环境 → 安装所有依赖 → 验证环境。全程自动化，零人工干预，执行完毕即可运行所有 Skill。

## 何时使用

- **首次使用**：用户安装客户端后首次运行任何 Python 类 Skill
- **环境缺失**：执行 Python 脚本时报 `python: command not found` 或 `ModuleNotFoundError`
- **环境初始化**：为某个 Skill 创建独立虚拟环境
- **前置检查**：任何 Python Skill 执行前的环境就绪保障
- **🆕 快速检查**：检查虚拟环境是否存在，无需创建（使用 check.sh/check.bat）

## 核心原则

1. **全自动** — 不弹确认、不要求手动下载、不需要人工操作任何步骤
2. **一次到位** — 统一安装所有 Skill 需要的依赖，后续 Skill 不再需要单独装包
3. **自动验证** — 安装完自动跑验证脚本，确认所有库可 import，通过才算成功
4. **幂等安全** — 重复执行不会破坏已有环境
5. **项目级隔离** — 每个目标目录有独立的 `.venv`

## 目录结构

```
env-checker/
├── SKILL.md              # 本文档
├── requirements.txt      # 统一依赖清单（汇总所有 Skill 的第三方库）
└── scripts/
    ├── check.sh          # 虚拟环境检查脚本（macOS/Linux）🆕
    ├── check.bat         # 虚拟环境检查脚本（Windows）🆕
    ├── check_venv.py     # 虚拟环境检查脚本（Python 跨平台）🆕
    ├── setup.sh          # macOS / Linux 一键脚本
    ├── setup.bat         # Windows 一键脚本
    └── verify.py         # 环境验证脚本
```

## 执行流程（5 步）

```
Step 1  检测 Python    →  搜索 PATH 和常见安装位置，找 Python 3.12
Step 2  安装 Python    →  未找到则自动下载安装（brew / pkg / exe）
Step 3  创建虚拟环境   →  在目标目录创建 .venv，升级 pip
Step 4  安装所有依赖   →  统一 requirements.txt + 项目级 requirements.txt
Step 5  自动验证       →  运行 verify.py 逐项检查 Python 版本和所有依赖库
```

## 使用方式

### 🆕 方式 1: 快速检查虚拟环境（推荐第一步）

在执行任何操作前，先检查虚拟环境是否存在：

**macOS / Linux:**
```bash
bash skills/env-checker/scripts/check.sh
```

**Windows:**
```cmd
skills\env-checker\scripts\check.bat
```

**输出格式:**
```
# 虚拟环境存在时（退出码 0）
VENV_EXISTS=true
VENV_PYTHON=/path/to/.venv/bin/python
VENV_DIR=/path/to/.venv
PROJECT_ROOT=/path/to/project
PYTHON_VERSION=Python 3.12.8

# 虚拟环境不存在时（退出码 1）
VENV_EXISTS=false
VENV_DIR=/path/to/.venv
PROJECT_ROOT=/path/to/project
SETUP_COMMAND=bash /path/to/skills/env-checker/scripts/setup.sh
```

**在脚本中使用:**
```bash
# 检查并获取虚拟环境路径
if eval "$(bash skills/env-checker/scripts/check.sh 2>&1)"; then
    # 虚拟环境存在，使用它
    echo "使用虚拟环境: $VENV_PYTHON"
    $VENV_PYTHON --version
else
    # 虚拟环境不存在，创建它
    echo "虚拟环境不存在，开始创建..."
    bash "$SETUP_COMMAND"
fi
```

---

### 方式 2: 创建虚拟环境（完整初始化）

### 你（大模型）必须按以下步骤操作：

#### 第一步：检测操作系统

```bash
uname -s 2>/dev/null || echo WINDOWS
```

- `Darwin` → macOS，用 `setup.sh`
- `Linux` → Linux，用 `setup.sh`
- `WINDOWS` 或报错 → Windows，用 `setup.bat`

#### 第二步：执行一键初始化

**macOS / Linux（推荐：不加 --project-dir，默认在项目根目录创建 .venv）：**

```bash
bash $CRS_SKILLS_ROOT/env-checker/scripts/setup.sh
```

**指定目录（可选）：**

```bash
bash $CRS_SKILLS_ROOT/env-checker/scripts/setup.sh \
    --project-dir /path/to/target-dir
```

**Windows：**

```cmd
$CRS_SKILLS_ROOT\env-checker\scripts\setup.bat
```

#### 第三步：用输出的路径执行后续脚本

脚本成功后输出：
```
ENV_PYTHON=/path/to/.venv/bin/python
ENV_VENV_DIR=/path/to/.venv
```

**后续所有 Python 脚本都用 `ENV_PYTHON` 的路径执行。**

### 参数说明

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--project-dir <path>` | 目标目录（venv 创建在此） | 当前工作目录 |
| `--requirements <path>` | 额外的 requirements.txt | 目标目录下的 requirements.txt |
| `--check-only` | 仅检测，不安装 | false |
| `--verbose` | 详细日志 | false |
| `--venv-name <name>` | 虚拟环境目录名 | `.venv` |

## 统一依赖清单

`requirements.txt` 汇总了所有 Skill 的第三方库，一次安装全部搞定：

| 用途 | 依赖库 |
|------|--------|
| LLM API | `openai`, `anthropic` |
| HTTP / 爬虫 | `requests`, `beautifulsoup4`, `lxml`, `urllib3` |
| 文档处理 | `python-docx` |
| 配置 / 解析 | `pyyaml`, `regex` |
| 数据处理 | `pandas` |
| 图像基础 | `pillow` |

## 验证脚本

`verify.py` 自动检查：
- Python 版本 ≥ 3.12
- 所有 11 个依赖库是否可 import
- 输出每个库的版本号和 PASS/FAIL 状态
- 全部通过才返回退出码 0

## Python 安装策略

### macOS（自动选择，优先级从高到低）

1. **Homebrew**：`brew install python@3.12`（无 sudo）
2. **官方 pkg**：从 python.org 下载 `.pkg`，`sudo installer` 静默安装
3. **国内镜像**：官方超时时切换 npmmirror

### Windows（自动选择）

1. **静默安装**：下载 `.exe`，`/quiet` 模式，自动加 PATH
2. **被动模式**：静默失败回退 `/passive`（仅显示进度条）
3. **国内镜像**：官方超时时切换 npmmirror
4. **下载工具**：优先 curl（Win10+），回退 PowerShell

## Python 下载地址

| 平台 | 下载地址 |
|------|---------|
| macOS (官方) | `https://www.python.org/ftp/python/3.12.8/python-3.12.8-macos11.pkg` |
| Windows x64 (官方) | `https://www.python.org/ftp/python/3.12.8/python-3.12.8-amd64.exe` |
| Windows ARM64 (官方) | `https://www.python.org/ftp/python/3.12.8/python-3.12.8-arm64.exe` |
| 国内镜像 (macOS) | `https://registry.npmmirror.com/-/binary/python/3.12.8/python-3.12.8-macos11.pkg` |
| 国内镜像 (Windows) | `https://registry.npmmirror.com/-/binary/python/3.12.8/python-3.12.8-amd64.exe` |

## 与其他 Skill 配合

完整使用流程示例（以 CRS Skills 为例）：

```bash
# CRS_SKILLS_ROOT = 项目根目录，例如 /Users/lifeng/git/git_taxai/crs-skills

# 1. 一键初始化环境（默认在项目根目录创建 .venv，只需执行一次）
bash $CRS_SKILLS_ROOT/env-checker/scripts/setup.sh

# 2. 使用根目录 .venv 执行任意技能包脚本
$CRS_SKILLS_ROOT/.venv/bin/python \
    $CRS_SKILLS_ROOT/crs-tax-calculator/scripts/client_manager.py list \
    --workspace $CRS_SKILLS_ROOT/workspaces
```

## 注意事项

1. **网络需求**：首次安装 Python 和依赖需要网络
2. **权限**：macOS pkg 安装需 sudo；Windows 可能需管理员
3. **验证保障**：只有 verify.py 全部 PASS，脚本才返回成功（退出码 0）
4. **版本策略**：优先精确匹配 3.12.x，若无则接受 ≥3.12
5. **幂等性**：已有可用虚拟环境和依赖时，跳过对应步骤
