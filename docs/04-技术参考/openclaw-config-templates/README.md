# OpenClaw 配置模板

本目录提供三种开箱即用的配置模板，适用于不同的使用场景。

---

## 📁 模板文件列表

### 1. 激进模式-零门槛配置.json

**适用场景**：
- ✅ 开发测试环境
- ✅ 内网隔离环境
- ✅ 快速上手学习
- ✅ 个人本地使用

**特点**：
- **完全无需认证**（auth.mode=none）
- 无需任何 Token
- 飞书机器人无需配对（开放模式）
- 禁用设备认证
- 真正的零门槛，即开即用

**访问方式**：
- 主机模式：`http://127.0.0.1:18800/`
- Docker 模式：`http://127.0.0.1:18900/`（使用 Nginx 代理，局域网可访问）

**技术方案**：
- OpenClaw 使用 loopback 绑定（127.0.0.1:3000）
- Docker 部署时使用 Nginx 反向代理（0.0.0.0:18900）

**⚠️ 警告**：不要在公网或生产环境使用！

---

### 2. 混合模式-团队协作配置.json

**适用场景**：
- ✅ 小团队协作
- ✅ 内网环境
- ✅ 需要基本访问控制

**特点**：
- Control UI 需要 Token（可分享给团队）
- 飞书私聊开放（团队成员直接用）
- 飞书群聊需配对（控制机器人被拉入哪些群）
- 平衡便利性和安全性

**适合团队**：5-20 人的小型团队

---

### 3. 安全模式-生产环境配置.json

**适用场景**：
- ✅ 生产环境
- ✅ 公网访问
- ✅ 大型组织
- ✅ 需要审计日志

**特点**：
- Token 认证 + 设备绑定
- 飞书私聊和群聊都需配对
- 仅本地访问（或配合防火墙）
- 使用密钥引用（不在配置中明文存储）
- 完整的访问控制

**适合组织**：20+ 人的团队或企业

---

## 🚀 使用方法

### 方法 1：创建新实例时使用

```bash
# 1. 创建实例
python skills/openclaw-manager/scripts/instance_manager.py create my-instance

# 2. 复制模板配置
cp docs/03-技术解读/openclaw-config-templates/激进模式-零门槛配置.json \
   workspace/lobsters/my-instance/.openclaw/openclaw.json

# 3. 修改配置中的占位符
# - 你的百炼API-Key
# - 你的飞书AppID
# - 你的飞书AppSecret

# 4. 启动实例
python skills/openclaw-manager/scripts/instance_manager.py start my-instance
```

---

### 方法 2：修改现有实例配置

```bash
# 1. 停止实例
python skills/openclaw-manager/scripts/instance_manager.py stop my-instance

# 2. 备份当前配置
cp workspace/lobsters/my-instance/.openclaw/openclaw.json \
   workspace/lobsters/my-instance/.openclaw/openclaw.json.backup

# 3. 应用新配置
# 选择合适的模板，复制内容到 openclaw.json

# 4. 修改占位符

# 5. 启动实例
python skills/openclaw-manager/scripts/instance_manager.py start my-instance
```

---

## 📝 配置占位符说明

每个模板中需要替换的占位符：

### 通用占位符

| 占位符 | 说明 | 获取方式 |
|--------|------|----------|
| `你的百炼API-Key` | 阿里云百炼 API Key | [百炼控制台](https://bailian.console.aliyun.com/) |
| `你的飞书AppID` | 飞书应用 ID | 飞书开发者后台 → 凭证与基础信息 |
| `你的飞书AppSecret` | 飞书应用 Secret | 飞书开发者后台 → 凭证与基础信息 |

### 安全模式额外占位符

| 占位符 | 说明 | 生成方式 |
|--------|------|----------|
| `生成一个随机32字符的token` | 访问 Token | `openssl rand -hex 32` |
| 环境变量 `BAILIAN_API_KEY` | API Key | 设置环境变量而非写在配置中 |
| 环境变量 `FEISHU_APP_SECRET` | App Secret | 设置环境变量而非写在配置中 |

---

## 🎯 模式选择建议

```
场景判断：

你是在学习 OpenClaw 吗？
└─ 是 → 【激进模式】（快速上手，减少困惑）

你是小团队（5-20人）使用吗？
└─ 是 → 【混合模式】（方便协作，基本安全）

你需要部署到生产环境吗？
└─ 是 → 【安全模式】（完整保护，审计日志）
```

---

## 🔄 模式迁移

### 从激进模式 → 混合模式

**修改点**：
1. `gateway.auth.mode` 从 `"none"` 改为 `"token"`
2. 添加 `gateway.auth.token`
3. `channels.feishu.groupPolicy` 从 `"open"` 改为 `"pairing"`

### 从混合模式 → 安全模式

**修改点**：
1. `gateway.bind` 从 `"lan"` 改为 `"loopback"`
2. `gateway.controlUi.dangerouslyDisableDeviceAuth` 从 `true` 改为 `false`
3. `channels.feishu.dmPolicy` 从 `"open"` 改为 `"pairing"`
4. `commands.native` 和 `nativeSkills` 从 `"auto"` 改为 `"off"`
5. 使用密钥引用替代明文 API Key

---

## 📚 相关文档

- [OpenClaw 配置文件完全解读](../openclaw配置文件完全解读.md) - 详细的字段说明
- [飞书配对解决方案](../../02-问题解决/飞书配对-真正的解决方案.md) - 配对问题排查

---

**最后更新**: 2026-03-12
