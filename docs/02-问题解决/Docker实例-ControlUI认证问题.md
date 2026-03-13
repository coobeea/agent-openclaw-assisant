# Docker 实例 Control UI 认证问题

## 问题现象

Docker 中运行的 OpenClaw 实例，访问 Control UI 时出现：
- "gateway token mismatch"
- "too many failed authentication attempts"  
- "control ui requires device identity (use HTTPS or localhost secure context)"

## 根本原因

Docker 容器网络特性导致：
1. 宿主机浏览器访问容器时，容器看到的客户端 IP 是 Docker 网关（如 `172.24.0.1`），而不是 `127.0.0.1`
2. Control UI 要求"安全上下文"（HTTPS 或 localhost）才能进行设备身份认证
3. 从容器角度，`172.24.0.1` 不是 localhost，所以认证失败

## 解决方案

在 Docker 实例的 `openclaw.json` 中添加以下配置：

```json
{
  "gateway": {
    "mode": "local",
    "bind": "custom",
    "customBindHost": "0.0.0.0",
    "controlUi": {
      "allowedOrigins": [
        "http://localhost:18900",
        "http://127.0.0.1:18900"
      ],
      "dangerouslyDisableDeviceAuth": true
    },
    "auth": {
      "mode": "token",
      "token": "your-token-here"
    }
  }
}
```

关键配置说明：
- `bind: "custom"` + `customBindHost: "0.0.0.0"`: 让 Gateway 监听所有网络接口，否则只监听容器内 127.0.0.1
- `dangerouslyDisableDeviceAuth: true`: 跳过设备身份认证（Docker 环境必须）

## 安全提示

`dangerouslyDisableDeviceAuth: true` 会禁用设备认证检查，只应在以下场景使用：
- 本地开发环境
- Docker 容器内部署
- 已有其他网络层安全保护

生产环境建议使用 HTTPS（Tailscale Serve）或其他安全措施。

## 验证方法

配置修改后重启容器：
```bash
docker restart <container-name>
```

然后访问：`http://127.0.0.1:18900/#token=<your-token>`

## 相关文件

- 配置文件位置：`workspace/lobsters/<instance-name>/.openclaw/openclaw.json`
- 源码参考：`workspace/source/openclaw/docs/gateway/protocol.md`
