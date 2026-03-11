# 主机模式部署

## 概述

主机模式直接在服务器上运行 OpenClaw，使用 Systemd 管理服务。

## 部署步骤

### 1. 使用部署脚本

```bash
bash scripts/deploy_host.sh openclaw-prod-01
```

### 2. 手动部署

#### 生成服务文件

```bash
# 从模板生成
cp templates/systemd/openclaw@.service /etc/systemd/system/openclaw@openclaw-prod-01.service

# 编辑配置
# 设置工作空间路径
```

#### 启用服务

```bash
sudo systemctl daemon-reload
sudo systemctl enable openclaw@openclaw-prod-01
sudo systemctl start openclaw@openclaw-prod-01
```

#### 查看状态

```bash
sudo systemctl status openclaw@openclaw-prod-01
```

---

## Systemd 服务配置

### 服务模板

```ini
[Unit]
Description=OpenClaw Instance %i
After=network.target

[Service]
Type=simple
User=openclaw
WorkingDirectory=/path/to/workspace/%i
ExecStart=/usr/local/bin/openclaw start --workspace /path/to/workspace/%i
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### 日志查看

```bash
# 查看服务日志
sudo journalctl -u openclaw@openclaw-prod-01 -f

# 查看最近100行
sudo journalctl -u openclaw@openclaw-prod-01 -n 100
```

---

## 自动重启配置

### 配置重启策略

```ini
[Service]
Restart=always
RestartSec=10
StartLimitBurst=5
StartLimitInterval=300
```

### 配置健康检查

使用 `health_check.py` 监控实例状态。

---

## 故障排查

### 服务启动失败

```bash
# 查看详细错误
sudo systemctl status openclaw@openclaw-prod-01
sudo journalctl -u openclaw@openclaw-prod-01 -n 50
```

### 权限问题

```bash
# 检查用户权限
sudo -u openclaw whoami

# 检查工作空间权限
ls -ld /path/to/workspace/openclaw-prod-01
```
