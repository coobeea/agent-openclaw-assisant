# 实例管理指南

## 实例生命周期

```
创建 → 配置 → 启动 → 运行 → 停止 → 删除
```

## 创建实例

### 使用管理工具

```bash
python scripts/instance_manager.py create openclaw-prod-01
```

### 工作流程

1. **验证实例 ID** - 检查命名规范
2. **检查重复** - 确保实例不存在
3. **创建工作空间** - 创建实例目录（路径从配置读取）
4. **初始化 OpenClaw** - 调用 `openclaw init --workspace <path>`
5. **生成配置** - 从模板生成初始配置（如需要）
6. **返回结果** - 输出实例信息

### 命名规范

**标准格式**: `openclaw-{env}-{num}`
- `openclaw-prod-01` - 生产实例
- `openclaw-dev-01` - 开发实例
- `openclaw-test-01` - 测试实例

**简化格式**: `openclaw-{name}`
- `openclaw-demo` - 演示实例
- `openclaw-personal` - 个人实例

---

## 启动实例

### 使用管理工具

```bash
python scripts/instance_manager.py start openclaw-prod-01
```

### 启动方式

根据配置自动选择：
- **前台运行**: 开发/测试环境
- **后台运行**: 生产环境
- **Systemd 服务**: 如已配置（需 openclaw-deploy）

---

## 停止实例

### 优雅停止

```bash
python scripts/instance_manager.py stop openclaw-prod-01
```

发送 SIGTERM 信号，等待进程退出。

### 强制停止

```bash
python scripts/instance_manager.py stop openclaw-prod-01 --force
```

发送 SIGKILL 信号，立即终止。

---

## 重启实例

```bash
python scripts/instance_manager.py restart openclaw-prod-01
```

等同于：stop → start

---

## 查看状态

### 单个实例

```bash
python scripts/instance_manager.py status openclaw-prod-01
```

**输出信息**:
- 实例ID
- 运行状态（运行中/已停止）
- 进程PID
- 端口号
- 启动时间
- CPU/内存使用

### 所有实例

```bash
python scripts/instance_manager.py list
```

**输出格式**:
```
实例列表:
  • openclaw-prod-01    [运行中]  端口:3000  运行:2小时
  • openclaw-dev-01     [已停止]  -          -
  • openclaw-test-01    [运行中]  端口:3001  运行:30分钟
```

---

## 查看日志

### 实时日志

```bash
python scripts/instance_manager.py logs openclaw-prod-01 --follow
```

### 最近日志

```bash
python scripts/instance_manager.py logs openclaw-prod-01 --lines 100
```

---

## 删除实例

### 删除流程

```bash
python scripts/instance_manager.py delete openclaw-prod-01
```

**确认提示**:
```
警告: 即将删除实例 openclaw-prod-01
      工作空间: /path/to/workspace/openclaw-prod-01
      这将删除所有数据，无法恢复！
      
是否继续? [yes/no]:
```

### 强制删除（无确认）

```bash
python scripts/instance_manager.py delete openclaw-prod-01 --force
```

---

## 实例配置

### 配置文件位置

实例配置由 OpenClaw 管理，位置取决于 OpenClaw 的实现。

### 查看配置

```bash
# 使用 OpenClaw 命令
openclaw config --workspace <instance-path> list

# 获取特定配置
openclaw config --workspace <instance-path> get key
```

### 修改配置

```bash
# 使用 OpenClaw 命令
openclaw config --workspace <instance-path> set key=value
```

**注意**: 优先使用 OpenClaw 命令，不直接修改配置文件。

---

## 多实例管理

### 批量操作

```bash
# 启动所有生产实例
for instance in $(python scripts/instance_manager.py list --filter prod); do
    python scripts/instance_manager.py start $instance
done

# 查看所有实例状态
python scripts/instance_manager.py list --verbose
```

### 端口管理

实例会自动分配端口，避免冲突。

**默认端口范围**: 3000-3100（在 global.yaml 配置）

---

## 故障排查

### 实例启动失败

1. 检查 OpenClaw 是否安装: `openclaw --version`
2. 检查端口是否被占用: `lsof -i :3000`
3. 查看详细日志: `python scripts/instance_manager.py logs <id>`

### 实例无响应

1. 检查进程: `python scripts/instance_manager.py status <id>`
2. 重启实例: `python scripts/instance_manager.py restart <id>`
3. 查看系统资源: `top` 或 `htop`

### 工作空间路径错误

1. 检查配置: `cat shared/configs/global.yaml`
2. 确认路径存在: `ls -la <workspace-root>`
3. 检查权限: `ls -ld <workspace-root>`
