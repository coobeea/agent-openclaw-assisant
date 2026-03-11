# 问题：飞书渠道配置未写入 openclaw.json（WebSocket 模式未生效）

## 现象

执行 `channel_manager.py add` 添加飞书渠道后，凭证仅保存到 `workspace/data/channels.jsonl`，
**没有写入实例的 `openclaw.json`**，导致 OpenClaw 启动时飞书 WebSocket 连接无法建立。

## 根本原因

`skills/openclaw-channel/scripts/channel_manager.py` 的 `add` 命令只将渠道信息追加到：
```
workspace/data/channels.jsonl
```

但 OpenClaw 实际读取的飞书配置在实例的：
```
workspace/lobsters/<实例名>/.openclaw/openclaw.json
```
中的 `channels.feishu` 字段，导致配置不生效。

## 当前临时解法（手动写入）

```python
import json
path = 'workspace/lobsters/openclaw-feishu-longxia/.openclaw/openclaw.json'
with open(path) as f:
    config = json.load(f)
config['channels'] = {
    'feishu': {
        'enabled': True,
        'appId': '<APP_ID>',
        'appSecret': '<APP_SECRET>',
        'connectionMode': 'websocket',   # 默认应使用 ws，无需公网回调
        'dmPolicy': 'pairing',
        'groupPolicy': 'open'
    }
}
with open(path, 'w') as f:
    json.dump(config, f, indent=2, ensure_ascii=False)
```

## 需要修复的地方

**文件**：`skills/openclaw-channel/scripts/channel_manager.py`

**修复目标**：`add` 命令在保存到 `channels.jsonl` 的同时，也将渠道配置写入对应实例的 `openclaw.json`：

```json
{
  "channels": {
    "feishu": {
      "enabled": true,
      "appId": "...",
      "appSecret": "...",
      "connectionMode": "websocket",
      "dmPolicy": "pairing",
      "groupPolicy": "open"
    }
  }
}
```

**注意**：
- `connectionMode` 默认应为 `websocket`（飞书长连接，不需要公网 IP）
- 写入时需要知道 `--instance` 参数（实例名），用于定位 `openclaw.json` 路径
- 当前 `add` 命令没有 `--instance` 参数，需要补充
