# 虚拟环境管理 - env-checker 使用指南

> **问题**: 项目没有统一的虚拟环境管理，跨机器环境不一致  
> **解决方案**: 使用 env-checker 技能包进行全自动环境初始化  
> **优先级**: ⭐⭐⭐⭐⭐ 所有新机器必须先执行

**创建时间**: 2026-03-11  
**适用版本**: v1.0.0+

---

## 🎯 问题描述

### 现象

1. **跨机器环境不一致**
   - A 机器能运行，B 机器报错
   - 依赖版本不统一
   - 难以复现问题

2. **系统Python被污染**
   - 安装过多不必要的包
   - 影响其他项目
   - 难以清理

3. **新机器部署困难**
   - 不知道需要安装哪些依赖
   - 系统可能没有Python
   - 手动配置耗时

---

## ✅ 解决方案

### 使用 env-checker 技能包

**env-checker 是什么？**

一个全自动的Python环境检测和初始化工具，能够：
- ✅ 检测系统Python版本
- ✅ **自动下载和安装Python**（如果系统没有）🌟
- ✅ 创建项目虚拟环境（`.venv/`）
- ✅ 安装所有技能包依赖
- ✅ 自动验证环境可用性
- ✅ 跨平台支持（macOS/Linux/Windows）

---

## 🚀 使用方法

### 第 1 步：运行 env-checker

#### macOS / Linux:
```bash
cd /path/to/agent-openclaw-assisant
bash skills/env-checker/scripts/setup.sh
```

#### Windows:
```cmd
cd C:\path\to\agent-openclaw-assisant
skills\env-checker\scripts\setup.bat
```

---

### 第 2 步：等待自动初始化

**env-checker 自动完成**:

1. **检测Python** (Step 1/5)
   - 搜索系统Python 3.12+
   - 如果找到，直接使用
   - 如果没有，进入Step 2

2. **安装Python** (Step 2/5，如需要)
   - macOS: 优先 Homebrew，回退 pkg
   - Linux: apt/yum/dnf 自动选择
   - Windows: 下载 exe，静默安装

3. **创建虚拟环境** (Step 3/5)
   - 创建 `.venv/` 目录
   - 升级 pip

4. **安装依赖** (Step 4/5)
   - 安装统一依赖（15+个包）
   - 安装项目依赖（如有）

5. **验证环境** (Step 5/5)
   - 检查Python版本
   - 检查所有依赖库
   - 全部通过才算成功

---

### 第 3 步：记住 ENV_PYTHON 路径

**成功输出**:
```
==============================================
  环境就绪
==============================================

  Python:     /path/to/agent-openclaw-assisant/.venv/bin/python
  虚拟环境:   /path/to/agent-openclaw-assisant/.venv

==============================================

ENV_PYTHON=/path/to/agent-openclaw-assisant/.venv/bin/python
ENV_VENV_DIR=/path/to/agent-openclaw-assisant/.venv
```

**后续所有命令都用 `ENV_PYTHON` 路径！**

---

## 💡 核心优势

### 1. 自动安装 Python 🌟

**场景**: 新机器没有Python

**传统方式**:
```bash
# ❌ 手动下载Python安装包
# ❌ 手动安装
# ❌ 配置PATH
# ❌ 验证安装
```

**env-checker 方式**:
```bash
# ✅ 一条命令，全自动
bash skills/env-checker/scripts/setup.sh
```

---

### 2. 隐藏目录设计

**`.venv/` vs `venv/`**:

```
# 使用 .venv（隐藏目录）
$ ls
workspace  skills  docs  README.md

# 使用 venv（显眼目录）
$ ls
venv  workspace  skills  docs  README.md  ← 看起来混乱
```

**优点**:
- ✅ 保持项目根目录整洁
- ✅ `ls` 命令不显示
- ✅ 不影响项目外观

---

### 3. 统一依赖管理

**Before**（分散管理）:
```
skills/
├── openclaw-manager/scripts/requirements.txt
├── openclaw-model/scripts/requirements.txt
├── openclaw-channel/scripts/requirements.txt
└── ...

问题: 重复安装，版本冲突，难以管理
```

**After**（统一管理）:
```
skills/
└── env-checker/
    └── requirements.txt  ← 唯一真实来源

优势: 一次安装，全局可用，版本统一
```

---

### 4. 跨平台兼容

**macOS/Linux**: `setup.sh`  
**Windows**: `setup.bat`

**一套命令，全平台可用**

---

## 📐 使用规范

### ✅ 必须遵守

1. **项目初始化第一步：运行 env-checker**
   ```bash
   bash skills/env-checker/scripts/setup.sh
   ```

2. **所有Python脚本使用 `.venv/bin/python`**
   ```bash
   .venv/bin/python skills/openclaw-manager/scripts/instance_manager.py list
   ```

3. **新依赖添加到 env-checker/requirements.txt**
   ```bash
   echo "new-package>=1.0.0" >> skills/env-checker/requirements.txt
   .venv/bin/pip install -r skills/env-checker/requirements.txt
   ```

---

### ❌ 禁止行为

1. ❌ 使用系统Python运行脚本
   ```bash
   python3 skills/.../script.py  # 错误！
   ```

2. ❌ 在根目录创建 `venv/` 目录
   ```bash
   python3 -m venv venv  # 错误！应该用 .venv
   ```

3. ❌ 手动创建虚拟环境
   ```bash
   python3 -m venv .venv  # 错误！应该用 env-checker
   ```

4. ❌ 在各技能包的 requirements.txt 中添加依赖
   ```bash
   # 错误！应该添加到 env-checker/requirements.txt
   ```

---

## 🤖 AI 助手使用规范

### 标准流程

```python
# AI执行任何Python脚本前的流程：

1. 检查虚拟环境是否存在
   ls -la .venv/bin/python

2. 如果不存在，引导用户创建
   "您还没有创建虚拟环境，我先帮您初始化环境..."
   bash skills/env-checker/scripts/setup.sh

3. 使用虚拟环境Python执行命令
   /path/to/.venv/bin/python skills/.../script.py <args>
```

### 命令模板

```bash
# 获取项目根目录
PROJECT_ROOT="/Users/lifeng/git/git-claw/agent-openclaw-assisant"

# 构建虚拟环境Python路径
VENV_PYTHON="${PROJECT_ROOT}/.venv/bin/python"

# 执行命令
${VENV_PYTHON} skills/openclaw-manager/scripts/instance_manager.py list
```

---

## 🔍 故障排查

### 问题 1: 系统没有 Python

**现象**: `python: command not found`

**解决方案**:
```bash
# env-checker 会自动安装！
bash skills/env-checker/scripts/setup.sh

# 它会自动下载并安装 Python 3.12.8
```

---

### 问题 2: env-checker 执行失败

**现象**: setup.sh 报错

**解决方案**:
```bash
# 使用 --verbose 查看详细日志
bash skills/env-checker/scripts/setup.sh --verbose

# 检查网络连接（需要下载Python和依赖）
ping python.org

# 检查磁盘空间
df -h
```

---

### 问题 3: 依赖安装失败

**现象**: verify.py 报 FAIL

**解决方案**:
```bash
# 重新安装依赖
.venv/bin/pip install -r skills/env-checker/requirements.txt

# 运行验证
.venv/bin/python skills/env-checker/scripts/verify.py
```

---

### 问题 4: 虚拟环境已存在但版本不匹配

**现象**: env-checker 提示"虚拟环境存在但不可用"

**解决方案**:
```bash
# env-checker 会自动删除并重建
bash skills/env-checker/scripts/setup.sh

# 或手动删除后重建
rm -rf .venv/
bash skills/env-checker/scripts/setup.sh
```

---

## 📚 相关文档

- [env-checker/SKILL.md](../../skills/env-checker/SKILL.md) - 完整技能包说明
- [虚拟环境管理规范.md](../03-规范约定/虚拟环境管理规范.md) - 详细规范
- [虚拟环境-快速上手.md](../01-使用指南/虚拟环境-快速上手.md) - 快速指南
- [新机器首次使用.md](../01-使用指南/新机器首次使用.md) - 完整部署流程

---

## 🎯 关键经验

### 经验 1: 优先使用现有工具

**教训**: 在创建新工具前，先检查项目是否已有类似工具

**应用**: 
- 发现 env-checker 已存在
- 扩充 env-checker 而非创建新工具
- 节省时间和维护成本

---

### 经验 2: 隐藏目录更整洁

**教训**: 虚拟环境目录应该不影响项目外观

**应用**:
- 使用 `.venv/` 而不是 `venv/`
- `ls` 命令不显示
- 项目根目录保持整洁

---

### 经验 3: 自动化是关键

**教训**: 用户最怕手动配置环境

**应用**:
- env-checker 自动检测Python
- 自动下载安装Python
- 自动创建虚拟环境
- 自动安装依赖
- 自动验证环境

---

### 经验 4: 统一管理更可靠

**教训**: 分散的依赖文件容易出问题

**应用**:
- env-checker/requirements.txt 作为唯一依赖来源
- 一次安装所有依赖
- 版本统一，不冲突

---

## 💡 最佳实践

### 用户最佳实践

```bash
# 1. 项目初始化（第一步）
bash skills/env-checker/scripts/setup.sh

# 2. 记住 ENV_PYTHON 路径
# /path/to/agent-openclaw-assisant/.venv/bin/python

# 3. 所有命令使用虚拟环境Python
.venv/bin/python skills/.../script.py
```

---

### AI 助手最佳实践

```python
# 伪代码
def execute_python_script(script_path, args):
    # 1. 检查虚拟环境
    if not exists(".venv/bin/python"):
        guide_user_to_run("bash skills/env-checker/scripts/setup.sh")
        return
    
    # 2. 使用虚拟环境Python
    cmd = f"{PROJECT_ROOT}/.venv/bin/python {script_path} {args}"
    execute(cmd)
```

---

## 🎉 总结

### 核心成果

1. ✅ 利用了现有的 env-checker 技能包
2. ✅ 实现了Python自动安装能力 🌟
3. ✅ 使用隐藏目录保持项目整洁
4. ✅ 统一了依赖管理
5. ✅ 更新了所有文档和AI配置

---

### 关键价值

| 特性 | env-checker 方案 | 优势 |
|------|----------------|------|
| 自动安装Python | ✅ 支持 | 🌟 系统没Python也能用 |
| 虚拟环境目录 | `.venv/`（隐藏） | ✨ 不影响项目外观 |
| 跨平台支持 | ✅ 完整 | 👍 全平台一致 |
| 自动验证 | ✅ 完整 | 🛡️ 保证可用 |
| 依赖管理 | ✅ 统一 | 📦 易于维护 |

---

### 用户收益

1. **环境问题零烦恼** - env-checker 全自动处理
2. **新机器快速部署** - 1条命令完成
3. **跨机器环境一致** - 统一依赖管理
4. **项目目录整洁** - 隐藏的虚拟环境

---

### AI 助手收益

1. **行为规范清晰** - 明确使用 `.venv/bin/python`
2. **流程标准化** - 先检查环境，再执行
3. **可靠性提升** - env-checker 保证环境可用
4. **错误减少** - 不再有环境问题

---

**最后更新**: 2026-03-11  
**解决方案提供者**: env-checker 技能包  
**文档维护**: AI Assistant
