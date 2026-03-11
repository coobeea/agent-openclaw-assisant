# 项目结构总览

> 完整的目录结构和文件说明

**版本**: v1.0.0  
**文件总数**: 83 个  
**最后更新**: 2026-03-10

---

## 📂 完整目录树

```
agent-openclaw-assisant/
│
├── 📁 .cursor/                          # Cursor IDE 配置目录
│   ├── skills/                         # 技能包激活目录（软链接）
│   │   ├── openclaw-manager  → ../../skills/openclaw-manager
│   │   ├── openclaw-deploy   → ../../skills/openclaw-deploy
│   │   ├── openclaw-plugin   → ../../skills/openclaw-plugin
│   │   ├── openclaw-channel  → ../../skills/openclaw-channel
│   │   ├── openclaw-model    → ../../skills/openclaw-model
│   │   ├── openclaw-agent    → ../../skills/openclaw-agent
│   │   └── README.md                  # 软链接说明
│   └── README.md                       # .cursor 目录说明
│
├── 📁 skills/                           # 技能包源文件目录
│   │
│   ├── 📦 openclaw-manager/            # [P0] 实例管理技能包
│   │   ├── SKILL.md                    # 技能包主文件
│   │   ├── reference/                  # 参考文档
│   │   │   ├── installation.md         # 安装指南
│   │   │   ├── instance-management.md  # 实例管理
│   │   │   └── workspace-management.md # 工作空间管理
│   │   ├── scripts/                    # 工具脚本
│   │   │   ├── install_openclaw.sh     # 安装脚本
│   │   │   ├── instance_manager.py     # 实例管理CLI
│   │   │   └── requirements.txt        # Python依赖
│   │   └── templates/                  # 配置模板
│   │       └── instance.config.yaml    # 实例配置模板
│   │
│   ├── 📦 openclaw-deploy/             # [P1] 部署管理技能包
│   │   ├── SKILL.md
│   │   ├── reference/
│   │   │   ├── host-mode.md            # 主机部署
│   │   │   ├── container-mode.md       # 容器部署
│   │   │   └── kubernetes.md           # K8s部署
│   │   ├── scripts/
│   │   │   ├── deploy_host.sh          # 主机部署脚本
│   │   │   ├── deploy_docker.sh        # Docker部署脚本
│   │   │   ├── health_check.py         # 健康检查工具
│   │   │   └── requirements.txt
│   │   └── templates/
│   │       ├── Dockerfile              # Docker镜像
│   │       ├── docker-compose.yml      # Compose配置
│   │       ├── systemd/                # Systemd服务
│   │       │   └── openclaw@.service
│   │       └── kubernetes/             # K8s清单
│   │           ├── deployment.yaml
│   │           └── service.yaml
│   │
│   ├── 📦 openclaw-plugin/             # [P1] 插件管理技能包
│   │   ├── SKILL.md
│   │   ├── reference/
│   │   │   ├── feishu.md               # 飞书插件
│   │   │   ├── qq.md                   # QQ插件
│   │   │   ├── wecom.md                # 企业微信插件
│   │   │   └── dingtalk.md             # 钉钉插件
│   │   └── scripts/
│   │       ├── plugin_manager.py       # 插件管理CLI
│   │       └── requirements.txt
│   │
│   ├── 📦 openclaw-channel/            # [P1] 渠道管理技能包
│   │   ├── SKILL.md
│   │   ├── reference/
│   │   │   ├── channel-config.md       # 渠道配置
│   │   │   ├── credential-management.md # 凭证管理
│   │   │   └── platform-guides/        # 平台配置指南
│   │   │       └── feishu-setup.md
│   │   └── scripts/
│   │       ├── channel_manager.py      # 渠道管理CLI
│   │       ├── credential_encrypt.py   # 加密工具
│   │       ├── connection_test.py      # 连接测试
│   │       └── requirements.txt
│   │
│   ├── 📦 openclaw-model/              # [P2] 模型管理技能包
│   │   ├── SKILL.md
│   │   ├── reference/
│   │   │   ├── model-config.md         # 模型配置
│   │   │   ├── supported-models.md     # 支持的模型
│   │   │   └── api-keys.md             # API密钥管理
│   │   └── scripts/
│   │       ├── model_manager.py        # 模型管理CLI
│   │       └── requirements.txt
│   │
│   ├── 📦 openclaw-agent/              # [P2] 智能体管理技能包
│   │   ├── SKILL.md
│   │   ├── reference/
│   │   │   ├── agent-config.md         # 智能体配置
│   │   │   ├── agent-routing.md        # 路由规则
│   │   │   └── multi-agent.md          # 多智能体
│   │   └── scripts/
│   │       ├── agent_manager.py        # 智能体管理CLI
│   │       └── requirements.txt
│   │
│   ├── README.md                        # 技能包目录说明
│   └── SKILLS_MANIFEST.yaml            # 技能包清单
│
├── 📁 shared/                           # 共享资源目录
│   ├── utils/                          # 工具库
│   │   ├── common.py                   # 通用工具
│   │   ├── logger.py                   # 日志系统
│   │   ├── crypto.py                   # 加密工具
│   │   └── README.md                   # 工具说明
│   └── configs/                        # 配置模板
│       ├── global.yaml.template        # 全局配置模板
│       └── README.md                   # 配置说明
│
├── 📁 docs/                             # 文档目录
│   ├── 快速开始.md                      # 5分钟入门
│   ├── 使用示例.md                      # 7个实战场景
│   ├── FAQ.md                           # 45+常见问题
│   ├── 需求分析.md                      # 需求和架构（v2.1）
│   ├── 架构设计.md                      # 系统架构详解
│   ├── 技能包索引.md                    # 功能索引
│   ├── 技能包激活验证.md                # 验证指南
│   ├── 项目结构.md                      # 结构说明
│   ├── 项目概览.md                      # 架构全景
│   ├── 项目完成总结.md                  # 完成总结
│   ├── 工作空间管理.md                  # 工作空间原则
│   ├── 工作空间设计说明.md              # 设计要点
│   ├── 开发进度.md                      # 进度追踪
│   └── 文件清单.md                      # 文件清单
│
├── 📁 workspace/                        # 实例工作空间（Git排除）
│   ├── openclaw-prod-01/               # 生产实例1
│   ├── openclaw-prod-02/               # 生产实例2
│   ├── openclaw-test-01/               # 测试实例
│   └── openclaw-dev-01/                # 开发实例
│
├── 📄 README.md                         # 项目主入口
├── 📄 STATUS.md                         # 项目状态快照
├── 📄 DELIVERY.md                       # 交付报告
├── 📄 PROJECT_SUMMARY.md                # 项目总览
├── 📄 STRUCTURE.md                      # 本文件
├── 📄 CHANGELOG.md                      # 变更日志
├── 📄 CONTRIBUTING.md                   # 贡献指南
├── 📄 LICENSE                           # MIT许可证
├── 📄 AGENTS.md                         # ⭐ Cursor 智能入口文件（核心，意图识别+流程编排）
│
├── 🔧 verify.sh                         # 项目验证脚本
├── 📄 requirements.txt                  # Python依赖
└── 📄 .gitignore                        # Git排除规则（隐私保护）
```

---

## 📊 文件分类统计

### 按类型

| 类型 | 数量 | 说明 |
|------|------|------|
| **SKILL.md** | 6 | 技能包主文件 |
| **Python 脚本** | 11 | CLI 工具 |
| **Bash 脚本** | 3 | 部署脚本 |
| **Markdown 文档** | 40+ | 项目和参考文档 |
| **YAML 配置** | 8 | 配置和模板 |
| **其他配置** | 4 | requirements.txt, .gitignore等 |

### 按目录

| 目录 | 文件数 | 占比 |
|------|--------|------|
| skills/ | 50 | 60% |
| docs/ | 14 | 17% |
| shared/ | 6 | 7% |
| .cursor/ | 2 | 2% |
| 根目录 | 11 | 14% |

---

## 🗂️ 重要文件速查

### 项目入口

| 文件 | 用途 | 优先级 |
|------|------|--------|
| README.md | 项目主入口，完整介绍 | ⭐⭐⭐ |
| STATUS.md | 项目状态快照 | ⭐⭐⭐ |
| DELIVERY.md | 详细交付报告 | ⭐⭐ |
| verify.sh | 一键验证脚本 | ⭐⭐⭐ |

### 必读文档

| 文件 | 用途 | 适合人群 |
|------|------|---------|
| docs/快速开始.md | 5分钟入门 | 新手 |
| docs/使用示例.md | 7个实战场景 | 新手/进阶 |
| docs/FAQ.md | 45+问题解答 | 所有人 |
| docs/需求分析.md | 完整需求和架构 | 开发者 |
| docs/架构设计.md | 系统架构详解 | 开发者 |

### 技能包文件

每个技能包的标准结构：

```
skills/openclaw-xxx/
├── SKILL.md              # 技能包主文件（Cursor识别）
├── reference/            # 详细参考文档
│   ├── guide-1.md
│   ├── guide-2.md
│   └── ...
├── scripts/              # 工具脚本
│   ├── tool.py          # Python CLI工具
│   └── requirements.txt # 依赖
└── templates/            # 配置模板（可选）
    └── config.yaml
```

---

## 🔍 文件功能说明

### 根目录文件

| 文件 | 功能 | 是否提交Git |
|------|------|-----------|
| README.md | 项目主入口和完整说明 | ✅ |
| STATUS.md | 项目状态快照 | ✅ |
| DELIVERY.md | 详细交付报告 | ✅ |
| PROJECT_SUMMARY.md | 项目总览 | ✅ |
| STRUCTURE.md | 本文件（结构说明） | ✅ |
| CHANGELOG.md | 变更日志 | ✅ |
| CONTRIBUTING.md | 贡献指南 | ✅ |
| LICENSE | MIT许可证 | ✅ |
| AGENTS.md | ⭐ Cursor 智能入口（意图识别+流程编排引擎） | ✅ |
| verify.sh | 验证脚本 | ✅ |
| requirements.txt | Python依赖 | ✅ |
| .gitignore | Git排除规则 | ✅ |

### 共享资源文件

| 文件 | 功能 | 依赖 |
|------|------|------|
| shared/utils/common.py | 路径/配置/命令管理 | pyyaml, click |
| shared/utils/logger.py | 统一日志系统 | logging |
| shared/utils/crypto.py | Fernet凭证加密 | cryptography |
| shared/configs/global.yaml.template | 全局配置模板 | - |

### 技能包脚本

| 脚本 | 功能 | 技能包 |
|------|------|--------|
| install_openclaw.sh | OpenClaw自动安装 | manager |
| instance_manager.py | 实例CRUD管理 | manager |
| deploy_host.sh | 主机模式部署 | deploy |
| deploy_docker.sh | Docker部署 | deploy |
| health_check.py | 健康检查 | deploy |
| plugin_manager.py | 插件管理 | plugin |
| channel_manager.py | 渠道配置 | channel |
| credential_encrypt.py | 凭证加密 | channel |
| connection_test.py | 连接测试 | channel |
| model_manager.py | 模型管理 | model |
| agent_manager.py | 智能体管理 | agent |

---

## 🎨 目录设计理念

### 分层架构

```
用户交互层     Cursor AI
               ↓
激活层         .cursor/skills/ (软链接)
               ↓
实现层         skills/ (源文件)
               ↓
工具层         shared/ (共享资源)
               ↓
OpenClaw层     OpenClaw CLI
               ↓
数据层         workspace/ (实例数据)
```

### 关注点分离

| 目录 | 关注点 | 变更频率 |
|------|--------|---------|
| .cursor/ | Cursor识别和激活 | 低 |
| skills/ | 技能包功能实现 | 中 |
| shared/ | 共享工具和配置 | 低 |
| docs/ | 文档和说明 | 中 |
| workspace/ | 运行时数据 | 高（不提交） |

---

## 🔗 软链接机制

### 为什么使用软链接？

**问题**: 
- Cursor 识别 `.cursor/skills/`
- 但我们想在 `skills/` 中管理源文件

**方案**: 软链接

```
源文件 (版本控制)         Cursor识别
skills/                   .cursor/skills/
├── openclaw-manager/ →   ├── openclaw-manager/
├── openclaw-deploy/  →   ├── openclaw-deploy/
└── ...                   └── ...
```

### 软链接验证

```bash
# 查看软链接
ls -la .cursor/skills/

# 输出示例:
# openclaw-manager -> ../../skills/openclaw-manager
# ^^^^^^^^^^^^^^^^    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   链接名称                  指向的源文件
```

### 软链接工作原理

```
修改源文件
    ↓
skills/openclaw-manager/SKILL.md (源文件被修改)
    ↓
.cursor/skills/openclaw-manager/SKILL.md (软链接自动反映)
    ↓
Cursor AI 读取到最新内容
```

---

## 🔐 敏感文件保护

### Git 排除列表

```gitignore
# 工作空间（包含实例数据）
workspace/

# 密钥和凭证
.keyfile
*.key
*.pem
*.env
*.env.*

# 配置文件（可能包含敏感信息）
shared/configs/global.yaml

# 日志
logs/
*.log

# 临时文件
*.tmp
*.cache
```

### 为什么排除 workspace/?

```
workspace/
└── openclaw-prod-01/
    ├── (OpenClaw的配置文件 - 可能包含凭证)
    ├── (对话历史 - 用户隐私)
    ├── (日志文件 - 敏感信息)
    └── .keyfile (加密密钥 - 绝密)
```

**原则**: 所有运行时数据和敏感信息都不提交到Git。

---

## 📈 目录增长历史

### Phase 1: 基础设施（第1天）

```
agent-openclaw-assisant/
├── docs/需求分析.md
├── README.md
└── .gitignore
```

**文件数**: ~5

### Phase 2: 技能包规划（第1天）

```
+ skills/openclaw-*/
+ shared/utils/
+ shared/configs/
```

**文件数**: ~20

### Phase 3: 完整实现（第1天完成）

```
+ 所有 SKILL.md
+ 所有 reference/ 文档
+ 所有 scripts/ 工具
+ 所有 templates/ 模板
```

**文件数**: ~70

### Phase 4: 激活和完善（第1天完成）

```
+ .cursor/skills/ (软链接)
+ 项目文档（14篇）
+ 验证工具
+ 交付报告
```

**文件数**: 83（当前）

---

## 🎯 文件优先级

### P0（必读）

- README.md
- verify.sh
- docs/快速开始.md

### P1（推荐阅读）

- docs/使用示例.md
- docs/FAQ.md
- STATUS.md
- skills/openclaw-manager/SKILL.md

### P2（深入理解）

- docs/需求分析.md
- docs/架构设计.md
- DELIVERY.md
- 各技能包的 reference/

### P3（参考）

- STRUCTURE.md（本文件）
- docs/文件清单.md
- 各技能包的详细文档

---

## 🔄 文件依赖关系

### 配置依赖

```
shared/configs/global.yaml.template (模板)
            ↓ (用户复制)
shared/configs/global.yaml (实际配置，不提交Git)
            ↓ (脚本读取)
各个 Python 脚本
            ↓ (操作)
workspace/ (实例数据)
```

### 文档依赖

```
README.md (入口)
    ↓
docs/快速开始.md (入门)
    ↓
docs/使用示例.md (实践)
    ↓
各技能包的 SKILL.md (功能)
    ↓
各技能包的 reference/ (详细)
```

### 技能包依赖

```
openclaw-manager (基础)
    ↓
openclaw-deploy, openclaw-plugin, openclaw-channel (核心)
    ↓
openclaw-model, openclaw-agent (高级)
```

---

## 📝 文件命名规范

### Markdown 文档

- **中文文档**: 使用中文文件名（如 `快速开始.md`）
- **英文文档**: 使用英文文件名（如 `SKILL.md`）
- **大小写**: 
  - 项目级文档：全大写（README.md, STATUS.md）
  - 技能包文档：小写加横线（instance-management.md）

### 脚本文件

- **Python**: 小写+下划线（instance_manager.py）
- **Bash**: 小写+下划线（install_openclaw.sh）
- **可执行**: 所有脚本都有执行权限

### 配置文件

- **模板**: 后缀 `.template`（global.yaml.template）
- **实际配置**: 不提交Git（global.yaml）
- **示例**: 后缀 `.example`（.env.example）

---

## 🎓 如何导航这个项目

### 场景1: 我是新手

```
1. 阅读 README.md（5分钟）
2. 运行 ./verify.sh（1分钟）
3. 阅读 docs/快速开始.md（10分钟）
4. 在 Cursor 中尝试创建实例（5分钟）
```

**总耗时**: 约 20 分钟

### 场景2: 我想深入理解架构

```
1. 阅读 docs/需求分析.md（30分钟）
2. 阅读 docs/架构设计.md（30分钟）
3. 查看 skills/openclaw-manager/（20分钟）
4. 查看 shared/utils/（10分钟）
```

**总耗时**: 约 90 分钟

### 场景3: 我遇到了问题

```
1. 查看 docs/FAQ.md 搜索问题关键词
2. 如果是技能包问题，查看对应 reference/
3. 如果是激活问题，查看 docs/技能包激活验证.md
4. 运行 ./verify.sh 诊断
```

### 场景4: 我想贡献代码

```
1. 阅读 CONTRIBUTING.md（10分钟）
2. 理解 STRUCTURE.md（本文件）（15分钟）
3. 查看相关技能包的实现（30分钟）
4. 开发、测试、提交
```

---

## 🛠️ 目录维护

### 添加新技能包

```bash
# 1. 创建目录
mkdir -p skills/new-skill/{reference,scripts,templates}

# 2. 创建文件
touch skills/new-skill/SKILL.md
touch skills/new-skill/scripts/tool.py

# 3. 添加执行权限
chmod +x skills/new-skill/scripts/tool.py

# 4. 创建软链接
cd .cursor/skills
ln -s ../../skills/new-skill new-skill

# 5. 验证
../../verify.sh
```

### 重组目录结构

**原则**: 保持 Cursor 技能包标准格式

```
skills/skill-name/
├── SKILL.md       (必需)
├── reference/     (推荐)
├── scripts/       (推荐)
└── templates/     (可选)
```

### 清理临时文件

```bash
# 清理Python缓存
find . -type d -name "__pycache__" -exec rm -rf {} +
find . -type f -name "*.pyc" -delete

# 清理日志
find . -name "*.log" -delete

# 清理临时文件
find . -name "*.tmp" -delete
```

---

## 📦 打包和分发

### 完整打包（含文档）

```bash
tar -czf openclaw-skills-v1.0.0-full.tar.gz \
  --exclude='.git' \
  --exclude='workspace' \
  --exclude='node_modules' \
  --exclude='__pycache__' \
  .
```

### 精简打包（仅核心）

```bash
tar -czf openclaw-skills-v1.0.0-core.tar.gz \
  skills/ \
  shared/ \
  .cursor/ \
  README.md \
  verify.sh \
  requirements.txt \
  .gitignore
```

---

## 📐 目录设计原则

### 1. 单一职责

每个目录有明确的职责：
- `skills/`: 技能包实现
- `shared/`: 共享资源
- `docs/`: 文档
- `.cursor/`: Cursor 激活

### 2. 高内聚低耦合

- 每个技能包独立
- 通过 shared/ 共享通用功能
- 通过软链接连接到 Cursor

### 3. 可扩展性

- 新技能包只需添加到 skills/
- 创建软链接即可激活
- 不影响现有技能包

### 4. 易于维护

- 清晰的目录结构
- 统一的命名规范
- 完整的文档说明

---

## 🎉 总结

### 目录特点

✅ **结构清晰**: 分层架构，职责明确  
✅ **易于导航**: 标准化的命名和组织  
✅ **完整文档**: 每个目录都有说明  
✅ **安全设计**: 敏感文件严格排除  
✅ **可扩展**: 易于添加新技能包

### 目录统计

- **总目录数**: ~25 个
- **总文件数**: 83 个
- **文档占比**: 65%（53个文档）
- **代码占比**: 25%（21个脚本）
- **配置占比**: 10%（9个配置）

---

**文件结构版本**: v1.0  
**最后更新**: 2026-03-10  
**维护状态**: ✅ 活跃
