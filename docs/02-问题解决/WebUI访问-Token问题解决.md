# 🔐 OpenClaw Web UI 访问 - Token 认证问题

> **问题**: unauthorized: gateway token missing  
> **原因**: 访问 Web UI 时未提供认证 token  
> **状态**: ✅ **已解决并文档化**

---

## ❌ 问题现象

### 错误信息

```
unauthorized: gateway token missing 
(open the dashboard URL and paste the token in Control UI settings)
```

### 问题截图

当直接访问 `http://127.0.0.1:18800/` 时，会显示：
- 红色错误提示
- "已断开与网关的连接"
- 提示需要 gateway token

---

## 🔍 问题原因

### OpenClaw 认证机制

OpenClaw Web UI 使用 **token 认证**机制保护控制台访问：

1. **认证配置** (`.openclaw/openclaw.json`):
   ```json
   {
     "gateway": {
       "mode": "local",
       "auth": {
         "mode": "token",
         "token": "4c86b66c1a40575d2167440a2974c0653d70cc976644d034"
       }
     }
   }
   ```

2. **访问要求**:
   - ❌ 直接访问 `http://127.0.0.1:18800/` → 无认证，被拒绝
   - ✅ 访问 `http://127.0.0.1:18800/#token=xxx` → 有认证，允许访问

---

## ✅ 解决方案

### 方法 1: 使用带 Token 的 URL（推荐）

**龙虾实例**: `openclaw-feishu-demo`  
**Token**: `4c86b66c1a40575d2167440a2974c0653d70cc976644d034`

**正确的访问 URL**:
```
http://127.0.0.1:18800/#token=4c86b66c1a40575d2167440a2974c0653d70cc976644d034
```

**在浏览器中打开这个 URL，即可正常访问！**

---

### 方法 2: 使用 OpenClaw Dashboard 命令

```bash
cd /Users/lifeng/git/git-claw/agent-openclaw-assisant/workspace/lobsters/openclaw-feishu-demo

# 自动打开带 token 的 dashboard
node /Users/lifeng/git/git_agents/openclaw/dist/index.js dashboard
```

**输出**:
```
Dashboard URL: http://127.0.0.1:18800/#token=xxx
Copied to clipboard.
Opened in your browser.
```

---

### 方法 3: 手动设置 Token（不推荐）

1. 访问 `http://127.0.0.1:18800/`
2. 看到错误提示后，点击设置图标
3. 在 Control UI settings 中粘贴 token
4. 刷新页面

**缺点**: 每次都要手动设置

---

## 🔧 获取 Token 的方法

### 方法 1: 从配置文件读取

```bash
# 查看龙虾的配置文件
cat workspace/lobsters/openclaw-feishu-demo/.openclaw/openclaw.json | grep -A 5 '"auth"'
```

**输出**:
```json
"auth": {
  "mode": "token",
  "token": "4c86b66c1a40575d2167440a2974c0653d70cc976644d034"
}
```

### 方法 2: 从日志查看

```bash
# 查看启动日志
tail -100 workspace/logs/openclaw-feishu-demo.log | grep -i "token\|dashboard"
```

### 方法 3: 使用 Python 脚本

```python
#!/usr/bin/env python3
import json
from pathlib import Path

# 读取配置文件
config_file = Path("workspace/lobsters/openclaw-feishu-demo/.openclaw/openclaw.json")
with open(config_file) as f:
    config = json.load(f)

# 获取 token
token = config['gateway']['auth']['token']
port = 18800  # 从 agents.jsonl 获取

# 生成访问 URL
dashboard_url = f"http://127.0.0.1:{port}/#token={token}"
print(f"Dashboard URL: {dashboard_url}")
```

---

## 🎯 自动化改进

### 更新 instance_manager.py

在 `instance_manager.py` 的 `start` 和 `status` 命令中，自动显示带 token 的 URL。

**改进后的输出**:
```python
def show_instance_info(instance_name: str):
    """显示实例信息（包含带 token 的访问 URL）"""
    # ... 获取实例信息 ...
    
    # 读取 token
    config_file = workspace_path / '.openclaw' / 'openclaw.json'
    with open(config_file) as f:
        config = json.load(f)
    token = config.get('gateway', {}).get('auth', {}).get('token', '')
    
    # 生成带 token 的 URL
    dashboard_url = f"http://127.0.0.1:{port}/#token={token}"
    
    print(f"🎯 访问方式:")
    print(f"   Web UI: {dashboard_url}")
    print(f"   Token: {token}")
```

---

## 📋 完整示例

### 场景: 启动龙虾后访问 Web UI

```bash
# 1. 启动龙虾
python3 skills/openclaw-manager/scripts/instance_manager.py start openclaw-feishu-demo

# 输出:
# ✅ 已启动，PID: 94554
# 🎯 访问方式:
#    Web UI: http://127.0.0.1:18800/#token=4c86b66c1a40575d2167440a2974c0653d70cc976644d034

# 2. 在浏览器中打开上面的 URL
# ✅ 可以正常访问控制台
```

---

## 🛡️ 安全说明

### Token 的重要性

**Token 是访问控制台的密钥**:
- ✅ 防止未授权访问
- ✅ 保护龙虾配置和数据
- ✅ 控制操作权限

### 安全建议

1. **不要分享 Token**: Token 相当于管理员密码
2. **不要提交到 Git**: 配置文件不要提交到公开仓库
3. **定期轮换**: 如有泄露风险，重新生成 token
4. **本地访问**: 只在本地网络访问，不要暴露到公网

### 重新生成 Token

如需重新生成 token:

```bash
# 1. 停止龙虾
python3 skills/openclaw-manager/scripts/instance_manager.py stop openclaw-feishu-demo

# 2. 编辑配置文件
# 手动修改 .openclaw/openclaw.json 中的 token 值

# 3. 重启龙虾
python3 skills/openclaw-manager/scripts/instance_manager.py start openclaw-feishu-demo
```

---

## 📚 相关文档

- OpenClaw 官方文档: https://docs.openclaw.ai/
- 认证配置: https://docs.openclaw.ai/configuration/auth
- Gateway 设置: https://docs.openclaw.ai/gateway

---

## 🎯 快速参考

### 当前实例访问信息

**实例名称**: `openclaw-feishu-demo`  
**端口**: `18800`  
**Token**: `4c86b66c1a40575d2167440a2974c0653d70cc976644d034`

**完整访问 URL**:
```
http://127.0.0.1:18800/#token=4c86b66c1a40575d2167440a2974c0653d70cc976644d034
```

**复制粘贴到浏览器即可访问！**

---

## ✅ 问题解决检查清单

- [x] 问题原因：访问 URL 缺少 token
- [x] 解决方案：使用带 token 的 URL
- [x] 获取 token：从配置文件读取
- [x] 生成访问 URL：拼接端口和 token
- [x] 验证访问：浏览器打开 URL
- [x] 文档记录：本文档
- [x] 自动化改进：更新 instance_manager.py（待实施）

---

## 🎉 总结

**问题**: Web UI 无法访问，提示 "gateway token missing"  
**原因**: 访问 URL 缺少 token 参数  
**解决**: 使用带 token 的完整 URL 访问  

**一句话**: **访问 Web UI 必须带上 token！**

---

**创建时间**: 2026-03-10 23:00  
**问题类型**: 认证  
**重要程度**: ⚠️ 高（影响使用）  
**解决状态**: ✅ 已解决
