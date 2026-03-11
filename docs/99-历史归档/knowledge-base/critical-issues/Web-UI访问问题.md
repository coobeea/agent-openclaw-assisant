# 🌐 Web UI 访问问题 - 高频问题

> **严重程度**: ⭐⭐⭐⭐  
> **发生频率**: 几乎每个新用户都会遇到  
> **症状**: 显示 "device identity required"  
> **来源**: agent-openclaws 项目历史经验

---

## 🚨 核心问题

**URL 格式错误**: 用了 `?token=` 而不是 `#token=`

### 错误示例（❌ 绝对不要这样！）

```
❌ http://127.0.0.1:19410/?token=abc123def456...
   ↑ 用了 ? (Query Parameter)
```

### 正确示例（✅ 必须这样！）

```
✅ http://127.0.0.1:19410/#token=abc123def456...
   ↑ 用了 # (Hash Fragment)
```

---

## 🔍 问题详解

### 为什么必须用 `#token=`?

| 特性 | `?token=` (Query) | `#token=` (Hash) |
|------|------------------|------------------|
| **刷新行为** | ❌ Token 丢失 | ✅ Token 保留 |
| **发送到服务器** | ❌ 是（安全风险） | ✅ 否（更安全） |
| **浏览器处理** | 作为请求参数 | 作为客户端状态 |
| **OpenClaw 支持** | ❌ 不支持 | ✅ 支持 |

### 技术原理

**Query Parameter (`?token=`)**:
```
用户访问: http://127.0.0.1:19410/?token=abc123
           ↓
发送到服务器: GET /?token=abc123
           ↓
刷新页面时重新请求
           ↓
OpenClaw 收到新请求，没有 device identity
           ↓
显示错误: "device identity required"
```

**Hash Fragment (`#token=`)**:
```
用户访问: http://127.0.0.1:19410/#token=abc123
           ↓
发送到服务器: GET / (不包含 #token=)
           ↓
JavaScript 读取 #token= 进行认证
           ↓
刷新页面时 Hash 保留
           ↓
✅ 认证成功，正常工作
```

---

## 🎯 完整访问流程

### 1. 获取访问地址

**方法 A: 创建时自动显示（推荐）**

```bash
python3 skills/openclaw-manager/scripts/instance_manager.py create ...

# 输出会包含：
✅ Web UI 访问地址：
   http://127.0.0.1:19410/#token=abc123def456...
   
   ⚠️ 注意：必须用 # 不是 ?
```

**方法 B: 查询现有龙虾**

```bash
python3 skills/openclaw-manager/scripts/instance_manager.py status <instance-id>

# 输出会包含完整访问地址
```

**方法 C: 手动构建**

```bash
# 1. 查看端口
PORT=$(cat test-workspace/data/agents.jsonl | jq -r '.gateway_port')

# 2. 查看 Token
TOKEN=$(cat test-workspace/lobsters/*/openclaw/openclaw.json | jq -r '.gateway.auth.token')

# 3. 构建 URL
echo "http://127.0.0.1:${PORT}/#token=${TOKEN}"
```

### 2. 访问 Web UI

1. **复制完整 URL**（确保包含 `#token=`）
2. **粘贴到浏览器**
3. **回车访问**

### 3. 验证成功

如果看到：
- ✅ OpenClaw 控制面板
- ✅ 可以发送消息
- ✅ 可以查看设置

如果看到：
- ❌ "device identity required"
- ❌ 白屏
- ❌ 无响应

→ 检查 URL 格式，确保用了 `#token=`

---

## 🔧 常见问题和解决

### 问题 1: 刷新后显示错误

**症状**: 第一次访问正常，刷新后显示 "device identity required"

**原因**: 用了 `?token=`

**解决**:
1. 重新复制正确的 URL（用 `#token=`）
2. 粘贴到浏览器
3. 建议收藏该 URL

### 问题 2: Docker 模式用 127.0.0.1 不行

**症状**: URL 格式正确但无法访问

**原因**: Docker 网络隔离

**解决**:
```
❌ http://127.0.0.1:19410/#token=abc123
✅ http://localhost:19410/#token=abc123  (Docker 推荐)
```

### 问题 3: 端口号不确定

**解决**:
```bash
# 查看所有龙虾的端口
python3 skills/openclaw-manager/scripts/instance_manager.py list

# 输出会显示每个龙虾的端口
```

### 问题 4: Token 不知道在哪

**解决**:
```bash
# 方法 1: 使用工具（推荐）
python3 skills/openclaw-manager/scripts/instance_manager.py status <instance-id>

# 方法 2: 直接读取配置
cat test-workspace/lobsters/*/openclaw/openclaw.json | jq -r '.gateway.auth.token'
```

---

## 🛡️ 安全说明

### Token 的作用

- 用于身份认证的密钥
- 每个龙虾有唯一的 Token
- 类似密码，需要妥善保管

### 安全建议

1. ✅ 不要在公开场合分享完整的 URL（包含 Token）
2. ✅ 使用 `#token=` 而不是 `?token=`（更安全）
3. ✅ 定期更换 Token（如果怀疑泄露）
4. ✅ 使用 HTTPS（生产环境）

### Token 泄露风险

**`?token=` 的风险**:
- ❌ Token 会出现在服务器日志中
- ❌ Token 会出现在代理服务器日志中
- ❌ Token 会出现在浏览器历史中
- ❌ 可能被第三方脚本读取

**`#token=` 的优势**:
- ✅ Token 不会发送到服务器
- ✅ Token 不会出现在服务器日志中
- ✅ Token 只在浏览器中处理
- ✅ 更难被第三方脚本读取

---

## 📋 检查清单

访问 Web UI 前，确认：

- [ ] ✅ URL 使用 `#token=` 不是 `?token=`
- [ ] ✅ 端口号正确（与龙虾配置一致）
- [ ] ✅ Token 正确（完整复制，没有截断）
- [ ] ✅ 龙虾正在运行（检查进程状态）
- [ ] ✅ 防火墙允许该端口（如果有防火墙）

Docker 模式额外检查：

- [ ] ✅ 使用 `localhost` 而不是 `127.0.0.1`
- [ ] ✅ Docker 容器正在运行
- [ ] ✅ 端口映射正确

---

## 🔍 调试方法

### 检查龙虾是否运行

```bash
# 方法 1: 使用工具
python3 skills/openclaw-manager/scripts/instance_manager.py status <instance-id>

# 方法 2: 检查进程
ps aux | grep openclaw | grep <port>

# 方法 3: 检查端口
lsof -i :<port>
```

### 检查健康状态

```bash
# 访问健康检查端点（不需要 Token）
curl -s http://localhost:<port>/health

# 应该返回:
# {"ok":true,"version":"2026.3.8"}
```

### 检查配置

```bash
# 检查认证模式
cat test-workspace/lobsters/*/openclaw/openclaw.json | jq '.gateway.auth.mode'
# 应该是: "token"

# 检查是否禁用了 device auth
cat test-workspace/lobsters/*/openclaw/openclaw.json | jq '.gateway.controlUi.dangerouslyDisableDeviceAuth'
# 应该是: true
```

---

## 🎓 最佳实践

### 创建工具输出格式

在创建龙虾工具中，应该输出：

```python
print("\n✅ 龙虾创建成功！")
print(f"\n🌐 Web UI 访问地址：")
print(f"   http://127.0.0.1:{port}/#token={token}")
print(f"\n⚠️  重要提示：")
print(f"   - 必须用 # 不是 ? (Hash Fragment)")
print(f"   - 复制完整 URL 到浏览器")
print(f"   - 建议收藏该地址")
```

### 文档中的示例

在文档中，应该明确标注：

```markdown
## 访问 Web UI

**正确格式** (用 #):
http://127.0.0.1:19410/#token=abc123...

**错误格式** (用 ?):
http://127.0.0.1:19410/?token=abc123...
```

---

## 📊 故障排查流程图

```
访问 Web UI 失败
    ↓
显示 "device identity required"?
    ↓ 是
URL 用了 # 还是 ?
    ↓ 用了 ?
【解决】改为 # → ✅ 成功
    ↓ 用了 #
龙虾是否运行?
    ↓ 否
【解决】启动龙虾 → ✅ 成功
    ↓ 是
Token 是否正确?
    ↓ 否
【解决】重新获取正确的 Token → ✅ 成功
    ↓ 是
端口是否正确?
    ↓ 否
【解决】检查并使用正确的端口 → ✅ 成功
    ↓ 是
【升级】检查高级配置（认证模式、防火墙等）
```

---

## 🎉 总结

### 核心原则

> **必须用 `#token=` 不是 `?token=`！**

### 三步访问法

1. ✅ 获取完整 URL（包含 `#token=`）
2. ✅ 粘贴到浏览器
3. ✅ 验证访问成功

### 预防措施

1. ✅ 在工具输出中明确标注格式
2. ✅ 在文档中用对比示例
3. ✅ 在错误提示中给出正确格式
4. ✅ 在测试中自动验证 URL 格式

---

**来源**: agent-openclaws 项目，几乎每个用户都遇到的问题  
**更新**: 2026-03-10  
**重要程度**: ⭐⭐⭐⭐ 高频问题！
