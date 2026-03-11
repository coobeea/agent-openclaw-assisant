# env-checker 使用示例

> **从零到一：全自动Python环境初始化实战**

---

## 🎯 适用场景

- ✅ 新机器首次使用
- ✅ 系统没有Python
- ✅ 需要创建虚拟环境
- ✅ 需要安装所有技能包依赖

---

## 📋 场景 1: 系统已有 Python 3.12+

### 执行命令

```bash
cd /Users/lifeng/git/git-claw/agent-openclaw-assisant
bash skills/env-checker/scripts/setup.sh
```

### 预期输出

```
[STEP] ===== 环境全自动初始化 (Python 3.12) =====

[INFO] 操作系统: macos (arm64)
[STEP] 1/5 检测 Python 环境...
[INFO] 找到 Python: python3.12 (版本 3.12.12)

[STEP] 3/5 配置虚拟环境...
[INFO] 创建虚拟环境: /Users/lifeng/git/git-claw/agent-openclaw-assisant/.venv
[INFO] 升级 pip...

[STEP] 4/5 安装依赖...
[INFO] 安装统一依赖(所有Skill): skills/env-checker/requirements.txt
[INFO] 所有依赖安装完成

[STEP] 5/5 验证环境...

==================================================
  环境验证报告
==================================================

  Python 版本:   3.12.12  (需要 >=3.12)  [PASS]
  Python 路径:   /Users/lifeng/git/git-claw/agent-openclaw-assisant/.venv/bin/python
  操作系统:      Darwin arm64

  依赖库检查:
  ------------------------------------------------
    click               8.1.7           [PASS]
    rich                13.7.0          [PASS]
    psutil              5.9.6           [PASS]
    pyyaml              6.0.1           [PASS]
    python-dotenv       1.0.0           [PASS]
    cryptography        41.0.7          [PASS]
    requests            2.31.0          [PASS]
    httpx               0.25.2          [PASS]
    openai              1.0.0           [PASS]
    anthropic           0.18.0          [PASS]
    python-docx         0.8.11          [PASS]
    pdfplumber          0.10.0          [PASS]
    openpyxl            3.1.0           [PASS]
    colorlog            6.8.0           [PASS]

  ------------------------------------------------
  结果: 全部通过 (14/14 库)

==================================================
  环境就绪，可以运行所有 Skill
==================================================

==============================================
  环境就绪
==============================================

  Python:     /Users/lifeng/git/git-claw/agent-openclaw-assisant/.venv/bin/python
  虚拟环境:   /Users/lifeng/git/git-claw/agent-openclaw-assisant/.venv

==============================================

ENV_PYTHON=/Users/lifeng/git/git-claw/agent-openclaw-assisant/.venv/bin/python
ENV_VENV_DIR=/Users/lifeng/git/git-claw/agent-openclaw-assisant/.venv
```

### 耗时

约 **30-60 秒**（取决于网络速度）

---

## 📋 场景 2: 系统没有 Python 🌟

### 执行命令

```bash
cd /Users/lifeng/git/git-claw/agent-openclaw-assisant
bash skills/env-checker/scripts/setup.sh
```

### 预期输出

```
[STEP] ===== 环境全自动初始化 (Python 3.12) =====

[INFO] 操作系统: macos (arm64)
[STEP] 1/5 检测 Python 环境...
[WARN] 未找到 Python 3.12 或兼容版本

[STEP] 2/5 自动安装 Python 3.12.8...

[INFO] 检测到 Homebrew，尝试通过 brew 安装...
[INFO] Homebrew 安装成功

[INFO] Python 安装成功: /opt/homebrew/bin/python3.12 (版本 3.12.8)

[STEP] 3/5 配置虚拟环境...
[INFO] 创建虚拟环境: /Users/lifeng/git/git-claw/agent-openclaw-assisant/.venv
[INFO] 升级 pip...

[STEP] 4/5 安装依赖...
[INFO] 安装统一依赖(所有Skill): skills/env-checker/requirements.txt
[INFO] 所有依赖安装完成

[STEP] 5/5 验证环境...
[验证报告...]

==============================================
  环境就绪
==============================================

ENV_PYTHON=/Users/lifeng/git/git-claw/agent-openclaw-assisant/.venv/bin/python
ENV_VENV_DIR=/Users/lifeng/git/git-claw/agent-openclaw-assisant/.venv
```

### 耗时

约 **2-5 分钟**（包含Python下载和安装）

---

## 📋 场景 3: 虚拟环境已存在

### 执行命令

```bash
cd /Users/lifeng/git/git-claw/agent-openclaw-assisant
bash skills/env-checker/scripts/setup.sh
```

### 预期输出

```
[STEP] ===== 环境全自动初始化 (Python 3.12) =====

[INFO] 操作系统: macos (arm64)
[STEP] 1/5 检测 Python 环境...
[INFO] 找到 Python: python3.12 (版本 3.12.12)

[STEP] 3/5 配置虚拟环境...
[INFO] 虚拟环境已存在且版本匹配 (Python 3.12.12): /Users/lifeng/git/git-claw/agent-openclaw-assisant/.venv

[STEP] 4/5 安装依赖...
[INFO] 安装统一依赖(所有Skill): skills/env-checker/requirements.txt
[INFO] 所有依赖安装完成

[STEP] 5/5 验证环境...
[验证报告...]

==============================================
  环境就绪
==============================================
```

### 耗时

约 **10-20 秒**（仅验证和更新依赖）

---

## 📋 场景 4: Windows 系统

### 执行命令

```cmd
cd C:\path\to\agent-openclaw-assisant
skills\env-checker\scripts\setup.bat
```

### 预期输出

```
[STEP] ===== 环境全自动初始化 (Python 3.12) =====

[INFO] 操作系统: Windows
[STEP] 1/5 检测 Python 环境...
[INFO] 找到 Python: python (版本 3.12.8)

[STEP] 3/5 配置虚拟环境...
[INFO] 创建虚拟环境: C:\path\to\agent-openclaw-assisant\.venv

[STEP] 4/5 安装依赖...
[INFO] 安装统一依赖(所有Skill): skills\env-checker\requirements.txt
[INFO] 所有依赖安装完成

[STEP] 5/5 验证环境...
[验证报告...]

==============================================
  环境就绪
==============================================

  Python:     C:\path\to\agent-openclaw-assisant\.venv\Scripts\python.exe
  虚拟环境:   C:\path\to\agent-openclaw-assisant\.venv

==============================================

ENV_PYTHON=C:\path\to\agent-openclaw-assisant\.venv\Scripts\python.exe
ENV_VENV_DIR=C:\path\to\agent-openclaw-assisant\.venv
```

### 使用虚拟环境

```cmd
# 直接使用
.venv\Scripts\python.exe skills\openclaw-manager\scripts\instance_manager.py list

# 或激活后使用
.venv\Scripts\activate
python skills\openclaw-manager\scripts\instance_manager.py list
```

---

## 📋 场景 5: 仅检查环境，不安装

### 执行命令

```bash
bash skills/env-checker/scripts/setup.sh --check-only
```

### 预期输出

```
[STEP] ===== 环境全自动初始化 (Python 3.12) =====

[INFO] 操作系统: macos (arm64)
[STEP] 1/5 检测 Python 环境...
[INFO] 找到 Python: python3.12 (版本 3.12.12)

==============================================
  环境检测报告
==============================================

  操作系统:     macos (arm64)
  Python 路径:  python3.12
  Python 版本:  3.12.12
  目标版本:     3.12.x
  版本状态:     完全匹配

==============================================
```

### 用途

- ✅ 快速检查Python版本
- ✅ 不创建虚拟环境
- ✅ 不安装依赖
- ✅ 验证环境是否满足要求

---

## 📋 场景 6: 指定自定义目录

### 执行命令

```bash
# 在自定义目录创建虚拟环境
bash skills/env-checker/scripts/setup.sh --project-dir /custom/path
```

### 效果

虚拟环境将创建在 `/custom/path/.venv/` 而不是项目根目录。

**使用场景**: 多项目共享虚拟环境（不推荐）

---

## 📋 场景 7: AI 助手自动使用

### 用户输入

```
用户: "创建一个飞书实例"
```

### AI 执行流程

```
1. 🔍 检查虚拟环境
   执行: ls -la .venv/bin/python
   
2. 如果不存在 → 引导创建
   输出: "您还没有创建虚拟环境，我先帮您初始化环境..."
   执行: bash skills/env-checker/scripts/setup.sh
   
3. 使用虚拟环境Python
   执行: /path/to/.venv/bin/python skills/openclaw-manager/scripts/instance_manager.py list
   
4. 继续后续操作...
```

---

## 💡 实用技巧

### 技巧 1: 设置环境变量

```bash
# 添加到 ~/.bashrc 或 ~/.zshrc
export OPENCLAW_ROOT="/Users/lifeng/git/git-claw/agent-openclaw-assisant"
export OPENCLAW_PYTHON="$OPENCLAW_ROOT/.venv/bin/python"

# 使用
$OPENCLAW_PYTHON skills/openclaw-manager/scripts/instance_manager.py list
```

---

### 技巧 2: 创建全局别名

```bash
# 添加到 ~/.bashrc 或 ~/.zshrc
alias openclaw='/Users/lifeng/git/git-claw/agent-openclaw-assisant/.venv/bin/python'

# 使用
openclaw skills/openclaw-manager/scripts/instance_manager.py list
```

---

### 技巧 3: 快速重建环境

```bash
# 删除并重建
rm -rf .venv/ && bash skills/env-checker/scripts/setup.sh
```

---

### 技巧 4: 验证单个依赖

```bash
# 验证特定包是否安装
.venv/bin/python -c "import click; print(click.__version__)"
```

---

## ❓ 常见问题

### Q1: env-checker 会修改系统 Python 吗？

**不会！** env-checker 只会：
- ✅ 在项目目录创建 `.venv/`
- ✅ 在系统上安装Python（如果没有）
- ❌ 不修改系统Python配置
- ❌ 不影响其他项目

---

### Q2: 可以在多个项目使用 env-checker 吗？

**可以！** 每个项目都会有独立的 `.venv/`，互不干扰。

---

### Q3: env-checker 安装的Python在哪里？

**macOS**:
- Homebrew: `/opt/homebrew/bin/python3.12`
- PKG: `/Library/Frameworks/Python.framework/Versions/3.12/bin/python3.12`

**Windows**:
- `%LOCALAPPDATA%\Programs\Python\Python312\python.exe`

---

### Q4: 虚拟环境占用多少空间？

约 **150-200 MB**（包含Python和所有依赖）

---

### Q5: 删除虚拟环境会影响系统吗？

**不会！** 虚拟环境完全独立，删除后不影响系统：

```bash
rm -rf .venv/  # 安全删除
```

---

## 📊 性能数据

| 场景 | 耗时 | 说明 |
|------|------|------|
| 系统已有Python | 30-60秒 | 仅创建环境+安装依赖 |
| 系统没有Python (Homebrew) | 2-3分钟 | 包含Python安装 |
| 系统没有Python (PKG) | 3-5分钟 | 包含下载+安装 |
| 虚拟环境已存在 | 10-20秒 | 仅验证+更新依赖 |

---

## 🎯 下一步

### 创建虚拟环境后

```bash
# 1. 记住 ENV_PYTHON 路径
ENV_PYTHON="/path/to/.venv/bin/python"

# 2. 查看实例列表
$ENV_PYTHON skills/openclaw-manager/scripts/instance_manager.py list

# 3. 创建第一个实例
$ENV_PYTHON skills/openclaw-manager/scripts/instance_manager.py create openclaw-feishu-001
```

### 继续学习

- [新机器首次使用.md](./新机器首次使用.md) - 完整部署流程
- [工具链使用指南.md](./工具链使用指南.md) - 所有工具说明
- [env-checker/SKILL.md](../../skills/env-checker/SKILL.md) - env-checker 详细说明

---

**最后更新**: 2026-03-11  
**技能包**: env-checker v2.0.0  
**难度**: ⭐ 简单  
**预计阅读时间**: 3分钟
