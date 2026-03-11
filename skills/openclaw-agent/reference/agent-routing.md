# 智能体路由配置

## 路由概念

路由决定了消息如何从渠道分发到智能体。

## 路由模式

### 模式1: 一对一

```
渠道: 飞书
  ↓
智能体: main
```

最简单的配置，一个渠道对应一个智能体。

### 模式2: 多对一

```
渠道: 飞书、QQ、企业微信
  ↓
智能体: main
```

多个渠道使用同一个智能体。

### 模式3: 一对多

```
渠道: 飞书
  ↓
智能体: customer-service, tech-support
```

一个渠道根据规则分发到不同智能体。

### 模式4: 多对多

```
飞书 → customer-service
QQ → customer-service
企业微信 → tech-support
钉钉 → sales
```

复杂的路由配置，每个渠道指定智能体。

## 路由规则

### 按关键词路由

```yaml
routing:
  - keywords: ["技术", "bug", "报错"]
    agent: tech-support
  - keywords: ["购买", "价格", "优惠"]
    agent: sales
  - default: customer-service
```

### 按用户路由

```yaml
routing:
  - user_group: vip
    agent: vip-service
  - default: customer-service
```
