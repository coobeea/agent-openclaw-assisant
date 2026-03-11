# 共享配置说明

## 配置文件

### global.yaml
全局配置文件，影响所有 OpenClaw 实例。

**使用方法:**
```bash
# 1. 复制模板文件
cp global.yaml.template global.yaml

# 2. 根据实际情况修改配置
# 编辑 global.yaml

# 3. 验证配置（使用技能包提供的工具）
python ../utils/validate_config.py global.yaml
```

**主要配置项:**
- `workspace_root`: 工作空间路径
- `openclaw.version`: OpenClaw 版本
- `instance.name_prefix`: 实例命名前缀
- `models.default_model`: 默认 AI 模型

### defaults.yaml
默认值配置，作为实例配置的后备值。

## 配置优先级

```
智能体配置 (workspace/{instance}/config/agents.yaml)
    ↓
实例配置 (workspace/{instance}/config/openclaw.yaml)
    ↓
默认配置 (shared/configs/defaults.yaml)
    ↓
全局配置 (shared/configs/global.yaml)
```

## 安全注意事项

⚠️ **不要在这些配置文件中存储敏感信息！**

敏感信息应该存储在：
- 实例的 `.env` 文件（workspace/{instance}/config/.env）
- 使用凭证加密工具加密后存储

## 配置示例

### 最小化配置
```yaml
global:
  workspace_root: "./workspace"
openclaw:
  version: "latest"
```

### 生产环境配置
```yaml
global:
  project_name: "my-openclaw-fleet"
  workspace_root: "/data/openclaw/workspace"
  log_level: "warn"

openclaw:
  version: "2026.3.8"
  install_method: "npm"

instance:
  name_prefix: "openclaw"
  auto_start: true
  auto_restart: true

monitoring:
  enabled: true
  log_retention_days: 30

backup:
  enabled: true
  interval: 24
  retention_count: 7
```

## 配置修改后的生效

- **全局配置**: 需要重启所有实例
- **实例配置**: 需要重启对应实例
- **智能体配置**: 部分支持热更新（取决于OpenClaw版本）

---

**注意**: 首次使用请复制 `global.yaml.template` 为 `global.yaml` 并根据实际情况修改。
