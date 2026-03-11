# Python 版本要求

> **本项目对 Python 版本的详细说明**

**创建时间**: 2026-03-11  
**最后更新**: 2026-03-11

---

## 🎯 版本要求

### 正式规范

| 类型 | 版本 | 说明 |
|------|------|------|
| **最低版本** | Python 3.10 | 兼容性考虑，支持较旧系统 |
| **推荐版本** | Python 3.12+ | env-checker 默认安装版本 |
| **测试版本** | 3.12.8, 3.14.2 | 经过充分测试的版本 |
| **目标版本** | 3.12.8 | `.python-version` 中定义 |

---

### 版本策略

#### 1. 最低版本: Python 3.10

**原因**:
- ✅ 平衡新特性和兼容性
- ✅ 支持 `match-case` 语法
- ✅ 支持类型提示改进
- ✅ 大多数现代库的最低要求

**适用场景**:
- 用户已有 Python 3.10/3.11
- 不想升级系统Python
- 手动创建虚拟环境（不推荐）

---

#### 2. 推荐版本: Python 3.12+

**原因**:
- ✅ 性能提升（比3.10快约15%）
- ✅ 更好的错误提示
- ✅ 更多新特性
- ✅ env-checker 默认安装版本

**适用场景**:
- 使用 env-checker 自动安装（推荐）
- 新机器部署
- 追求最佳性能

---

#### 3. 目标版本: 3.12.8

**定义位置**: `.python-version` 文件

**用途**:
- pyenv 自动切换版本
- 开发环境版本统一
- CI/CD 版本参考

---

## 📁 版本定义文件

### 1. `.python-version`

**位置**: 项目根目录  
**内容**: `3.12.8`  
**用途**: pyenv 自动版本切换

```bash
# 安装指定版本（如果使用 pyenv）
pyenv install 3.12.8

# pyenv 会自动使用 .python-version 中的版本
cd /path/to/agent-openclaw-assisant
python --version  # 自动切换到 3.12.8
```

---

### 2. `pyproject.toml`

**位置**: 项目根目录  
**内容**: `requires-python = ">=3.10"`  
**用途**: 标准 Python 项目配置

**定义内容**:
```toml
[project]
requires-python = ">=3.10"

classifiers = [
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Programming Language :: Python :: 3.13",
    "Programming Language :: Python :: 3.14",
]
```

---

### 3. `requirements.txt`

**位置**: 项目根目录  
**内容**: 顶部注释说明

```txt
# Python 版本要求:
#   - 最低版本: Python 3.10
#   - 推荐版本: Python 3.12+
#   - 测试版本: Python 3.12.8, 3.14.2
```

---

### 4. `env-checker` 配置

**位置**: `skills/env-checker/scripts/`  
**内容**: `REQUIRED_MINOR=12` (Python 3.12+)  
**用途**: 自动安装Python时的版本选择

**文件**:
- `setup.sh`: `REQUIRED_VERSION="3.12"`, `PYTHON_FULL_VERSION="3.12.8"`
- `setup.bat`: `REQUIRED_VERSION="3.12"`, `PYTHON_FULL_VERSION="3.12.8"`
- `verify.py`: `MIN_PYTHON = (3, 12)`

---

## 🔧 env-checker 版本配置

### 当前配置

```bash
# skills/env-checker/scripts/setup.sh
REQUIRED_MAJOR=3
REQUIRED_MINOR=12
PYTHON_FULL_VERSION="3.12.8"
```

**行为**:
1. 优先查找 Python 3.12.x
2. 如果找到 3.13, 3.14 等更高版本，也可以使用
3. 如果没有找到任何 >=3.12 的版本，自动下载安装 3.12.8

---

### 版本检测逻辑

```bash
# 精确匹配: Python 3.12.x
version_eq_minor "$ver"  # 返回 true

# 兼容匹配: Python >= 3.12
version_ge "$ver"        # 返回 true
```

**示例**:
- Python 3.10.5 → ❌ 不满足，自动安装
- Python 3.11.2 → ❌ 不满足，自动安装
- Python 3.12.1 → ✅ 精确匹配
- Python 3.13.0 → ✅ 兼容匹配
- Python 3.14.2 → ✅ 兼容匹配（您当前版本）

---

## 🎯 推荐配置

### 方案对比

| 方案 | 最低版本 | env-checker | 优点 | 缺点 |
|------|---------|------------|------|------|
| **当前方案** | 3.10+ | 3.12+ | 兼容性好 | 版本不一致 |
| 方案B | 3.12+ | 3.12+ | 版本统一 | 不支持旧系统 |
| 方案C | 3.10+ | 3.10+ | 完全统一 | env-checker需改动 |

---

### 推荐: 保持当前方案

**理由**:
1. **兼容性优先** - Python 3.10+ 覆盖更多系统
2. **自动升级** - env-checker 自动安装 3.12.8（最佳版本）
3. **灵活性** - 允许用户使用现有Python（如果 >=3.10）

**版本策略**:
- `pyproject.toml`: `>=3.10` （最低门槛）
- `env-checker`: `>=3.12` （推荐/自动安装）
- `.python-version`: `3.12.8` （开发标准）

---

## 📐 使用建议

### 新机器部署

**推荐方式**（使用 env-checker）:
```bash
# env-checker 会自动安装 Python 3.12.8
bash skills/env-checker/scripts/setup.sh
```

**结果**: 
- ✅ 统一使用 Python 3.12.8
- ✅ 版本一致性最佳
- ✅ 性能最优

---

### 已有 Python 的机器

**场景 1: Python 3.12+**
```bash
# 直接使用，无需安装
bash skills/env-checker/scripts/setup.sh
# ✅ 使用现有 Python 3.12+
```

**场景 2: Python 3.10-3.11**
```bash
# 可以使用，但 env-checker 会建议升级
bash skills/env-checker/scripts/setup.sh
# ⚠️  会提示: "推荐使用 Python 3.12+"
```

**场景 3: Python < 3.10**
```bash
# env-checker 会自动安装 3.12.8
bash skills/env-checker/scripts/setup.sh
# ✅ 自动下载并安装 Python 3.12.8
```

---

## 🔍 版本检测

### 检查当前 Python 版本

```bash
# 系统 Python
python3 --version

# 虚拟环境 Python
.venv/bin/python --version

# 或使用 env-checker
bash skills/env-checker/scripts/setup.sh --check-only
```

---

### 检查兼容性

```bash
# 方式1: 使用 Python
python3 -c "import sys; print(f'Python {sys.version_info.major}.{sys.version_info.minor}')"

# 方式2: 使用 env-checker
bash skills/env-checker/scripts/setup.sh --check-only
```

---

## 📊 版本特性对比

| 特性 | 3.10 | 3.11 | 3.12 | 3.13+ |
|------|------|------|------|-------|
| match-case | ✅ | ✅ | ✅ | ✅ |
| 类型提示改进 | ✅ | ✅ | ✅ | ✅ |
| 性能提升 | - | +25% | +40% | +50% |
| 错误提示改进 | 基础 | 改进 | 优秀 | 最佳 |
| f-string 改进 | 基础 | 改进 | 完善 | 完善 |
| 异步改进 | 基础 | 改进 | 优秀 | 最佳 |

**结论**: Python 3.12+ 是最佳选择

---

## 🚨 常见问题

### Q1: 为什么 pyproject.toml 要求 >=3.10，而 env-checker 要求 >=3.12？

**答**: 这是有意的设计

- `pyproject.toml` (**最低门槛**): 兼容性考虑，允许用户使用现有 3.10/3.11
- `env-checker` (**推荐标准**): 自动安装时选择最佳版本 3.12.8

**好处**:
- ✅ 用户有 3.10/3.11 → 可以用
- ✅ 用户没Python → 自动安装 3.12.8
- ✅ 两全其美

---

### Q2: 我的系统是 Python 3.14，会有问题吗？

**不会！** Python 3.14 >= 3.12，完全兼容。

```bash
# env-checker 会检测到 3.14.2
[INFO] 找到 Python: python3 (版本 3.14.2)
[INFO] 版本状态: 兼容 (高于目标)  ✅
```

---

### Q3: 我想强制使用 Python 3.12，不想用 3.14？

**解决方案**:

```bash
# 方式1: 使用 pyenv 锁定版本
pyenv install 3.12.8
pyenv local 3.12.8  # 使用 .python-version

# 方式2: 创建虚拟环境时指定版本
python3.12 -m venv .venv
```

---

### Q4: 能否降低 env-checker 的版本要求到 3.10？

**可以，但不推荐**

如果必须降低，需要修改：
1. `skills/env-checker/scripts/setup.sh`: `REQUIRED_MINOR=10`
2. `skills/env-checker/scripts/setup.bat`: `REQUIRED_MINOR=10`
3. `skills/env-checker/scripts/verify.py`: `MIN_PYTHON = (3, 10)`

**后果**:
- ⚠️ 性能下降
- ⚠️ 缺少一些新特性
- ⚠️ 可能遇到兼容性问题

---

### Q5: 如何确保团队使用统一的Python版本？

**推荐方式**: 使用 env-checker

```bash
# 1. 所有成员运行 env-checker
bash skills/env-checker/scripts/setup.sh

# 2. env-checker 会自动:
#    - 检测系统Python
#    - 如果版本 < 3.12，自动安装 3.12.8
#    - 创建统一的虚拟环境

# 结果: 所有成员都使用 Python 3.12+
```

---

## 📚 相关文件

| 文件 | 作用 |
|------|------|
| `.python-version` | pyenv 版本锁定（3.12.8） |
| `pyproject.toml` | 项目元数据和最低版本要求（>=3.10） |
| `requirements.txt` | 依赖包列表和版本注释 |
| `skills/env-checker/scripts/setup.sh` | env-checker 配置（3.12+） |
| `skills/env-checker/scripts/setup.bat` | Windows 配置（3.12+） |
| `skills/env-checker/scripts/verify.py` | 版本验证（3.12+） |

---

## 🎯 总结

### 版本策略

```
最低兼容: Python 3.10  (pyproject.toml)
推荐使用: Python 3.12+ (env-checker)
开发标准: Python 3.12.8 (.python-version)
已测试:   Python 3.12.8, 3.14.2
```

### 核心原则

1. **兼容性优先** - 最低 3.10，支持更多系统
2. **性能优先** - 推荐 3.12+，env-checker 自动安装
3. **统一优先** - 使用 env-checker 确保团队版本一致
4. **自动化优先** - env-checker 自动处理版本问题

### 用户指引

- ✅ **新机器**: 使用 env-checker，自动安装 3.12.8
- ✅ **已有 3.12+**: 直接使用，无需改动
- ✅ **已有 3.10-3.11**: 可以用，但建议升级
- ✅ **低于 3.10**: env-checker 自动安装 3.12.8

---

**推荐阅读**:
- [env-checker/SKILL.md](../../skills/env-checker/SKILL.md) - env-checker 完整说明
- [虚拟环境管理规范.md](./虚拟环境管理规范.md) - 虚拟环境规范

---

**最后更新**: 2026-03-11  
**维护者**: lifeng
