# verify.sh 删除说明

> 2026-03-12 删除根目录的 verify.sh 脚本

---

## 🎯 删除原因

### 1. **跨平台致命缺陷**

```bash
#!/bin/bash  # ❌ Windows 无法运行
```

verify.sh 是 bash 脚本，只能在 macOS/Linux 上运行，**完全无法在 Windows 上使用**。

**违反项目核心原则**:
- ❌ 项目要求所有功能跨平台支持
- ❌ env-checker 技能包提供了 .sh 和 .bat 双版本
- ❌ verify.sh 没有 Windows 版本，与项目设计理念相悖

---

### 2. **架构位置错误**

verify.sh 放在根目录，违反了"技能包自包含"原则：

```
❌ 错误的位置：
agent-openclaw-assisant/
├── verify.sh           # ❌ 业务逻辑不应在根目录
└── skills/
    └── env-checker/    # ✅ 环境验证应该在这里
```

**为什么错误**:
- ❌ 不是项目元文件（不像 README.md、.gitignore）
- ❌ 是业务逻辑，应该在技能包内
- ❌ 违反职责划分原则

---

### 3. **职责定位错误**

verify.sh 检查的内容：

| 检查项 | 实际意义 | 正确做法 |
|--------|---------|---------|
| 文件/目录是否存在 | ❌ Git 已保证 | 无需检查 |
| 脚本执行权限 | ❌ Git 会保留 | 无需检查 |
| 软链接是否正确 | ❌ 使用时动态检查 | 启动时检查 |
| 文档是否存在 | ❌ Git 已保证 | 无需检查 |

**99% 的检查都是无意义的静态检查！**

---

### 4. **没有检查真正重要的内容**

**应该验证但没验证的**:

| 真正需要验证的 | 负责的技能包 | 当前状态 |
|-------------|------------|---------|
| Python 是否安装 | env-checker | ✅ 已有 setup.sh |
| 虚拟环境是否存在 | env-checker | ✅ 已有 check.sh |
| 依赖是否安装 | env-checker | ✅ 已有 verify.py |
| 依赖版本是否正确 | env-checker | ✅ verify.py 检查 |
| OpenClaw 是否安装 | openclaw-manager | 使用时检查 |
| 实例是否可用 | openclaw-manager | ✅ 已有 health-check |

**verify.sh 做的都是 Git 保证的事情，没有检查真正重要的环境可用性！**

---

## ✅ 正确的验证方式

### 环境验证由 env-checker 负责

```bash
# 1. 检查虚拟环境（跨平台）
# macOS/Linux
bash skills/env-checker/scripts/check.sh

# Windows
skills\env-checker\scripts\check.bat

# 2. 如果不存在，创建它
bash skills/env-checker/scripts/setup.sh  # macOS/Linux
skills\env-checker\scripts\setup.bat      # Windows

# 3. 验证依赖库
.venv/bin/python skills/env-checker/scripts/verify.py  # macOS/Linux
.venv\Scripts\python skills\env-checker\scripts\verify.py  # Windows
```

---

## 📝 更新的文档

删除 verify.sh 后，更新了以下文档中的所有引用：

### 主要文档
1. ✅ `README.md` - 删除徽章和引用
2. ✅ `docs/README.md` - 更新链接
3. ✅ `docs/01-使用指南/FAQ.md` - 更新所有验证命令
4. ✅ `docs/01-使用指南/STATUS.md` - 更新验证状态说明
5. ✅ `docs/04-技术参考/项目结构.md` - 删除 verify.sh 条目
6. ✅ `docs/04-技术参考/STRUCTURE.md` - 更新所有引用
7. ✅ `docs/03-规范约定/技能包职责划分.md` - 添加错误示例

### 历史文档
- 保留历史归档文档中的引用（作为历史记录）

---

## 🎓 学到的教训

### 1. 跨平台是强制要求

任何脚本都必须同时支持：
- ✅ macOS/Linux（.sh）
- ✅ Windows（.bat）
- ✅ 或使用 Python 跨平台脚本

**不允许只支持单一平台的脚本！**

---

### 2. 业务逻辑属于技能包

```
✅ 正确：
skills/env-checker/scripts/
├── check.sh           # 检查虚拟环境
├── check.bat          # Windows 版本
├── setup.sh           # 创建虚拟环境
├── setup.bat          # Windows 版本
└── verify.py          # 验证依赖（跨平台）

❌ 错误：
agent-openclaw-assisant/
├── verify.sh          # 业务逻辑不应在根目录
└── check_venv.sh      # 业务逻辑不应在根目录
```

---

### 3. 静态检查毫无意义

**❌ 无意义的检查**:
- 文件是否存在（Git 已保证）
- 目录是否存在（Git 已保证）
- 文档是否存在（Git 已保证）

**✅ 有意义的检查**:
- Python 是否安装
- 虚拟环境是否可用
- 依赖库是否安装
- 版本是否符合要求

---

### 4. 职责归属要清晰

| 职责 | 归属技能包 | 不应该放在 |
|------|-----------|-----------|
| 环境检查 | env-checker | ❌ 根目录 |
| 实例管理 | openclaw-manager | ❌ 根目录 |
| 渠道配置 | openclaw-channel | ❌ 根目录 |
| 模型配置 | openclaw-model | ❌ 根目录 |

**每个功能都有明确的归属，不要在根目录创建业务脚本！**

---

## 🎯 核心原则总结

1. **跨平台强制** - 所有功能必须支持 Windows/macOS/Linux
2. **职责归属清晰** - 业务逻辑在技能包内，根目录只放元文件
3. **动态检查优先** - 使用时检查环境可用性，而非静态文件检查
4. **技能包自包含** - 每个技能包的功能和工具都在自己目录内

---

## 📚 相关文档

- [技能包职责划分.md](../../03-规范约定/技能包职责划分.md) - 职责边界规范
- [env-checker/SKILL.md](../../../skills/env-checker/SKILL.md) - 环境验证技能包
- [虚拟环境管理规范.md](../../03-规范约定/虚拟环境管理规范.md) - 虚拟环境规范

---

**核心结论**: verify.sh 的删除不是损失，而是架构的优化！环境验证本来就应该由 env-checker 技能包负责。
