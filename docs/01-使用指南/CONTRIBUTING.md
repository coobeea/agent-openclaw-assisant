# 贡献指南

感谢您对 OpenClaw 管理技能包项目的关注！

## 🤝 如何贡献

### 贡献方式

1. **报告问题**: 发现 bug 或有改进建议
2. **提交代码**: 修复 bug 或添加新功能
3. **完善文档**: 改进文档质量
4. **分享经验**: 分享使用经验和最佳实践
5. **开发新技能包**: 为新的功能开发技能包

## 📋 贡献流程

### 1. Fork 项目

```bash
# 在 GitHub 上 Fork 项目
# 然后克隆你的 Fork
git clone https://github.com/your-username/agent-openclaw-assisant.git
cd agent-openclaw-assisant
```

### 2. 创建分支

```bash
# 创建功能分支
git checkout -b feature/your-feature-name

# 或创建修复分支
git checkout -b fix/bug-description
```

### 3. 进行开发

按照项目规范进行开发（见下文）。

### 4. 提交代码

```bash
# 添加更改
git add .

# 提交（使用清晰的提交信息）
git commit -m "feat(manager): add instance health check"

# 推送到你的 Fork
git push origin feature/your-feature-name
```

### 5. 创建 Pull Request

在 GitHub 上创建 Pull Request，描述你的更改。

---

## 📝 代码规范

### 技能包开发规范

#### SKILL.md 文件
- 必须包含 YAML frontmatter（name、description）
- 主文件建议在 500 行以内
- 使用第三人称描述
- 包含清晰的触发条件
- 提供具体的使用示例

#### 目录结构
```
skill-name/
├── SKILL.md              # 必需
├── reference/            # 详细文档
├── scripts/              # 工具脚本
└── templates/            # 配置模板
```

#### 命名规范
- 技能包: `openclaw-{module}` (小写，连字符)
- 脚本文件: `script_name.py`, `script-name.sh`
- 配置模板: `name.template` 或 `name.example`

### Python 代码规范

- **风格**: 遵循 PEP 8
- **格式化**: 使用 Black
- **类型提示**: 使用 Python 类型注解
- **文档**: 每个函数都有 docstring
- **错误处理**: 明确的异常处理和错误信息

**示例:**

```python
from typing import Optional, Dict, Any
from pathlib import Path

def load_config(config_path: Path) -> Dict[str, Any]:
    """
    加载配置文件
    
    Args:
        config_path: 配置文件路径
    
    Returns:
        配置字典
    
    Raises:
        FileNotFoundError: 配置文件不存在
        yaml.YAMLError: YAML 解析错误
    """
    if not config_path.exists():
        raise FileNotFoundError(f"配置文件不存在: {config_path}")
    
    # ... 实现代码
```

### Shell 脚本规范

- **Shebang**: 使用 `#!/bin/bash` 或 `#!/usr/bin/env bash`
- **错误处理**: 使用 `set -euo pipefail`
- **函数**: 复杂逻辑使用函数封装
- **注释**: 关键步骤添加注释

**示例:**

```bash
#!/bin/bash
set -euo pipefail

# 安装 OpenClaw
install_openclaw() {
    local version="${1:-latest}"
    
    echo "📦 开始安装 OpenClaw ${version}..."
    
    # 检测安装方式
    if command -v npm &> /dev/null; then
        npm install -g openclaw@${version}
    else
        echo "❌ 未找到 npm，请先安装 Node.js"
        exit 1
    fi
    
    echo "✅ OpenClaw 安装完成"
}

# 主函数
main() {
    install_openclaw "$@"
}

main "$@"
```

### 配置文件规范

- **格式**: 使用 YAML（优先）或 JSON
- **注释**: 为每个配置项添加注释
- **模板**: 敏感信息使用占位符
- **示例**: 提供完整的配置示例

---

## 🧪 测试规范

### 脚本测试

每个 Python 脚本应包含测试代码：

```python
if __name__ == "__main__":
    # 测试代码
    test_function()
```

### 集成测试

在 `tests/` 目录添加集成测试脚本：

```bash
tests/
├── test_manager.sh         # 测试管理功能
├── test_deployment.sh      # 测试部署
└── integration/            # 完整流程测试
```

### 测试checklist

- [ ] 功能测试：核心功能正常工作
- [ ] 错误测试：错误情况有合适的提示
- [ ] 边界测试：边界条件处理正确
- [ ] 集成测试：与其他技能包协同工作

---

## 📖 文档规范

### 文档类型

1. **技能包文档**: SKILL.md + reference/
2. **项目文档**: docs/
3. **代码注释**: Docstring + inline comments
4. **README**: 各目录的 README.md

### 文档要求

- ✅ 清晰准确
- ✅ 包含示例
- ✅ 保持更新
- ✅ 中文为主（代码注释可使用英文）

### Markdown 规范

- 使用标准 Markdown 语法
- 代码块指定语言
- 表格对齐整齐
- 适当使用 emoji（不要过度）

---

## 🚀 开发环境设置

### 安装依赖

```bash
# Node.js 依赖
npm install

# Python 依赖
pip install -r requirements.txt

# 开发依赖
pip install -r requirements-dev.txt  # 如果有的话
```

### 配置开发环境

```bash
# 复制配置模板
cp shared/configs/global.yaml.template shared/configs/global.yaml

# 编辑配置
# 设置 development.debug = true
```

### 运行测试

```bash
# 测试共享工具
python shared/utils/common.py
python shared/utils/logger.py
python shared/utils/crypto.py

# 运行集成测试
bash tests/test_manager.sh
```

---

## 🎯 贡献示例

### 示例 1: 修复 Bug

```bash
# 1. 创建分支
git checkout -b fix/instance-creation-error

# 2. 修复代码
# 编辑 skills/openclaw-manager/scripts/instance_manager.py

# 3. 测试
python skills/openclaw-manager/scripts/instance_manager.py

# 4. 提交
git add .
git commit -m "fix(manager): handle invalid instance ID"

# 5. 推送并创建 PR
git push origin fix/instance-creation-error
```

### 示例 2: 添加新功能

```bash
# 1. 创建分支
git checkout -b feature/add-status-command

# 2. 开发功能
# 在合适的技能包中添加代码

# 3. 更新文档
# 更新 SKILL.md 和相关文档

# 4. 测试
# 运行测试确保功能正常

# 5. 提交
git add .
git commit -m "feat(manager): add status command for instances"

# 6. 推送并创建 PR
git push origin feature/add-status-command
```

### 示例 3: 完善文档

```bash
# 1. 创建分支
git checkout -b docs/improve-quickstart

# 2. 编辑文档
# 改进 docs/快速开始.md

# 3. 预览
# 在 Cursor 或其他 Markdown 编辑器中预览

# 4. 提交
git add .
git commit -m "docs: improve quick start guide with more examples"

# 5. 推送并创建 PR
git push origin docs/improve-quickstart
```

---

## 🎨 Commit Message 规范

### 格式

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Type 类型

- `feat`: 新功能
- `fix`: Bug 修复
- `docs`: 文档更新
- `style`: 代码格式（不影响功能）
- `refactor`: 重构
- `test`: 测试相关
- `chore`: 构建/工具相关

### Scope 范围

- `manager`: openclaw-manager 技能包
- `deploy`: openclaw-deploy 技能包
- `plugin`: openclaw-plugin 技能包
- `channel`: openclaw-channel 技能包
- `model`: openclaw-model 技能包
- `agent`: openclaw-agent 技能包
- `shared`: 共享工具
- `docs`: 文档
- `*`: 所有技能包

### 示例

```
feat(manager): add instance health check command

Implement health check functionality that reports instance status,
including process state, port availability, and resource usage.

Closes #123
```

---

## ✅ Pull Request 检查清单

提交 PR 之前，请确认：

- [ ] 代码遵循项目规范
- [ ] 添加了必要的测试
- [ ] 更新了相关文档
- [ ] 通过了所有测试
- [ ] Commit message 规范
- [ ] 没有提交敏感信息
- [ ] 没有提交 workspace/ 目录
- [ ] PR 描述清晰，说明了改动原因

---

## 💬 交流与讨论

### 提问

- **GitHub Issues**: 用于 bug 报告和功能请求
- **GitHub Discussions**: 用于问题讨论和经验分享

### 讨论主题

- 架构设计讨论
- 新功能提议
- 最佳实践分享
- 使用问题求助

---

## 🙏 致谢

感谢所有贡献者的付出！

### 贡献者列表

- [@lifeng](https://github.com/lifeng) - 项目创建者

---

## 📄 许可证

本项目采用 MIT 许可证。贡献代码即表示您同意将代码以相同许可证发布。

---

**有疑问？** 欢迎在 Issues 中提问！
