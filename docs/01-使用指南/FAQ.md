# 常见问题解答（FAQ）

## 基础概念

### Q1: 什么是"龙虾军团"？

**A**: "龙虾军团"是对多个 OpenClaw 实例的一个形象称呼。每个 OpenClaw 实例就像一只龙虾（Claw），多个实例组成军团，可以部署在不同环境、对接不同平台。

### Q2: 为什么要管理多个 OpenClaw 实例？

**A**: 不同场景需要不同配置：
- **环境隔离**: 开发、测试、生产环境分离
- **平台分离**: 不同的消息平台使用不同实例
- **负载分担**: 多个实例分担高并发请求
- **灾备**: 主备实例，高可用

### Q3: 这个项目和 OpenClaw 是什么关系？

**A**: 
- **OpenClaw**: 开源的个人 AI 助手平台（上游项目）
- **本项目**: 为 Cursor IDE 打造的 OpenClaw 管理工具集（管理工具）

类比：OpenClaw 是 Docker，本项目是 Docker Compose/K8s。

---

## 安装和配置

### Q4: GitHub 访问很慢或无法访问怎么办？🇨🇳

**A**: 使用 Gitee 国内镜像

**镜像地址**: `https://gitee.com/618lf/openclaw.git`

**使用方法**:
```bash
# 使用 Gitee 镜像（国内，推荐）
git clone https://gitee.com/618lf/openclaw.git openclaw

# 原 GitHub 地址（国外）
git clone https://github.com/openclaw/openclaw.git
```

**速度提升**: 50-100倍 🚀

**详细说明** → [网络问题-国内镜像.md](../02-问题解决/网络问题-国内镜像.md)

---

### Q5: 必须在 Cursor 中使用吗？

**A**: 不是。有两种使用方式：

1. **Cursor 中使用（推荐）**: 自然语言交互，最方便
   ```
   "帮我创建一个实例"
   ```

2. **命令行使用**: 直接执行脚本
   ```bash
   python skills/openclaw-manager/scripts/instance_manager.py create openclaw-prod-01
   ```

### Q5: 如何配置工作空间路径？

**A**: 复制配置模板：

```bash
cp shared/configs/global.yaml.template shared/configs/global.yaml
```

编辑 `global.yaml`:

```yaml
workspace_root: ./workspace  # 相对路径
# 或
workspace_root: /var/lib/openclaw  # 绝对路径
# 或
workspace_root: ~/openclaw-data  # 用户主目录
```

### Q6: 工作空间会上传到 Git 吗？

**A**: **不会！** `.gitignore` 已配置排除：
- `workspace/` 目录
- `*.key`, `*.env` 等敏感文件
- 日志文件

### Q7: 如何验证项目安装正确？

**A**: 验证环境是否就绪：

```bash
# macOS/Linux
bash skills/env-checker/scripts/check.sh

# Windows
skills\env-checker\scripts\check.bat
```

看到 `VENV_EXISTS=true` 表示虚拟环境已就绪。

---

## 技能包使用

### Q8: 技能包之间有依赖关系吗？

**A**: 有推荐顺序：

```
1. openclaw-manager (必需) - 安装和实例管理
   ↓
2. openclaw-deploy (推荐) - 部署到生产
   ↓
3. openclaw-plugin (推荐) - 安装平台插件
   ↓
4. openclaw-channel (推荐) - 配置渠道
   ↓
5. openclaw-model (可选) - 添加 AI 模型
   ↓
6. openclaw-agent (可选) - 创建智能体
```

但你可以只使用需要的部分。

### Q9: 软链接是什么？为什么要用软链接？

**A**: 

**软链接（Symbolic Link）**: 类似 Windows 的"快捷方式"。

```
.cursor/skills/openclaw-manager  →  skills/openclaw-manager
     (快捷方式)                         (实际文件)
```

**为什么用**:
- Cursor 识别 `.cursor/skills/`
- 源文件在 `skills/` 便于管理
- 修改源文件，Cursor 立即生效

**查看软链接**:
```bash
ls -la .cursor/skills/
```

看到箭头（→）就是软链接。

### Q10: 软链接失效了怎么办？

**A**: 重新创建：

```bash
cd .cursor/skills
rm openclaw-manager
ln -s ../../skills/openclaw-manager openclaw-manager
```

或批量重建：
```bash
cd .cursor/skills
rm -f openclaw-*
ln -s ../../skills/openclaw-* .
```

---

## 实例管理

### Q11: 实例命名有什么规范？

**A**: 推荐格式：`openclaw-{env}-{num}`

**示例**:
- ✅ `openclaw-prod-01` (生产-编号)
- ✅ `openclaw-test-feishu` (测试-平台)
- ✅ `openclaw-dev-alice` (开发-开发者)
- ❌ `instance1` (不明确)
- ❌ `龙虾-01` (使用中文)

### Q12: 如何查看所有实例？

**A**: 

在 Cursor 中：
```
"查看所有实例"
```

或命令行：
```bash
python skills/openclaw-manager/scripts/instance_manager.py list
```

### Q13: 实例启动失败怎么办？

**A**: 按步骤排查：

```bash
# 1. 查看详细日志
python skills/openclaw-manager/scripts/instance_manager.py logs openclaw-prod-01

# 2. 检查端口占用
lsof -i :3000

# 3. 检查实例状态
python skills/openclaw-manager/scripts/instance_manager.py status openclaw-prod-01

# 4. 检查工作空间权限
ls -la workspace/openclaw-prod-01
```

### Q14: 如何删除实例？

**A**: 

```bash
python skills/openclaw-manager/scripts/instance_manager.py delete openclaw-prod-01
```

**警告**: 这会删除实例的所有数据！建议先备份：

```bash
tar -czf openclaw-prod-01-backup.tar.gz workspace/openclaw-prod-01/
```

---

## 部署相关

### Q15: 主机模式和容器模式有什么区别？

**A**: 

| 模式 | 适用场景 | 优点 | 缺点 |
|------|---------|------|------|
| **主机** | 开发、单机 | 简单、性能好 | 环境依赖 |
| **容器** | 测试、生产 | 隔离、易迁移 | 需要 Docker |
| **K8s** | 大规模、集群 | 高可用、弹性 | 复杂度高 |

### Q16: 如何在 Docker 中部署？

**A**: 

在 Cursor 中：
```
"将 openclaw-prod-01 部署到 Docker"
```

或手动：
```bash
bash skills/openclaw-deploy/scripts/deploy_docker.sh openclaw-prod-01
```

### Q17: Docker 容器如何查看日志？

**A**: 

```bash
docker logs -f openclaw-prod-01
```

或通过技能包：
```bash
python skills/openclaw-manager/scripts/instance_manager.py logs openclaw-prod-01
```

---

## 平台集成

### Q18: 支持哪些消息平台？

**A**: 目前支持 4 个平台：
- ✅ 飞书 (Feishu)
- ✅ QQ
- ✅ 企业微信 (WeCom)
- ✅ 钉钉 (DingTalk)

### Q19: 如何获取飞书的 App ID 和 App Secret？

**A**: 参考详细指南：

```bash
cat skills/openclaw-channel/reference/platform-guides/feishu-setup.md
```

简要步骤：
1. 访问飞书开放平台
2. 创建企业自建应用
3. 在"凭证与基础信息"中获取

### Q20: 一个实例可以同时对接多个平台吗？

**A**: **可以！** 这正是本项目的核心功能之一：

```bash
# 安装多个平台插件
python skills/openclaw-plugin/scripts/plugin_manager.py install feishu --instance openclaw-prod-01
python skills/openclaw-plugin/scripts/plugin_manager.py install qq --instance openclaw-prod-01

# 配置多个渠道
python skills/openclaw-channel/scripts/channel_manager.py add --instance openclaw-prod-01 --platform feishu ...
python skills/openclaw-channel/scripts/channel_manager.py add --instance openclaw-prod-01 --platform qq ...
```

---

## 安全相关

### Q21: API Key 和 App Secret 安全吗？

**A**: **安全！** 采用多层保护：

1. **加密存储**: Fernet 对称加密
2. **Git 排除**: 不会提交到版本控制
3. **权限控制**: 密钥文件 600 权限
4. **显示遮罩**: 显示时只显示部分字符（如 `sk-...xyz`）

### Q22: 加密密钥存储在哪里？

**A**: 

```
workspace/{instance}/.keyfile
```

**权限**: 600（仅所有者可读写）

**重要**: 备份这个文件！丢失后无法解密已存储的凭证。

### Q23: 如何手动加密/解密凭证？

**A**: 使用加密工具：

```bash
# 加密
python skills/openclaw-channel/scripts/credential_encrypt.py encrypt "my-secret"

# 解密
python skills/openclaw-channel/scripts/credential_encrypt.py decrypt "gAAAAAB..."
```

---

## 模型和智能体

### Q24: 支持哪些 AI 模型？

**A**: 

**在线模型**:
- OpenAI: gpt-4, gpt-3.5-turbo
- Anthropic: claude-3-opus, claude-3-sonnet

**本地模型**:
- Ollama: llama2, mistral, codellama
- LM Studio: 所有 GGUF 格式

详见：`skills/openclaw-model/reference/supported-models.md`

### Q25: 一个实例可以有多个智能体吗？

**A**: **可以！** 这是多智能体架构：

```
实例: openclaw-prod-01
  ├── customer-service (客服)
  ├── tech-support (技术支持)
  └── sales (销售)
```

每个智能体可以：
- 使用不同的 AI 模型
- 对接不同的渠道
- 有独立的配置

### Q26: 如何选择合适的模型？

**A**: 根据场景选择：

| 场景 | 推荐模型 | 原因 |
|------|---------|------|
| 客服 | gpt-3.5-turbo | 快速、成本低 |
| 技术支持 | gpt-4 | 专业、准确 |
| 创意生成 | claude-3-sonnet | 创意好、平衡 |
| 本地测试 | ollama/llama2 | 免费、隐私 |

---

## 故障排除

### Q27: 提示"实例不存在"？

**A**: 

```bash
# 1. 检查实例是否真的存在
python skills/openclaw-manager/scripts/instance_manager.py list

# 2. 检查工作空间路径配置
cat shared/configs/global.yaml

# 3. 检查目录权限
ls -la workspace/
```

### Q28: 渠道连接测试失败？

**A**: 

```bash
# 1. 测试连接
python skills/openclaw-channel/scripts/connection_test.py openclaw-prod-01 feishu

# 2. 检查凭证是否正确
python skills/openclaw-channel/scripts/channel_manager.py list --instance openclaw-prod-01

# 3. 在平台后台检查应用状态
# 访问飞书开放平台，查看应用是否启用

# 4. 检查回调地址配置
# 确保 webhook URL 正确配置
```

### Q29: 模型调用失败？

**A**: 

```bash
# 1. 检查 API Key 是否有效
python skills/openclaw-model/scripts/model_manager.py list --instance openclaw-prod-01

# 2. 测试 API Key（在浏览器中）
# OpenAI: https://platform.openai.com/usage
# Anthropic: https://console.anthropic.com/settings/keys

# 3. 检查余额
# 确保账户有足够的额度

# 4. 更新 API Key
python skills/openclaw-model/scripts/model_manager.py add \
  --instance openclaw-prod-01 \
  --model gpt-4 \
  --provider openai \
  --api-key sk-new-key
```

### Q30: 脚本执行时提示"Permission denied"？

**A**: 添加执行权限：

```bash
chmod +x skills/*/scripts/*.py
chmod +x skills/*/scripts/*.sh
```

或重新运行：
```bash
python skills/openclaw-manager/scripts/instance_manager.py ...
```

---

## 高级用法

### Q31: 如何实现智能体之间的协作？

**A**: 通过路由规则实现：

```yaml
# 在 OpenClaw 配置中设置
routing:
  - keywords: ["技术", "bug"]
    agent: tech-support
  - keywords: ["购买", "价格"]
    agent: sales
  - default: customer-service
```

详见：`skills/openclaw-agent/reference/agent-routing.md`

### Q32: 如何监控实例的健康状态？

**A**: 使用健康检查工具：

```bash
python skills/openclaw-deploy/scripts/health_check.py openclaw-prod-01
```

输出示例：
```
✅ 工作空间
✅ 端口 3000
✅ HTTP 响应
✅ CPU 使用率 15%
✅ 内存使用率 42%
```

### Q33: 如何备份实例数据？

**A**: 

```bash
# 1. 停止实例（建议）
python skills/openclaw-manager/scripts/instance_manager.py stop openclaw-prod-01

# 2. 打包工作空间
tar -czf openclaw-prod-01-backup-$(date +%Y%m%d).tar.gz workspace/openclaw-prod-01/

# 3. 重新启动
python skills/openclaw-manager/scripts/instance_manager.py start openclaw-prod-01
```

**恢复**:
```bash
tar -xzf openclaw-prod-01-backup-20260310.tar.gz -C workspace/
```

### Q34: 如何在多台服务器上部署？

**A**: 

**方案 1: 克隆项目**
```bash
# 在每台服务器上
git clone <repo-url>
cd agent-openclaw-assisant
bash skills/env-checker/scripts/setup.sh
```

**方案 2: Kubernetes**
```bash
# 使用 K8s 部署到集群
kubectl apply -f skills/openclaw-deploy/templates/kubernetes/deployment.yaml
```

### Q35: 如何添加新的消息平台（如 Slack）？

**A**: 

1. **添加插件文档**:
   ```bash
   cat > skills/openclaw-plugin/reference/slack.md <<EOF
   # Slack 插件配置指南
   ...
   EOF
   ```

2. **更新插件管理器**:
   在 `plugin_manager.py` 的支持列表中添加 'slack'

3. **添加渠道配置指南**:
   ```bash
   cat > skills/openclaw-channel/reference/platform-guides/slack-setup.md <<EOF
   ...
   EOF
   ```

4. **更新 SKILL.md**: 在相关技能包的文档中添加 Slack 说明

---

## 性能和扩展

### Q36: 最多可以创建多少个实例？

**A**: **理论上无限制**，实际受限于：
- 系统资源（CPU、内存）
- 端口数量（每个实例占用一个端口）
- OpenClaw 本身的限制

**建议**:
- 单机: 1-10 个实例
- 容器: 10-50 个实例
- K8s: 50+ 个实例

### Q37: 实例占用多少资源？

**A**: 取决于配置和负载，**参考值**：

| 资源 | 最小 | 推荐 | 高负载 |
|------|------|------|--------|
| CPU | 0.5 核 | 1 核 | 2 核 |
| 内存 | 512 MB | 1 GB | 2 GB |
| 磁盘 | 100 MB | 1 GB | 10 GB |

### Q38: 如何提升性能？

**A**: 

1. **使用更快的模型**: gpt-3.5-turbo 比 gpt-4 快
2. **调整并发数**: 限制每个实例的并发会话
3. **使用缓存**: OpenClaw 的缓存功能
4. **负载均衡**: 多实例分担负载
5. **容器优化**: 调整 Docker 资源限制

---

## 开发和贡献

### Q39: 如何修改技能包？

**A**: 

1. **编辑源文件**（不是软链接）:
   ```bash
   vim skills/openclaw-manager/SKILL.md
   ```

2. **保存后立即生效**: Cursor 通过软链接读取最新内容

3. **测试**: 在 Cursor 中测试修改后的功能

4. **提交**: 
   ```bash
   git add skills/openclaw-manager/
   git commit -m "update: improve openclaw-manager skill"
   ```

### Q40: 如何添加新的脚本工具？

**A**: 

1. **创建脚本**:
   ```bash
   cat > skills/openclaw-manager/scripts/backup.py <<EOF
   #!/usr/bin/env python3
   ...
   EOF
   ```

2. **添加执行权限**:
   ```bash
   chmod +x skills/openclaw-manager/scripts/backup.py
   ```

3. **更新 SKILL.md**: 在工具说明中添加新工具的描述

4. **测试**: 运行脚本确保正常工作

### Q41: 如何贡献代码？

**A**: 参考 `CONTRIBUTING.md`:

1. Fork 项目
2. 创建功能分支
3. 编写代码和文档
4. 验证环境：`bash skills/env-checker/scripts/check.sh`
5. 提交 Pull Request

---

## 其他问题

### Q42: 这个项目是免费的吗？

**A**: **是的！** 本项目采用 MIT 许可证，完全开源免费。

但使用 AI 模型（如 OpenAI、Anthropic）需要自己的 API Key，会产生费用。

### Q43: 支持 Windows 吗？

**A**: 

**部分支持**:
- ✅ Python 脚本：完全支持
- ⚠️ Bash 脚本：需要 Git Bash 或 WSL
- ⚠️ 软链接：需要 Windows 10+ 开发者模式

**推荐**: 在 Windows 上使用 WSL2。

### Q44: 项目会持续更新吗？

**A**: 

**已完成**: 核心功能（Phase 1-5）  
**待开发**: 增强功能（Phase 6）

更新策略：
- 跟随 OpenClaw 版本更新
- 根据用户反馈改进
- 添加新功能和平台

查看 `CHANGELOG.md` 了解更新历史。

### Q45: 遇到问题怎么办？

**A**: 

1. **查看文档**: 先查阅相关文档
   - `docs/使用示例.md` - 实战场景
   - `docs/快速开始.md` - 入门教程
   - 各技能包的 `reference/` - 详细说明

2. **验证环境**: 
   ```bash
   bash skills/env-checker/scripts/check.sh
   ```

3. **查看日志**:
   ```bash
   python skills/openclaw-manager/scripts/instance_manager.py logs <instance-id>
   ```

4. **提 Issue**: 在项目仓库提交问题

---

## 快速参考

### 最常用命令

```bash
# 验证环境
bash skills/env-checker/scripts/check.sh

# 创建实例
python skills/openclaw-manager/scripts/instance_manager.py create openclaw-prod-01

# 启动实例
python skills/openclaw-manager/scripts/instance_manager.py start openclaw-prod-01

# 查看状态
python skills/openclaw-manager/scripts/instance_manager.py status openclaw-prod-01

# 查看日志
python skills/openclaw-manager/scripts/instance_manager.py logs openclaw-prod-01

# 列出所有实例
python skills/openclaw-manager/scripts/instance_manager.py list
```

### 最常用的 Cursor 指令

```
"安装 OpenClaw"
"创建实例"
"启动实例"
"查看状态"
"部署到 Docker"
"添加飞书插件"
"配置渠道"
"添加模型"
"创建智能体"
```

---

**有其他问题？** 欢迎查看详细文档或在 Cursor 中直接提问！
