# 工作空间管理

## 概念说明

**工作空间（Workspace）** 是 OpenClaw 实例的数据存储目录。

### 我们的职责

✅ **我们管理**:
- 工作空间的统一位置（可配置）
- 为每个实例创建顶层目录
- 将工作空间路径传递给 OpenClaw

❌ **我们不管理**:
- 实例内部的目录结构（由 OpenClaw 决定）
- 实例内部的文件组织（由 OpenClaw 管理）
- 实例内部的数据格式（由 OpenClaw 定义）

---

## 路径配置

### 配置文件

```yaml
# shared/configs/global.yaml
global:
  workspace_root: "./workspace"
```

### 支持的路径格式

| 格式 | 示例 | 适用场景 |
|------|------|---------|
| 相对路径 | `./workspace` | 开发环境，数据跟随项目 |
| 绝对路径 | `/data/openclaw` | 生产环境，数据独立存储 |
| 用户目录 | `~/openclaw-data` | 个人使用，存储在主目录 |

---

## 工作空间结构

```
{workspace_root}/
├── openclaw-prod-01/          # 实例工作空间
│   └── (由 OpenClaw 管理)     # 内部结构不预定义
│
├── openclaw-dev-01/
│   └── (由 OpenClaw 管理)
│
└── .keyfile                   # 加密密钥（由 crypto.py 生成）
```

---

## 创建工作空间

### 代码示例

```python
from shared.utils.common import OpenClawUtils

utils = OpenClawUtils()

# 创建实例工作空间（只创建顶层目录）
instance_path = utils.ensure_workspace_exists("openclaw-prod-01")

# 调用 OpenClaw 初始化（OpenClaw 创建内部结构）
utils.run_command([
    "openclaw", "init",
    "--workspace", str(instance_path),
    "--name", "openclaw-prod-01"
])
```

### 命令行示例

```bash
# 1. 从配置读取路径
workspace_root=$(python -c "from shared.utils.common import load_global_config; print(load_global_config()['global']['workspace_root'])")

# 2. 创建实例目录
mkdir -p "$workspace_root/openclaw-prod-01"

# 3. 初始化 OpenClaw
openclaw init \
  --workspace "$workspace_root/openclaw-prod-01" \
  --name "openclaw-prod-01"
```

---

## 访问工作空间

### 获取实例路径

```python
from shared.utils.common import OpenClawUtils

utils = OpenClawUtils()
instance_path = utils.get_instance_path("openclaw-prod-01")
print(f"实例工作空间: {instance_path}")
```

### 列出所有实例

```python
instances = utils.list_instances()
for instance in instances:
    print(f"- {instance}")
```

### 检查实例存在

```python
if utils.instance_exists("openclaw-prod-01"):
    print("实例存在")
```

---

## 工作空间迁移

### 更改工作空间路径

如果需要迁移到新位置：

```bash
# 1. 停止所有实例
python scripts/instance_manager.py stop --all

# 2. 移动数据
mv ./workspace /new/location/

# 3. 更新配置
# 编辑 shared/configs/global.yaml
# workspace_root: "/new/location"

# 4. 重启实例
python scripts/instance_manager.py start --all
```

---

## 备份与恢复

### 备份单个实例

```bash
workspace_root="./workspace"  # 从配置读取
instance_id="openclaw-prod-01"

tar -czf "${instance_id}-backup-$(date +%Y%m%d).tar.gz" \
  -C "$workspace_root" "$instance_id"
```

### 恢复实例

```bash
tar -xzf openclaw-prod-01-backup-20260310.tar.gz \
  -C "$workspace_root"
```

### 备份所有实例

```bash
tar -czf openclaw-all-backup-$(date +%Y%m%d).tar.gz \
  "$workspace_root"
```

---

## 清理工作空间

### 清理测试实例

```bash
python scripts/instance_manager.py delete openclaw-test-*
```

### 清理日志（如果 OpenClaw 支持）

```bash
# 使用 OpenClaw 命令
openclaw logs --workspace <instance-path> clean --days 30
```

### 查看空间使用

```bash
du -sh $workspace_root/*
```

---

## 最佳实践

### 开发环境

```yaml
workspace_root: "./workspace"
```

- 数据随项目，便于管理
- 切换项目时数据独立

### 生产环境

```yaml
workspace_root: "/data/openclaw/instances"
```

- 数据独立存储
- 便于大容量磁盘挂载
- 方便备份和监控

### 权限设置

```bash
# 工作空间权限
chmod 700 $workspace_root

# 实例目录权限
chmod 700 $workspace_root/openclaw-*
```

---

## 注意事项

### ⚠️ 不要做的事

1. ❌ 不要假设实例内部有特定目录
2. ❌ 不要直接修改实例内部文件
3. ❌ 不要在代码中硬编码工作空间路径
4. ❌ 不要将 workspace/ 提交到 Git

### ✅ 应该做的事

1. ✅ 从配置文件读取工作空间路径
2. ✅ 只创建实例的顶层目录
3. ✅ 使用 OpenClaw 命令操作实例
4. ✅ 定期备份工作空间
5. ✅ 监控磁盘空间使用
