# OpenClaw 配置文件完全解读 (openclaw.json)

> 基于源码 Schema 定义的权威解读文档
> 
> **源码文件**: `src/config/zod-schema.ts` 及相关子模块
> 
> **文档版本**: 2026.3.12
> 
> **OpenClaw版本**: 2026.3.11

---

## 📋 目录

1. [配置文件概述](#配置文件概述)
2. [顶层结构](#顶层结构)
3. [核心配置章节](#核心配置章节)
   - [meta - 元数据](#meta---元数据)
   - [models - AI 模型配置](#models---ai-模型配置)
   - [agents - 智能体配置](#agents---智能体配置)
   - [commands - 命令执行配置](#commands---命令执行配置)
   - [gateway - 网关配置](#gateway---网关配置)
   - [channels - 渠道配置](#channels---渠道配置)
   - [plugins - 插件配置](#plugins---插件配置)
   - [bindings - 路由绑定](#bindings---路由绑定)
4. [高级配置](#高级配置)
5. [配置模板文件](#配置模板文件) ⭐ 新增
6. [实战示例](#实战示例)
7. [配置模式对比](#配置模式对比) ⭐ 新增
8. [快速切换配置模式](#快速切换配置模式) ⭐ 新增
9. [常见问题 FAQ](#常见问题-faq) ⭐ 新增
10. [配置验证](#配置验证)
11. [配置最佳实践](#配置最佳实践)

---

## 配置文件概述

### 什么是 openclaw.json？

`openclaw.json` 是 OpenClaw 实例的**核心配置文件**，它定义了：
- 实例使用的 AI 模型
- 智能体（Agent）的行为
- 各种消息渠道（飞书、QQ、企微等）的连接
- 插件和技能的启用状态
- 网关的访问控制
- 路由规则（哪个渠道的消息分配给哪个智能体）

### 文件位置

```
<workspace>/<instance-name>/.openclaw/openclaw.json
```

例如：
```
workspace/lobsters/openclaw-docker-001/.openclaw/openclaw.json
```

### Schema 来源

OpenClaw 使用 **Zod** 库来定义配置的类型和验证规则。主要的 Schema 定义在：
- `src/config/zod-schema.ts` - 主配置结构
- `src/config/zod-schema.agents.ts` - 智能体配置
- `src/config/zod-schema.core.ts` - 模型和核心配置
- `src/config/zod-schema.session.ts` - 命令和会话配置
- `src/config/zod-schema.providers.ts` - 渠道配置

---

## 顶层结构

```typescript
// 来自 src/config/zod-schema.ts, line 206-878
export const OpenClawSchema = z.object({
  $schema: z.string().optional(),          // JSON Schema 引用
  meta: {...}.optional(),                   // 元数据
  env: {...}.optional(),                    // 环境变量
  wizard: {...}.optional(),                 // 向导信息
  diagnostics: {...}.optional(),            // 诊断配置
  logging: {...}.optional(),                // 日志配置
  cli: {...}.optional(),                    // CLI 配置
  update: {...}.optional(),                 // 更新配置
  browser: {...}.optional(),                // 浏览器配置
  ui: {...}.optional(),                     // UI 配置
  secrets: {...}.optional(),                // 密钥管理
  auth: {...}.optional(),                   // 认证配置
  acp: {...}.optional(),                    // ACP 协议
  models: {...}.optional(),                 // ⭐ AI 模型配置
  nodeHost: {...}.optional(),               // Node 主机配置
  agents: {...}.optional(),                 // ⭐ 智能体配置
  tools: {...}.optional(),                  // 工具配置
  bindings: {...}.optional(),               // ⭐ 路由绑定
  broadcast: {...}.optional(),              // 广播配置
  audio: {...}.optional(),                  // 音频配置
  media: {...}.optional(),                  // 媒体配置
  messages: {...}.optional(),               // 消息配置
  commands: {...}.optional(),               // ⭐ 命令配置
  approvals: {...}.optional(),              // 审批配置
  session: {...}.optional(),                // 会话配置
  cron: {...}.optional(),                   // 定时任务
  hooks: {...}.optional(),                  // Webhook 钩子
  web: {...}.optional(),                    // Web 配置
  channels: {...}.optional(),               // ⭐ 渠道配置
  discovery: {...}.optional(),              // 服务发现
  canvasHost: {...}.optional(),             // Canvas 主机
  talk: {...}.optional(),                   // 语音合成
  gateway: {...}.optional(),                // ⭐ 网关配置
  memory: {...}.optional(),                 // 记忆配置
  skills: {...}.optional(),                 // 技能配置
  plugins: {...}.optional(),                // ⭐ 插件配置
}).strict();
```

**⭐ 标记** 表示最常用的核心配置项。

---

## 核心配置章节

### meta - 元数据

**Schema 定义**: `src/config/zod-schema.ts`, line 209-229

```typescript
meta: z.object({
  lastTouchedVersion: z.string().optional(),  // 最后修改时的 OpenClaw 版本
  lastTouchedAt: z.union([                    // 最后修改时间（ISO 8601 格式）
    z.string(),
    z.number().transform((n, ctx) => {
      const d = new Date(n);
      if (Number.isNaN(d.getTime())) {
        ctx.addIssue({ code: z.ZodIssueCode.custom, message: "Invalid timestamp" });
        return z.NEVER;
      }
      return d.toISOString();
    }),
  ]).optional(),
}).strict().optional()
```

#### 字段说明

**`lastTouchedVersion`** (可选)
- **类型**: `string`
- **说明**: 记录最后修改配置时的 OpenClaw 版本号，用于版本兼容性检查
- **示例**: `"2026.3.11"`

**`lastTouchedAt`** (可选)
- **类型**: `string` 或 `number`
- **说明**: 最后修改时间
  - 可以是 ISO 8601 字符串格式：`"2026-03-12T12:47:14.299Z"`
  - 也可以是 Unix 时间戳（毫秒），会自动转换为 ISO 格式
- **示例**: `"2026-03-12T12:47:14.299Z"` 或 `1710248834299`

#### 实际示例

```json
{
  "meta": {
    "lastTouchedVersion": "2026.3.11",
    "lastTouchedAt": "2026-03-12T12:47:14.299Z"
  }
}
```

**用途**：
- OpenClaw 在每次修改配置时自动更新这些字段
- 用于追踪配置变更历史
- 在版本升级时进行兼容性检查和自动迁移

---

### models - AI 模型配置

**Schema 定义**: `src/config/zod-schema.core.ts`, line 254-261

```typescript
ModelsConfigSchema = z.object({
  mode: z.union([z.literal("merge"), z.literal("replace")]).optional(),
  providers: z.record(z.string(), ModelProviderSchema).optional(),
  bedrockDiscovery: BedrockDiscoverySchema,
}).strict().optional()
```

#### 顶层字段

**`mode`** (可选，默认: `"merge"`)
- **类型**: `"merge"` 或 `"replace"`
- **说明**: 模型合并模式
  - `merge`: 将用户定义的模型与内置模型合并
  - `replace`: 完全替换内置模型
- **推荐**: 使用 `merge` 保留内置模型

**`providers`** (可选)
- **类型**: 对象字典 `Record<string, ModelProvider>`
- **说明**: 模型提供商配置，键为提供商 ID（如 `"bailian"`, `"openai"`）
- **默认值**: `{}`

**`bedrockDiscovery`** (可选)
- **类型**: `object`
- **说明**: AWS Bedrock 自动发现配置（用于 AWS Bedrock 用户）

#### ModelProvider Schema

**定义**: `src/config/zod-schema.core.ts`, line 227-240

```typescript
ModelProviderSchema = z.object({
  baseUrl: z.string().min(1),                                    // API 基础地址
  apiKey: SecretInputSchema.optional().register(sensitive),      // API 密钥（敏感信息）
  auth: z.union([                                                 // 认证方式
    z.literal("api-key"),     // API Key 认证
    z.literal("aws-sdk"),     // AWS SDK 认证
    z.literal("oauth"),       // OAuth 认证
    z.literal("token")        // Token 认证
  ]).optional(),
  api: ModelApiSchema.optional(),                                // API 协议类型
  injectNumCtxForOpenAICompat: z.boolean().optional(),          // 是否注入 num_ctx 参数
  headers: z.record(z.string(), SecretInputSchema).optional(),  // 自定义请求头
  authHeader: z.boolean().optional(),                            // 是否使用 Authorization 头
  models: z.array(ModelDefinitionSchema),                        // 模型列表
}).strict()
```

##### ModelProvider 字段说明

**`baseUrl`** ⭐ (必填)
- **类型**: `string`
- **说明**: API 服务的基础 URL
- **示例**: `"https://coding.dashscope.aliyuncs.com/v1"`

**`apiKey`** (可选)
- **类型**: `string` 或 `SecretRef`
- **说明**: API 密钥
  - 可以直接填写字符串（不推荐）
  - 也可以使用密钥引用（推荐，见[密钥管理](#secrets---密钥管理)）
- **示例**: `"sk-sp-xxxxxxxxxxxx"`

**`auth`** (可选，默认: `"api-key"`)
- **类型**: `"api-key"` | `"aws-sdk"` | `"oauth"` | `"token"`
- **说明**: 认证方式
  - `api-key`: 使用 API Key 认证（最常用）
  - `aws-sdk`: AWS SDK 认证（用于 AWS Bedrock）
  - `oauth`: OAuth 认证
  - `token`: Token 认证

**`api`** (可选)
- **类型**: `ModelApi`
- **说明**: API 协议类型
- **示例**: `"openai-completions"`

**`models`** ⭐ (必填)
- **类型**: `ModelDefinition[]` (数组)
- **说明**: 该提供商支持的模型列表

#### ModelDefinition Schema

**定义**: `src/config/zod-schema.core.ts`, line 204-225

```typescript
ModelDefinitionSchema = z.object({
  id: z.string().min(1),                           // 模型唯一标识
  name: z.string().min(1),                         // 模型显示名称
  api: ModelApiSchema.optional(),                  // 模型使用的 API 协议
  reasoning: z.boolean().optional(),               // 是否为推理模型
  input: z.array(z.union([                         // 支持的输入类型
    z.literal("text"),
    z.literal("image")
  ])).optional(),
  cost: z.object({                                 // 费用配置
    input: z.number().optional(),                  // 输入 token 单价
    output: z.number().optional(),                 // 输出 token 单价
    cacheRead: z.number().optional(),              // 缓存读取单价
    cacheWrite: z.number().optional()              // 缓存写入单价
  }).strict().optional(),
  contextWindow: z.number().positive().optional(), // 上下文窗口大小（tokens）
  maxTokens: z.number().positive().optional(),     // 最大输出 tokens
  headers: z.record(z.string(), z.string()).optional(), // 自定义请求头
  compat: ModelCompatSchema,                       // 兼容性配置
}).strict()
```

##### ModelDefinition 字段说明

**`id`** ⭐ (必填)
- **类型**: `string`
- **说明**: 模型的唯一标识符
- **示例**: `"qwen3.5-plus"`, `"gpt-4"`, `"claude-3-opus"`
- **注意**: 智能体引用模型时使用 `provider/id` 格式，如 `"bailian/qwen3.5-plus"`

**`name`** ⭐ (必填)
- **类型**: `string`
- **说明**: 模型的显示名称，用于 UI 展示
- **示例**: `"qwen3.5-plus (推荐)"`, `"GPT-4 Turbo"`

**`reasoning`** (可选，默认: `false`)
- **类型**: `boolean`
- **说明**: 是否为推理模型（如 OpenAI o1）
  - 推理模型会启用特殊处理逻辑
  - 普通对话模型设为 `false`

**`input`** (可选)
- **类型**: 数组，元素为 `"text"` 或 `"image"`
- **说明**: 支持的输入类型
  - `["text"]`: 仅支持文本输入
  - `["text", "image"]`: 支持文本+图片输入（多模态）
- **示例**: `["text", "image"]`

**`cost`** (可选)
- **类型**: `object`
- **说明**: 费用计算配置（用于成本统计）
- **字段**:
  - `input`: 输入 token 单价
  - `output`: 输出 token 单价
  - `cacheRead`: 缓存读取单价
  - `cacheWrite`: 缓存写入单价
- **示例**: 
  ```json
  {
    "input": 0.01,
    "output": 0.03,
    "cacheRead": 0.001,
    "cacheWrite": 0.0125
  }
  ```

**`contextWindow`** (可选)
- **类型**: `number`
- **说明**: 模型的上下文窗口大小（tokens）
- **示例**: `1000000` (100万 tokens), `8192`, `128000`

**`maxTokens`** (可选)
- **类型**: `number`
- **说明**: 模型单次输出的最大 tokens 数
- **示例**: `65536` (6.5万 tokens), `4096`, `8192`

**`compat`** (可选)
- **类型**: `ModelCompat` 对象
- **说明**: 模型兼容性配置，用于处理不同 API 提供商的差异
- **用途**: 大部分情况下无需配置，OpenClaw 会自动处理

#### 实际示例

```json
{
  "models": {
    "providers": {
      "bailian": {
        "baseUrl": "https://coding.dashscope.aliyuncs.com/v1",
        "apiKey": "sk-sp-ff72377d1f29462ca958491ae5ce520b",
        "api": "openai-completions",
        "models": [
          {
            "id": "qwen3.5-plus",
            "name": "qwen3.5-plus (推荐)",
            "reasoning": false,
            "input": ["text", "image"],
            "cost": {
              "input": 0,
              "output": 0,
              "cacheRead": 0,
              "cacheWrite": 0
            },
            "contextWindow": 1000000,
            "maxTokens": 65536
          }
        ]
      }
    }
  }
}
```

**用途**：
- 定义实例可以使用的所有 AI 模型
- 支持多个提供商（OpenAI、Anthropic、阿里百炼等）
- 智能体通过 `provider/model-id` 格式引用模型（如 `bailian/qwen3.5-plus`）

---

### agents - 智能体配置

**Schema 定义**: `src/config/zod-schema.agents.ts`, line 6-12

```typescript
AgentsSchema = z.object({
  defaults: z.lazy(() => AgentDefaultsSchema).optional(),  // 默认智能体配置
  list: z.array(AgentEntrySchema).optional(),               // 智能体列表
}).strict().optional()
```

#### 顶层字段

**`defaults`** (可选)
- **类型**: `AgentDefaults` 对象
- **说明**: 所有智能体的默认配置
  - 智能体未指定的配置项会从这里继承
  - 可以统一设置模型、工作目录、压缩策略等

**`list`** (可选)
- **类型**: `AgentEntry[]` 数组
- **说明**: 智能体实例列表
  - 每个智能体可以覆盖 defaults 中的配置

---

#### AgentDefaults 主要字段

**定义**: `src/config/zod-schema.agent-defaults.ts`

**`model.primary`** (可选)
- **类型**: `string`
- **说明**: 默认使用的主模型
  - 智能体初始使用的模型
  - 用户可以通过 `/model` 指令动态切换到其他模型
- **格式**: `provider/model-id`
- **示例**: `"bailian/qwen3.5-plus"`, `"openai/gpt-4"`

**`models`** (可选) - ⭐ 模型切换池
- **类型**: `Record<string, ModelConfig>` 对象字典
- **说明**: 智能体**可以切换到**的模型列表
  - 键为完整的模型引用（`provider/model-id`）
  - 值为该模型的特定配置
  - **核心机制**: 用户可以在对话中通过 `/model` 指令动态切换模型
  - 只有在这个字典中定义的模型才能被切换到
- **示例**:
  ```json
  {
    "bailian/qwen3.5-plus": {},
    "bailian/kimi-k2.5": {},
    "openai/gpt-4": { "alias": "GPT4" }
  }
  ```

#### 💡 模型切换机制详解

OpenClaw 支持在对话过程中动态切换模型，而不是负载均衡。

**工作原理**：
1. **初始模型**: 智能体启动时使用 `model.primary` 指定的模型
2. **切换指令**: 用户在对话中发送 `/model <模型名>` 指令
3. **切换范围**: 只能切换到 `models` 字典中定义的模型
4. **会话记忆**: 切换后的模型继承之前的对话历史

**使用示例**：

```
用户: 你好
智能体: (使用 qwen3.5-plus) 您好！有什么可以帮您的？

用户: /model gpt-4
智能体: 已切换到模型 openai/gpt-4

用户: 继续之前的话题
智能体: (使用 gpt-4，记得之前的对话) 好的，我们继续...
```

**配置建议**：

```json
{
  "agents": {
    "defaults": {
      "model": {
        "primary": "bailian/qwen3.5-plus"
      },
      "models": {
        // 默认模型（必需）
        "bailian/qwen3.5-plus": {},
        
        // 其他可切换的模型
        "bailian/qwen3-coder-plus": {
          "alias": "coder"
        },
        "bailian/kimi-k2.5": {
          "alias": "kimi"
        },
        "openai/gpt-4": {
          "alias": "gpt4"
        }
      }
    }
  }
}
```

**使用 alias 简化切换**：

有了 `alias` 配置后，用户可以用简短的名字切换模型：
- `/model coder` → 切换到 `bailian/qwen3-coder-plus`
- `/model kimi` → 切换到 `bailian/kimi-k2.5`  
- `/model gpt4` → 切换到 `openai/gpt-4`

**注意事项**：
- ⚠️ `model.primary` 必须在 `models` 字典中存在
- ⚠️ 未在 `models` 中定义的模型无法被切换到
- 💡 切换模型会消耗额外的 API 调用（新模型需要重新处理上下文）

**`workspace`** (可选)
- **类型**: `string`
- **说明**: 智能体的工作目录路径
  - 智能体执行命令和技能时的工作目录
  - 通常指向实例的 workspace 路径
- **示例**: `"/Users/lifeng/git/agent-openclaw/workspace/lobsters/instance-001"`

**`compaction.mode`** (可选，默认: `"safeguard"`)
- **类型**: `"off"` | `"safeguard"` | `"auto"`
- **说明**: 上下文压缩模式
  - `off`: 关闭自动压缩
  - `safeguard`: 保守压缩（推荐）
  - `auto`: 自动压缩
- **用途**: 当对话历史过长时自动压缩以节省 tokens

**`system`** (可选)
- **类型**: `string`
- **说明**: 系统提示词（System Prompt）
  - 定义智能体的角色和行为
  - 每个智能体可以有不同的系统提示词
- **示例**: `"你是一个专业的客服人员，请友好、耐心地回答用户问题。"`

**`temperature`** (可选，默认: `1.0`)
- **类型**: `number` (0-2)
- **说明**: 生成温度参数
  - 越低越确定性（0.2-0.5 适合精确任务）
  - 越高越随机性（0.8-1.5 适合创意任务）

**`maxTokens`** (可选)
- **类型**: `number`
- **说明**: 最大生成 tokens 数
  - 限制智能体单次响应的长度

---

#### AgentEntry 主要字段

**定义**: `src/config/zod-schema.agent-runtime.ts`

**`id`** ⭐ (必填)
- **类型**: `string`
- **说明**: 智能体唯一标识符
  - 用于路由绑定（`bindings`）中引用
  - 必须唯一
- **示例**: `"default-agent"`, `"support-agent"`, `"coding-agent"`

**`name`** (可选)
- **类型**: `string`
- **说明**: 智能体显示名称
  - 用于 UI 展示和日志记录
- **示例**: `"默认智能体"`, `"客服助手"`, `"编程专家"`

**`model.primary`** (可选)
- **类型**: `string`
- **说明**: 覆盖 `defaults` 中的默认模型
  - 允许不同智能体使用不同的模型
- **示例**: `"bailian/qwen3-coder-plus"` (编程专用模型)

**`system`** (可选)
- **类型**: `string`
- **说明**: 覆盖 `defaults` 中的默认系统提示词
  - 为该智能体定制专属的行为
- **示例**: `"你是一个 Python 编程专家，擅长代码调试和性能优化。"`

**`tools`** (可选)
- **类型**: `ToolsConfig` 对象
- **说明**: 工具配置（技能、权限等）
  - 控制该智能体可以使用哪些工具和技能

#### 实际示例

```json
{
  "agents": {
    "defaults": {
      "model": {
        "primary": "bailian/qwen3.5-plus"
      },
      "models": {
        "bailian/qwen3.5-plus": {},
        "bailian/kimi-k2.5": {},
        "bailian/glm-5": {}
      },
      "workspace": "/Users/lifeng/git/git-claw/agent-openclaw-assisant/workspace/lobsters/openclaw-docker-001",
      "compaction": {
        "mode": "safeguard"
      }
    },
    "list": [
      {
        "id": "default-agent",
        "name": "默认智能体"
      },
      {
        "id": "coding-agent",
        "name": "编程助手",
        "model": {
          "primary": "bailian/qwen3-coder-plus"
        }
      }
    ]
  }
}
```

**用途**：
- `defaults`: 设置所有智能体的公共配置（模型、工作目录、压缩策略等）
- `list`: 定义具体的智能体实例，可以覆盖 defaults 中的配置
- 每个智能体可以有不同的模型、系统提示词、工具权限

---

### commands - 命令执行配置

**Schema 定义**: `src/config/zod-schema.session.ts` 中的 `CommandsSchema`

```typescript
CommandsSchema = z.object({
  native: z.union([                        // 原生命令执行权限
    z.literal("auto"),                     // 自动（根据环境判断）
    z.literal("on"),                       // 始终启用
    z.literal("off")                       // 始终禁用
  ]).optional(),
  nativeSkills: z.union([                  // 原生技能执行权限
    z.literal("auto"),
    z.literal("on"),
    z.literal("off")
  ]).optional(),
  restart: z.boolean().optional(),          // 是否允许重启命令
  ownerDisplay: z.union([                   // 命令输出的所有者显示方式
    z.literal("raw"),                       // 原始显示（显示用户名）
    z.literal("anonymous"),                 // 匿名（不显示用户名）
    z.literal("hide")                       // 隐藏
  ]).optional(),
}).strict().optional()
```

#### 字段说明

**`native`** (可选，默认: `"auto"`)
- **类型**: `"auto"` | `"on"` | `"off"`
- **说明**: 控制智能体是否可以执行系统命令（如 `ls`, `cat`, `grep`）
  - `auto`: 根据环境自动决定（本地开发环境允许，生产环境禁止）
  - `on`: 始终允许
  - `off`: 始终禁止
- **安全建议**: 生产环境建议设为 `"off"` 或使用审批机制

**`nativeSkills`** (可选，默认: `"auto"`)
- **类型**: `"auto"` | `"on"` | `"off"`
- **说明**: 控制智能体是否可以执行原生技能（Python/Shell 脚本）
  - `auto`: 根据环境自动决定
  - `on`: 始终允许
  - `off`: 始终禁止
- **用途**: 原生技能是实例 `skills/` 目录下的 Python/Shell 脚本

**`restart`** (可选，默认: `true`)
- **类型**: `boolean`
- **说明**: 是否允许智能体使用重启命令
  - `true`: 允许智能体重启实例
  - `false`: 禁止重启

**`ownerDisplay`** (可选，默认: `"raw"`)
- **类型**: `"raw"` | `"anonymous"` | `"hide"`
- **说明**: 命令输出时如何显示执行者信息
  - `raw`: 显示完整用户名
  - `anonymous`: 匿名化处理
  - `hide`: 完全隐藏

#### 实际示例

```json
{
  "commands": {
    "native": "auto",
    "nativeSkills": "auto",
    "restart": true,
    "ownerDisplay": "raw"
  }
}
```

**用途**：
- 控制智能体的命令执行权限（安全性考虑）
- `native`: 控制系统命令（如 `ls`, `cat`）
- `nativeSkills`: 控制技能脚本（Python/Shell）
- 在生产环境建议设置为 `"off"` 或使用审批机制

---

### gateway - 网关配置

**Schema 定义**: `src/config/zod-schema.ts`, line 621-810

```typescript
gateway: z.object({
  port: z.number().int().positive().optional(),                    // 网关端口
  mode: z.union([z.literal("local"), z.literal("remote")]).optional(), // 运行模式
  bind: z.union([                                                   // 绑定地址模式
    z.literal("auto"),
    z.literal("lan"),
    z.literal("loopback"),
    z.literal("custom"),
    z.literal("tailnet")
  ]).optional(),
  customBindHost: z.string().optional(),                           // 自定义绑定地址
  controlUi: {...}.optional(),                                     // Control UI 配置
  auth: {...}.optional(),                                          // 认证配置
  trustedProxies: z.array(z.string()).optional(),                 // 受信任的代理列表
  allowRealIpFallback: z.boolean().optional(),                    // 允许真实 IP 回退
  tools: {...}.optional(),                                         // 工具权限
  channelHealthCheckMinutes: z.number().int().min(0).optional(), // 渠道健康检查间隔
  tailscale: {...}.optional(),                                    // Tailscale 配置
  remote: {...}.optional(),                                       // 远程连接配置
  reload: {...}.optional(),                                       // 热重载配置
  tls: {...}.optional(),                                          // TLS 配置
  http: {...}.optional(),                                         // HTTP 端点配置
  nodes: {...}.optional(),                                        // 节点配置
}).strict().optional()
```

#### 主要字段说明

**`port`** (可选，默认: `3000`)
- **类型**: `number`
- **说明**: 网关监听端口
- **示例**: `18900`, `3000`, `8080`

**`mode`** (可选，默认: `"local"`)
- **类型**: `"local"` 或 `"remote"`
- **说明**: 运行模式
  - `local`: 本地模式（网关和客户端在同一台机器）
  - `remote`: 远程模式（客户端通过网络访问网关）

**`bind`** (可选，默认: `"auto"`)
- **类型**: `"auto"` | `"loopback"` | `"lan"` | `"custom"` | `"tailnet"`
- **说明**: 绑定地址模式
  - `auto`: 自动选择（根据 mode 决定）
  - `loopback`: 仅本地访问（绑定 127.0.0.1）
  - `lan`: 局域网访问（绑定 0.0.0.0）
  - `custom`: 自定义地址（需配合 `customBindHost`）
  - `tailnet`: Tailscale 网络
- **Docker 环境**: 通常使用 `"custom"` + `"0.0.0.0"`

**`customBindHost`** (可选)
- **类型**: `string`
- **说明**: 当 `bind="custom"` 时的具体 IP 地址
- **示例**: `"0.0.0.0"`, `"192.168.1.100"`

**`trustedProxies`** (可选，默认: `[]`)
- **类型**: `string[]` 数组
- **说明**: 受信任的代理 IP 或 CIDR 范围
  - 用于从 `X-Forwarded-For` 等头部获取真实客户端 IP
  - Docker 环境需要配置 Docker 网络范围
- **示例**: `["172.24.0.0/16"]`, `["10.0.0.0/8", "192.168.0.0/16"]`

**`controlUi`** (可选)
- **类型**: `object`
- **说明**: Control UI（Web 控制台）配置
- **详见**: 下方 controlUi 章节

**`auth`** (可选)
- **类型**: `object`
- **说明**: 认证配置
- **详见**: 下方 auth 章节

#### gateway.controlUi Schema

**定义**: `src/config/zod-schema.ts`, line 635-646

```typescript
controlUi: z.object({
  enabled: z.boolean().optional(),                                    // 是否启用 Control UI
  basePath: z.string().optional(),                                    // 基础路径
  root: z.string().optional(),                                        // 静态文件根目录
  allowedOrigins: z.array(z.string()).optional(),                    // 允许的跨域源
  dangerouslyAllowHostHeaderOriginFallback: z.boolean().optional(), // 允许 Host 头回退
  allowInsecureAuth: z.boolean().optional(),                         // 允许不安全认证
  dangerouslyDisableDeviceAuth: z.boolean().optional(),              // 禁用设备认证
}).strict().optional()
```

##### controlUi 字段说明

**`enabled`** (可选，默认: `true`)
- **类型**: `boolean`
- **说明**: 是否启用 Web 控制台
  - `true`: 启用（可通过浏览器访问 `http://localhost:port`）
  - `false`: 禁用

**`allowedOrigins`** (可选，默认: `[]`)
- **类型**: `string[]` 数组
- **说明**: CORS 允许的源列表
  - 用于跨域访问控制
  - Docker 环境需要添加多个可能的访问地址
- **示例**: 
  ```json
  [
    "http://localhost:18900",
    "http://127.0.0.1:18900",
    "http://0.0.0.0:18900"
  ]
  ```

**`dangerouslyDisableDeviceAuth`** ⚠️ (可选，默认: `false`)
- **类型**: `boolean`
- **说明**: **危险设置！** 禁用设备认证
  - `true`: 禁用设备绑定机制
  - `false`: 启用设备认证（推荐）
- **使用场景**: 
  - Docker 容器环境（必需）
  - 开发环境
- **警告**: 生产环境的主机部署不应启用此选项

#### gateway.auth Schema

**定义**: `src/config/zod-schema.ts`, line 647-679

```typescript
auth: z.object({
  mode: z.union([                                 // 认证模式
    z.literal("none"),                            // 无认证
    z.literal("token"),                           // Token 认证
    z.literal("password"),                        // 密码认证
    z.literal("trusted-proxy")                    // 受信任代理认证
  ]).optional(),
  token: SecretInputSchema.optional(),            // Token 值
  password: SecretInputSchema.optional(),         // 密码值
  allowTailscale: z.boolean().optional(),         // 允许 Tailscale 认证
  rateLimit: {...}.optional(),                    // 速率限制配置
  trustedProxy: {...}.optional(),                 // 受信任代理配置
}).strict().optional()
```

##### auth 字段说明

**`mode`** (可选，默认: `"token"`)
- **类型**: `"none"` | `"token"` | `"password"` | `"trusted-proxy"`
- **说明**: 认证方式
  - `none`: 无认证（⚠️ 不推荐，任何人可访问）
  - `token`: Token 认证（推荐）
  - `password`: 密码认证
  - `trusted-proxy`: 通过可信代理认证（适用于反向代理场景）

**`token`** (条件必填)
- **类型**: `string` 或 `SecretRef`
- **说明**: 访问 token
  - 当 `mode="token"` 时**必需**
  - 访问 Control UI 时需要在 URL 中携带：`http://host:port/#token=your-token`
- **生成建议**: 使用随机字符串（至少 32 字符）
- **示例**: `"daf88df829d079823b2ccaf6a6c338ad17874d513199d6b7"`

**`password`** (条件必填)
- **类型**: `string` 或 `SecretRef`
- **说明**: 访问密码
  - 当 `mode="password"` 时**必需**
  - 访问 Control UI 时会弹出密码输入框

**`allowTailscale`** (可选，默认: `false`)
- **类型**: `boolean`
- **说明**: 是否允许通过 Tailscale 认证
  - `true`: 允许（需配置 Tailscale）
  - `false`: 不允许

#### 实际示例

```json
{
  "gateway": {
    "mode": "local",
    "bind": "custom",
    "customBindHost": "0.0.0.0",
    "trustedProxies": ["172.24.0.0/16"],
    "controlUi": {
      "allowedOrigins": [
        "http://localhost:18900",
        "http://127.0.0.1:18900",
        "http://0.0.0.0:18900"
      ],
      "dangerouslyDisableDeviceAuth": true
    },
    "auth": {
      "mode": "token",
      "token": "daf88df829d079823b2ccaf6a6c338ad17874d513199d6b7"
    }
  }
}
```

**用途**：
- `bind` + `customBindHost`: 控制网关监听的网络接口（本地/局域网/自定义）
- `auth`: 保护网关访问，防止未授权访问
- `controlUi`: 配置 Web 控制台的行为和安全策略
- `trustedProxies`: Docker/反向代理环境中获取真实客户端 IP

---

### channels - 渠道配置

**Schema 定义**: `src/config/zod-schema.providers.ts` 中的 `ChannelsSchema`

```typescript
ChannelsSchema = z.record(z.string(), z.unknown()).optional()
```

OpenClaw 支持多种消息渠道（飞书、QQ、企微、钉钉等），每个渠道的具体 Schema 由对应的插件定义。

#### 通用渠道字段（以飞书为例）

**`appId`** ⭐ (必填)
- **类型**: `string`
- **说明**: 飞书应用的 App ID
- **获取方式**: 飞书开发者后台 → 凭证与基础信息
- **示例**: `"cli_a92386f562391bd9"`

**`appSecret`** ⭐ (必填)
- **类型**: `string` 或 `SecretRef`
- **说明**: 飞书应用的 App Secret（敏感信息）
- **获取方式**: 飞书开发者后台 → 凭证与基础信息
- **安全建议**: 使用密钥引用而非明文
- **示例**: `"qSI9rTfbfIbfymEgAwJyE3QeON28llIv"`

**`enabled`** (可选，默认: `true`)
- **类型**: `boolean`
- **说明**: 是否启用该渠道
  - `true`: 启用
  - `false`: 禁用（但保留配置）

**`streaming`** (可选，默认: `false`)
- **类型**: `boolean`
- **说明**: 是否启用流式响应
  - `true`: 智能体响应时实时推送（用户体验更好）
  - `false`: 等待完整响应后一次性推送

**`dmPolicy`** (可选，默认: `"pairing"`)
- **类型**: `"open"` 或 `"pairing"`
- **说明**: 私聊（Direct Message）访问策略
  - `open`: 开放模式
    - ✅ 任何人都可以直接私聊机器人
    - ✅ 无需管理员批准
    - ⚠️ 可能产生意外的 API 费用
  - `pairing`: 配对模式
    - 🔒 用户首次私聊需要管理员批准
    - ✅ 控制谁可以使用
    - 批准方式：`python instance_manager.py approve-pairing <实例名> feishu`
- **推荐**：
  - 开发/测试环境：使用 `"open"`
  - 生产环境：使用 `"pairing"`

**`groupPolicy`** (可选，默认: `"open"`)
- **类型**: `"open"` 或 `"pairing"`
- **说明**: 群聊访问策略
  - `open`: 开放模式
    - ✅ 机器人加入任何群聊都会自动响应
    - ⚠️ 可能被拉入大量无关群聊
  - `pairing`: 配对模式
    - 🔒 每个群聊需要管理员批准后才响应
    - ✅ 控制机器人在哪些群使用
- **推荐**：
  - 个人/小团队：使用 `"open"`
  - 大型组织：使用 `"pairing"`

**`accounts`** (可选)
- **类型**: `Record<string, AccountConfig>` 对象字典
- **说明**: 多账号配置
  - 允许一个实例同时管理多个飞书机器人
  - 键为账号 ID（自定义，如 `"bot_002"`）

---

#### accounts 配置（多账号功能）

多账号功能允许一个 OpenClaw 实例同时管理多个飞书机器人，每个机器人可以路由到不同的智能体。

**`appId`** ⭐ (必填)
- **类型**: `string`
- **说明**: 该机器人账号的 App ID

**`appSecret`** ⭐ (必填)
- **类型**: `string` 或 `SecretRef`
- **说明**: 该机器人账号的 App Secret

**`connectionMode`** (可选，默认: `"websocket"`)
- **类型**: `"webhook"` 或 `"websocket"`
- **说明**: 连接模式
  - `webhook`: 使用 HTTP 回调（需要公网 URL）
  - `websocket`: 使用 WebSocket 长连接（推荐，无需公网）

**`dmPolicy`** (可选，默认: `"pairing"`)
- **类型**: `"open"` 或 `"pairing"`
- **说明**: 该账号的私聊（Direct Message）策略
  - `open`: 开放模式（任何人都可以私聊此机器人）
  - `pairing`: 配对模式（需要管理员批准才能私聊）
- **继承**: 如果不指定，会继承渠道级别的 `dmPolicy`

**`groupPolicy`** (可选，默认: `"open"`)
- **类型**: `"open"` 或 `"pairing"`
- **说明**: 该账号的群聊策略
  - `open`: 开放模式（机器人加入任何群聊都会响应）
  - `pairing`: 配对模式（需要批准才能在群聊中使用）
- **继承**: 如果不指定，会继承渠道级别的 `groupPolicy`

#### 实际示例

```json
{
  "channels": {
    "feishu": {
      "appId": "cli_a92386f562391bd9",
      "appSecret": "qSI9rTfbfIbfymEgAwJyE3QeON28llIv",
      "enabled": true,
      "streaming": false,
      "accounts": {
        "bot_002": {
          "appId": "cli_a938ea9171fbdbd3",
          "appSecret": "ZVYzY9gpVV0FoPH31bgVAcnB6N112kSY",
          "connectionMode": "websocket",
          "dmPolicy": "pairing",
          "groupPolicy": "open"
        }
      }
    }
  }
}
```

**用途**：
- 连接各种消息平台（飞书、QQ、企微、钉钉等）
- 支持一个实例同时管理多个机器人账号
- 通过 `enabled` 字段快速启用/禁用渠道

---

### plugins - 插件配置

**Schema 定义**: `src/config/zod-schema.ts`, line 846-877

```typescript
plugins: z.object({
  enabled: z.boolean().optional(),                           // 是否启用插件系统
  allow: z.array(z.string()).optional(),                     // 允许列表
  deny: z.array(z.string()).optional(),                      // 拒绝列表
  load: z.object({                                            // 加载配置
    paths: z.array(z.string()).optional(),                   // 额外的插件加载路径
  }).strict().optional(),
  slots: z.object({                                           // 插槽配置
    memory: z.string().optional(),                           // 记忆插件
    contextEngine: z.string().optional(),                    // 上下文引擎插件
  }).strict().optional(),
  entries: z.record(z.string(), PluginEntrySchema).optional(), // 插件实例配置
  installs: z.record(z.string(), z.object({                   // 插件安装记录
    ...InstallRecordShape,
  }).strict()).optional(),
}).strict().optional()
```

#### 主要字段说明

**`enabled`** (可选，默认: `true`)
- **类型**: `boolean`
- **说明**: 是否启用插件系统
  - `true`: 启用
  - `false`: 禁用所有插件

**`allow`** (可选，默认: `[]`)
- **类型**: `string[]` 数组
- **说明**: 允许加载的插件 ID 白名单
  - 为空数组表示允许所有插件
  - 指定插件 ID 后只加载列表中的插件
- **示例**: `["feishu", "github", "jira"]`

**`deny`** (可选，默认: `[]`)
- **类型**: `string[]` 数组
- **说明**: 禁止加载的插件 ID 黑名单
  - 列表中的插件不会被加载
  - 优先级高于 `allow`
- **示例**: `["experimental-plugin"]`

**`entries`** (可选，默认: `{}`)
- **类型**: `Record<string, PluginEntry>` 对象字典
- **说明**: 插件实例配置
  - 键为插件 ID（如 `"feishu"`, `"github"`）
  - 值为插件的具体配置

**`installs`** (可选，默认: `{}`)
- **类型**: `Record<string, InstallRecord>` 对象字典
- **说明**: 插件安装记录
  - 由 OpenClaw 自动管理，记录插件的安装信息
  - 通常无需手动修改

#### PluginEntry Schema

**定义**: `src/config/zod-schema.ts`, line 149-160

```typescript
PluginEntrySchema = z.object({
  enabled: z.boolean().optional(),                           // 是否启用该插件
  hooks: z.object({                                           // 钩子配置
    allowPromptInjection: z.boolean().optional(),            // 是否允许提示词注入
  }).strict().optional(),
  config: z.record(z.string(), z.unknown()).optional(),      // 插件自定义配置
}).strict()
```

##### PluginEntry 字段说明

**`enabled`** (可选，默认: `true`)
- **类型**: `boolean`
- **说明**: 是否启用该插件实例
  - `true`: 启用
  - `false`: 禁用（但保留配置）

**`hooks.allowPromptInjection`** (可选，默认: `false`)
- **类型**: `boolean`
- **说明**: 是否允许插件注入提示词
  - `true`: 允许（⚠️ 安全风险）
  - `false`: 禁止（推荐）
- **安全考虑**: 允许提示词注入可能导致插件修改智能体行为

**`config`** (可选，默认: `{}`)
- **类型**: `Record<string, any>` 对象
- **说明**: 插件特定的配置参数
  - 每个插件的配置项不同
  - 由插件自行定义和解析
- **示例**:
  ```json
  {
    "config": {
      "token": "github_pat_xxxxxxxxxxxx",
      "repos": ["owner/repo1", "owner/repo2"],
      "autoSync": true
    }
  }
  ```

#### 实际示例

```json
{
  "plugins": {
    "enabled": true,
    "entries": {
      "feishu": {
        "enabled": true
      },
      "github": {
        "enabled": true,
        "config": {
          "token": "ghp_xxxxxxxxxxxx",
          "repos": ["owner/repo1", "owner/repo2"]
        }
      }
    }
  }
}
```

**用途**：
- 启用/禁用特定插件（如飞书、QQ、GitHub、Jira 等）
- 配置插件的行为和参数
- 控制插件的权限（如是否允许提示词注入）

---

### bindings - 路由绑定

**Schema 定义**: `src/config/zod-schema.agents.ts`, line 92

```typescript
BindingsSchema = z.array(z.union([RouteBindingSchema, AcpBindingSchema])).optional()
```

#### RouteBinding Schema

**定义**: `src/config/zod-schema.agents.ts`, line 37-44

```typescript
RouteBindingSchema = z.object({
  type: z.literal("route").optional(),     // 绑定类型（route）
  agentId: z.string(),                     // 目标智能体 ID
  comment: z.string().optional(),          // 备注说明
  match: BindingMatchSchema,               // 匹配规则
}).strict()
```

#### BindingMatch Schema

**定义**: `src/config/zod-schema.agents.ts`, line 14-35

```typescript
BindingMatchSchema = z.object({
  channel: z.string(),                     // 渠道 ID（如 "feishu", "qq"）
  accountId: z.string().optional(),        // 账号 ID（多账号时指定）
  peer: z.object({                          // 对等端（会话类型）
    kind: z.union([
      z.literal("direct"),                 // 私聊（DM）
      z.literal("group"),                  // 群聊
      z.literal("channel"),                // 频道
      z.literal("dm")                      // 已弃用，使用 "direct"
    ]),
    id: z.string(),                        // 对等端 ID（群 ID/用户 ID）
  }).strict().optional(),
  guildId: z.string().optional(),          // Discord Guild ID
  teamId: z.string().optional(),           // 团队 ID
  roles: z.array(z.string()).optional(),   // 角色列表
}).strict()
```

#### 字段说明

**`agentId`** ⭐ (必填)
- **类型**: `string`
- **说明**: 要路由到的智能体 ID
  - 必须在 `agents.list` 中定义
  - 引用不存在的智能体会导致配置验证失败
- **示例**: `"test-agent"`, `"support-agent"`, `"coding-agent"`

**`comment`** (可选)
- **类型**: `string`
- **说明**: 备注说明
  - 方便理解路由规则的意图
  - 不影响实际路由逻辑
- **示例**: `"feishu -> test-agent"`, `"私聊路由到客服智能体"`

**`match.channel`** ⭐ (必填)
- **类型**: `string`
- **说明**: 渠道 ID
  - 必须与 `channels` 中配置的渠道对应
- **常见值**: `"feishu"`, `"qq"`, `"wecom"`, `"dingtalk"`, `"discord"`, `"telegram"`

**`match.accountId`** (可选)
- **类型**: `string`
- **说明**: 账号 ID（多账号时指定）
  - 对应 `channels.<channel>.accounts` 中的键
  - 不指定则匹配该渠道的默认账号
- **示例**: `"bot_002"`, `"customer-service"`

**`match.peer.kind`** (可选)
- **类型**: `"direct"` | `"group"` | `"channel"`
- **说明**: 会话类型
  - `direct`: 私聊（1对1对话）
  - `group`: 群聊
  - `channel`: 频道（如 Discord 频道）
  - 不指定则匹配所有类型

**`match.peer.id`** (可选)
- **类型**: `string`
- **说明**: 会话 ID
  - 群聊时为群 ID
  - 私聊时为用户 ID
  - 不指定则匹配所有会话

#### 实际示例

```json
{
  "bindings": [
    {
      "agentId": "test-agent",
      "match": {
        "channel": "feishu"
      },
      "comment": "feishu -> test-agent"
    },
    {
      "agentId": "agent-002",
      "match": {
        "channel": "feishu",
        "accountId": "bot_002"
      },
      "comment": "feishu (bot_002) -> agent-002"
    },
    {
      "agentId": "vip-agent",
      "match": {
        "channel": "feishu",
        "peer": {
          "kind": "direct",
          "id": "ou_xxxxxxxxxxxx"
        }
      },
      "comment": "feishu DM from specific user -> vip-agent"
    }
  ]
}
```

**用途**：
- 定义消息路由规则（哪个渠道的消息分配给哪个智能体）
- 支持按渠道、账号、会话类型、会话 ID 进行精细化路由
- 可以为不同的用户或群组配置不同的智能体

**匹配优先级**：
1. 最具体的匹配（指定了 `peer.id`）优先级最高
2. 指定了 `accountId` 的匹配次之
3. 只指定 `channel` 的匹配优先级最低

---

## 高级配置

### secrets - 密钥管理

**Schema 定义**: `src/config/zod-schema.core.ts`, line 148-179

OpenClaw 支持从多种来源读取敏感信息（API Key、Token 等），而不是直接写在配置文件中。

#### 密钥引用格式

```typescript
SecretRefSchema = z.discriminatedUnion("source", [
  EnvSecretRefSchema,     // 从环境变量读取
  FileSecretRefSchema,    // 从文件读取
  ExecSecretRefSchema,    // 从命令输出读取
])
```

#### 使用示例

**从环境变量读取**：
```json
{
  "models": {
    "providers": {
      "openai": {
        "baseUrl": "https://api.openai.com/v1",
        "apiKey": {
          "source": "env",
          "provider": "default",
          "id": "OPENAI_API_KEY"
        },
        "models": [...]
      }
    }
  }
}
```

**从文件读取**：
```json
{
  "models": {
    "providers": {
      "openai": {
        "baseUrl": "https://api.openai.com/v1",
        "apiKey": {
          "source": "file",
          "provider": "default",
          "id": "/providers/openai/apiKey"
        },
        "models": [...]
      }
    }
  }
}
```

### session - 会话配置

**Schema 定义**: `src/config/zod-schema.session.ts` 中的 `SessionSchema`

控制会话行为、历史记录、持久化等。

#### 主要字段

**`history.enabled`** (可选，默认: `true`)
- **类型**: `boolean`
- **说明**: 是否保留会话历史
  - `true`: 保留（智能体可以记住之前的对话）
  - `false`: 不保留（每次对话都是全新的）

**`history.maxMessages`** (可选)
- **类型**: `number`
- **说明**: 最大保留消息数
  - 超过此数量后旧消息会被移除
  - 用于控制内存使用

**`persistence.enabled`** (可选，默认: `false`)
- **类型**: `boolean`
- **说明**: 是否持久化会话
  - `true`: 会话持久化到磁盘（重启后恢复）
  - `false`: 仅在内存中（重启后丢失）

**`persistence.path`** (可选)
- **类型**: `string`
- **说明**: 持久化存储路径
  - 会话数据的存储目录

### memory - 记忆配置

**Schema 定义**: `src/config/zod-schema.ts`, line 114-121

为智能体提供长期记忆能力（RAG）。

#### 主要字段

**`backend`** (可选，默认: `"builtin"`)
- **类型**: `"builtin"` 或 `"qmd"`
- **说明**: 记忆后端选择
  - `builtin`: 内置简单记忆（适合小规模使用）
  - `qmd`: qmdx 文档记忆系统（支持大规模文档检索）

**`citations`** (可选，默认: `"auto"`)
- **类型**: `"auto"` | `"on"` | `"off"`
- **说明**: 是否显示引用来源
  - `auto`: 自动决定是否显示
  - `on`: 始终显示引用来源
  - `off`: 不显示引用来源

**`qmd.paths`** (可选)
- **类型**: `array` 数组
- **说明**: qmdx 文档路径列表
  - 当 `backend="qmd"` 时使用
  - 指定要索引的文档目录

### cron - 定时任务

**Schema 定义**: `src/config/zod-schema.ts`, line 486-557

支持类似 Linux cron 的定时任务功能。

#### 主要字段

**`enabled`** (可选，默认: `true`)
- **类型**: `boolean`
- **说明**: 是否启用定时任务功能
  - `true`: 启用
  - `false`: 禁用

**`maxConcurrentRuns`** (可选)
- **类型**: `number`
- **说明**: 最大并发任务数
  - 限制同时运行的定时任务数量
  - 防止资源过载

**`webhook`** (可选)
- **类型**: `string` (URL)
- **说明**: Webhook URL
  - 任务完成时向此 URL 发送通知
  - 用于监控和集成

---

## 配置模板文件

为了方便使用，我们提供了三个开箱即用的配置模板：

📄 **激进模式配置**：`docs/03-技术解读/openclaw-config-templates/激进模式-零门槛配置.json`
- 无需认证即可访问
- 飞书无需配对
- 适合开发测试

📄 **混合模式配置**：`docs/03-技术解读/openclaw-config-templates/混合模式-团队协作配置.json`
- 需要 Token 访问
- 私聊开放，群聊需配对
- 适合小团队

📄 **安全模式配置**：`docs/03-技术解读/openclaw-config-templates/安全模式-生产环境配置.json`
- Token 认证 + 设备绑定
- 所有渠道需配对
- 适合生产环境

**使用方法**：
1. 复制对应模板文件内容
2. 替换其中的占位符（API Key、App ID 等）
3. 保存为实例的 `.openclaw/openclaw.json`
4. 重启实例

---

## 实战示例

### 示例 1：激进模式配置（最简化、零门槛）

**适用场景**：
- ✅ 开发测试环境
- ✅ 内网环境
- ✅ 快速上手学习
- ⚠️ **不适用于生产环境**

**特点**：
- **完全无需认证**（auth.mode=none）
- 无需任何 Token
- 渠道无需配对（开放模式）
- 禁用设备认证
- 真正的零门槛

**技术方案**：
- **主机模式**：loopback 绑定，仅本机访问
- **Docker 模式**：loopback + Nginx 代理，局域网可访问

**访问方式**：
- 主机模式：`http://127.0.0.1:18800/`
- Docker 模式：`http://127.0.0.1:18900/` 或 `http://局域网IP:18900/`

```json
{
  "meta": {
    "lastTouchedVersion": "2026.3.11",
    "lastTouchedAt": "2026-03-12T10:00:00.000Z"
  },
  "models": {
    "providers": {
      "bailian": {
        "baseUrl": "https://coding.dashscope.aliyuncs.com/v1",
        "apiKey": "sk-sp-xxxxxxxxxxxx",
        "api": "openai-completions",
        "models": [
          {
            "id": "qwen3.5-plus",
            "name": "通义千问 3.5 Plus",
            "contextWindow": 1000000,
            "maxTokens": 65536
          }
        ]
      }
    }
  },
  "agents": {
    "defaults": {
      "model": {
        "primary": "bailian/qwen3.5-plus"
      }
    }
  },
  "commands": {
    "native": "auto",
    "nativeSkills": "auto"
  },
  "gateway": {
    "mode": "local",
    "bind": "loopback",
    "port": 3000,
    "auth": {
      "mode": "none"
    },
    "controlUi": {
      "enabled": true,
      "dangerouslyDisableDeviceAuth": true
    }
  },
  "channels": {
    "feishu": {
      "appId": "cli_xxxxxxxxxxxx",
      "appSecret": "your-app-secret",
      "enabled": true,
      "streaming": false,
      "connectionMode": "websocket",
      "dmPolicy": "open",
      "groupPolicy": "open"
    }
  },
  "plugins": {
    "entries": {
      "feishu": {
        "enabled": true
      }
    }
  }
}
```

**配置要点解析**：

1. **网关配置（完全无认证）**：
   ```json
   {
     "gateway": {
       "bind": "loopback",        // 仅本机访问（127.0.0.1）
       "port": 3000,              // 内部端口
       "auth": {
         "mode": "none"           // ✅ 完全无认证
       },
       "controlUi": {
         "dangerouslyDisableDeviceAuth": true  // 禁用设备绑定
       }
     }
   }
   ```
   
   **重要说明**：
   - 使用 `bind: loopback` 是唯一支持 `auth.mode: none` 的绑定模式
   - **主机模式**：直接访问 `http://127.0.0.1:18800/`，仅本机可访问
   - **Docker 模式**：使用 Nginx 代理架构
     - OpenClaw 监听：`127.0.0.1:3000`（内部，无认证）
     - Nginx 监听：`0.0.0.0:18900`（外部，代理到 OpenClaw）
     - 访问：`http://127.0.0.1:18900/` 或 `http://局域网IP:18900/`
   - 详见：[激进模式-Nginx代理方案.md](./激进模式-Nginx代理方案.md)

2. **飞书渠道（无需配对）**：
   ```json
   {
     "channels": {
       "feishu": {
         "dmPolicy": "open",       // 私聊开放（无需配对）
         "groupPolicy": "open"     // 群聊开放（无需配对）
       }
     }
   }
   ```

**访问方式**：
- Control UI：`http://<服务器IP>:3000` （无需 token）
- 飞书：直接私聊或拉入群聊即可使用（无需批准配对）

⚠️ **安全警告**：
- **不要在公网环境使用此配置**
- **不要在生产环境使用此配置**
- **建议仅在内网或开发环境使用**
- 任何能访问网络的人都可以控制你的实例

---

### 示例 2：最小化安全配置

如果你需要基本的安全保护，使用此配置：

```json
{
  "meta": {
    "lastTouchedVersion": "2026.3.11",
    "lastTouchedAt": "2026-03-12T10:00:00.000Z"
  },
  "models": {
    "providers": {
      "openai": {
        "baseUrl": "https://api.openai.com/v1",
        "apiKey": "sk-xxxxxxxxxxxxxxxx",
        "models": [
          {
            "id": "gpt-4",
            "name": "GPT-4",
            "contextWindow": 8192,
            "maxTokens": 4096
          }
        ]
      }
    }
  },
  "agents": {
    "defaults": {
      "model": {
        "primary": "openai/gpt-4"
      }
    }
  },
  "gateway": {
    "mode": "local",
    "auth": {
      "mode": "token",
      "token": "your-random-token-here"
    }
  },
  "channels": {
    "feishu": {
      "appId": "cli_xxxxxxxxxxxx",
      "appSecret": "your-app-secret",
      "enabled": true,
      "dmPolicy": "pairing",
      "groupPolicy": "pairing"
    }
  }
}
```

---

### 示例 3：多智能体 + 飞书渠道

```json
{
  "models": {
    "providers": {
      "bailian": {
        "baseUrl": "https://coding.dashscope.aliyuncs.com/v1",
        "apiKey": "sk-sp-xxxxxxxxxxxx",
        "api": "openai-completions",
        "models": [
          {
            "id": "qwen3.5-plus",
            "name": "通义千问3.5 Plus",
            "contextWindow": 1000000,
            "maxTokens": 65536
          }
        ]
      }
    }
  },
  "agents": {
    "defaults": {
      "model": {
        "primary": "bailian/qwen3.5-plus"
      }
    },
    "list": [
      {
        "id": "support-agent",
        "name": "客服智能体",
        "system": "你是一个专业的客服人员，请友好、耐心地回答用户问题。"
      },
      {
        "id": "tech-agent",
        "name": "技术支持智能体",
        "system": "你是一个技术支持专家，擅长解决技术问题。"
      }
    ]
  },
  "channels": {
    "feishu": {
      "appId": "cli_a92386f562391bd9",
      "appSecret": "your-app-secret",
      "enabled": true
    }
  },
  "plugins": {
    "entries": {
      "feishu": {
        "enabled": true
      }
    }
  },
  "bindings": [
    {
      "agentId": "support-agent",
      "match": {
        "channel": "feishu",
        "peer": {
          "kind": "direct"
        }
      },
      "comment": "私聊路由到客服智能体"
    },
    {
      "agentId": "tech-agent",
      "match": {
        "channel": "feishu",
        "peer": {
          "kind": "group"
        }
      },
      "comment": "群聊路由到技术支持智能体"
    }
  ],
  "gateway": {
    "mode": "local",
    "auth": {
      "mode": "token",
      "token": "your-token-here"
    }
  }
}
```

---

### 示例 4：Docker 环境配置

```json
{
  "meta": {
    "lastTouchedVersion": "2026.3.11",
    "lastTouchedAt": "2026-03-12T12:00:00.000Z"
  },
  "models": {
    "providers": {
      "bailian": {
        "baseUrl": "https://coding.dashscope.aliyuncs.com/v1",
        "apiKey": "sk-sp-xxxxxxxxxxxx",
        "api": "openai-completions",
        "models": [
          {
            "id": "qwen3.5-plus",
            "name": "qwen3.5-plus",
            "contextWindow": 1000000,
            "maxTokens": 65536
          }
        ]
      }
    }
  },
  "agents": {
    "defaults": {
      "model": {
        "primary": "bailian/qwen3.5-plus"
      },
      "workspace": "/workspace"
    }
  },
  "commands": {
    "native": "auto",
    "nativeSkills": "auto",
    "restart": true
  },
  "gateway": {
    "mode": "local",
    "bind": "custom",
    "customBindHost": "0.0.0.0",
    "trustedProxies": ["172.24.0.0/16"],
    "controlUi": {
      "allowedOrigins": [
        "http://localhost:18900",
        "http://127.0.0.1:18900"
      ],
      "dangerouslyDisableDeviceAuth": true
    },
    "auth": {
      "mode": "token",
      "token": "your-docker-token"
    }
  }
}
```

**Docker 配置要点**：
- `gateway.bind = "custom"` + `customBindHost = "0.0.0.0"`: 允许容器外部访问
- `trustedProxies`: 配置 Docker 网络 CIDR（通常是 `172.x.x.x/16`）
- `controlUi.dangerouslyDisableDeviceAuth = true`: 禁用设备认证（Docker 环境必需）
- `agents.defaults.workspace = "/workspace"`: 使用容器内路径

---

## 配置模式对比

### 激进模式 vs 安全模式

根据你的使用场景，选择合适的配置策略：

#### 🔓 激进模式（零门槛）

**适用场景**：
- 开发测试环境
- 内网隔离环境
- 快速上手学习
- 个人本地使用

**核心配置**：
```json
{
  "gateway": {
    "bind": "lan",                    // 局域网可访问
    "auth": {
      "mode": "none"                  // 无需认证
    },
    "controlUi": {
      "dangerouslyDisableDeviceAuth": true
    }
  },
  "channels": {
    "feishu": {
      "dmPolicy": "open",             // 私聊开放
      "groupPolicy": "open"           // 群聊开放
    }
  }
}
```

**优点**：
- ✅ 零配置门槛，即开即用
- ✅ 无需记住 Token
- ✅ 飞书机器人无需配对，拉群即用
- ✅ 减少新手困惑

**风险**：
- ⚠️ 任何能访问网络的人都可以控制实例
- ⚠️ 任何人都可以通过飞书机器人对话（可能产生 API 费用）
- ⚠️ 无法追踪谁在使用

---

#### 🔐 安全模式（推荐）

**适用场景**：
- 生产环境
- 公网访问
- 团队协作
- 需要审计日志

**核心配置**：
```json
{
  "gateway": {
    "bind": "loopback",               // 仅本地访问
    "auth": {
      "mode": "token",                // Token 认证
      "token": "your-random-token"
    },
    "controlUi": {
      "dangerouslyDisableDeviceAuth": false
    }
  },
  "channels": {
    "feishu": {
      "dmPolicy": "pairing",          // 私聊需配对
      "groupPolicy": "pairing"        // 群聊需配对
    }
  }
}
```

**优点**：
- ✅ 保护实例不被未授权访问
- ✅ 控制谁可以使用飞书机器人
- ✅ 避免意外的 API 费用
- ✅ 可以追踪使用者

**缺点**：
- ❌ 需要配置和记住 Token
- ❌ 飞书使用前需要管理员批准配对
- ❌ 配置稍复杂

---

#### 🎯 混合模式（平衡）

结合两者优点，适合小团队：

**核心配置**：
```json
{
  "gateway": {
    "bind": "lan",                    // 局域网可访问（方便）
    "auth": {
      "mode": "token",                // 需要 Token（安全）
      "token": "shared-team-token"
    },
    "controlUi": {
      "dangerouslyDisableDeviceAuth": true
    }
  },
  "channels": {
    "feishu": {
      "dmPolicy": "open",             // 私聊开放（方便）
      "groupPolicy": "pairing"        // 群聊需配对（控制范围）
    }
  }
}
```

**平衡点**：
- ✅ Control UI 需要 Token（防止外人访问）
- ✅ 私聊开放（团队成员可以直接用）
- ✅ 群聊需配对（控制机器人被拉入哪些群）

---

### 配置决策树

```
Q: 你的实例会暴露在公网吗？
├─ 是 → 必须使用【安全模式】
└─ 否（仅内网）
   └─ Q: 是否多人使用？
      ├─ 是 → 推荐【混合模式】或【安全模式】
      └─ 否（个人使用）→ 可以使用【激进模式】
```

---

### 三种模式快速对比

#### 配置项对比

**网关配置**：
```
激进模式：bind=loopback, auth.mode=none（完全无认证）
          Docker 模式: +Nginx 代理实现局域网访问
混合模式：bind=lan, auth.mode=token（自定义token）
安全模式：bind=loopback, auth.mode=token（强token + 仅本机）
```

**飞书配置**：
```
激进模式：dmPolicy=open, groupPolicy=open
混合模式：dmPolicy=open, groupPolicy=pairing
安全模式：dmPolicy=pairing, groupPolicy=pairing
```

**设备认证**：
```
激进模式：dangerouslyDisableDeviceAuth=true
混合模式：dangerouslyDisableDeviceAuth=true
安全模式：dangerouslyDisableDeviceAuth=false
```

#### 使用体验对比

**Control UI 访问**：
```
激进模式：http://localhost:18900 → 直接进入
混合模式：http://localhost:18900/#token=xxx → 需要 Token
安全模式：http://localhost:18900/#token=xxx → 需要 Token + 设备绑定
```

**飞书私聊**：
```
激进模式：发消息 → 立即响应
混合模式：发消息 → 立即响应
安全模式：发消息 → 提示需要配对 → 管理员批准 → 可用
```

**飞书群聊**：
```
激进模式：拉机器人进群 → 立即可用
混合模式：拉机器人进群 → 提示需要配对 → 管理员批准 → 可用
安全模式：拉机器人进群 → 提示需要配对 → 管理员批准 → 可用
```

---

### 实际操作建议

#### 🎓 学习阶段（推荐：激进模式）

**为什么**：
- 减少配置门槛
- 避免"为什么不工作"的困惑
- 快速看到效果，建立信心

**配置清单**：
- [ ] `gateway.bind = "loopback"`
- [ ] `gateway.port = 3000`（Docker 模式）
- [ ] `gateway.auth.mode = "none"`
- [ ] `channels.feishu.dmPolicy = "open"`
- [ ] `channels.feishu.groupPolicy = "open"`
- [ ] `gateway.controlUi.dangerouslyDisableDeviceAuth = true`
- [ ] Docker 模式：使用 Nginx 代理（见 [激进模式-Nginx代理方案.md](./激进模式-Nginx代理方案.md)）

---

#### 🚀 生产部署（必须：安全模式）

**为什么**：
- 保护 API 费用
- 审计使用者
- 防止滥用

**配置清单**：
- [ ] `gateway.auth.mode = "token"`
- [ ] `gateway.auth.token = "生成随机32字符"`
- [ ] `gateway.bind = "loopback"` 或配置防火墙
- [ ] `channels.feishu.dmPolicy = "pairing"`
- [ ] `channels.feishu.groupPolicy = "pairing"`
- [ ] `controlUi.dangerouslyDisableDeviceAuth = false`

---

#### 👥 团队协作（推荐：混合模式）

**为什么**：
- 平衡便利性和安全性
- 团队成员可以直接私聊
- 控制机器人被拉入哪些群

**配置清单**：
- [ ] `gateway.auth.mode = "token"` + 分享 Token 给团队
- [ ] `gateway.bind = "lan"`
- [ ] `channels.feishu.dmPolicy = "open"`
- [ ] `channels.feishu.groupPolicy = "pairing"`
- [ ] `controlUi.dangerouslyDisableDeviceAuth = true`

---

## 快速切换配置模式

### 如何启用"激进模式"（零门槛）

如果你已有一个实例，想要切换到激进模式（无需认证、无需配对），按以下步骤操作：

#### 步骤 1：修改网关认证

在 `<workspace>/<instance>/.openclaw/openclaw.json` 中修改：

```json
{
  "gateway": {
    "bind": "lan",                    // 改为局域网访问
    "auth": {
      "mode": "none"                  // 改为无认证
    },
    "controlUi": {
      "dangerouslyDisableDeviceAuth": true  // 禁用设备认证
    }
  }
}
```

#### 步骤 2：修改渠道策略

在同一文件中修改渠道配置：

```json
{
  "channels": {
    "feishu": {
      "appId": "cli_xxxxxxxxxxxx",
      "appSecret": "your-app-secret",
      "enabled": true,
      "dmPolicy": "open",             // 改为开放模式
      "groupPolicy": "open",          // 改为开放模式
      "accounts": {
        "bot_002": {
          "appId": "cli_yyyyyyyyyyyy",
          "appSecret": "another-secret",
          "dmPolicy": "open",         // 多账号也改为开放
          "groupPolicy": "open"
        }
      }
    }
  }
}
```

#### 步骤 3：重启实例

```bash
python skills/openclaw-manager/scripts/instance_manager.py restart <实例名>
```

#### 步骤 4：验证配置

**Control UI**：
- 访问 `http://127.0.0.1:18900`（或你的端口）
- 无需输入 Token，直接进入

**飞书渠道**：
- 直接私聊机器人，立即响应（无需配对）
- 拉机器人进群，立即可用（无需批准）

---

### 如何从"激进模式"切换回"安全模式"

#### 步骤 1：启用网关认证

```json
{
  "gateway": {
    "bind": "loopback",               // 改为仅本地访问
    "auth": {
      "mode": "token",                // 改为 Token 认证
      "token": "生成一个随机token"    // 添加 Token
    },
    "controlUi": {
      "dangerouslyDisableDeviceAuth": false  // 启用设备认证
    }
  }
}
```

**生成 Token 的方法**：
```bash
# macOS/Linux
openssl rand -hex 32

# 或使用 Python
python3 -c "import secrets; print(secrets.token_hex(32))"
```

#### 步骤 2：启用配对模式

```json
{
  "channels": {
    "feishu": {
      "dmPolicy": "pairing",          // 改为配对模式
      "groupPolicy": "pairing"        // 改为配对模式
    }
  }
}
```

#### 步骤 3：重启实例并批准配对

```bash
# 重启实例
python skills/openclaw-manager/scripts/instance_manager.py restart <实例名>

# 批准配对请求
python skills/openclaw-channel/scripts/channel_manager.py approve-pairing <实例名> feishu
```

---

## 配置验证

OpenClaw 使用 Zod 进行配置验证。如果配置有误，启动时会报错并提示具体的问题。

### 常见验证错误

1. **模型引用不存在**
   ```
   Error: Unknown model "openai/gpt-5"
   ```
   解决：确保模型 ID 在 `models.providers.<provider>.models` 中定义

2. **智能体 ID 重复**
   ```
   Error: Duplicate agent id "test-agent"
   ```
   解决：确保 `agents.list` 中的 `id` 唯一

3. **绑定引用不存在的智能体**
   ```
   Error: Unknown agent id "non-existent-agent" in bindings
   ```
   解决：确保 `bindings[].agentId` 在 `agents.list` 中存在

4. **必填字段缺失**
   ```
   Error: models.providers.openai.baseUrl is required
   ```
   解决：补充必填字段

---

## 配置最佳实践

### 1. 使用密钥引用

**不推荐**：
```json
{
  "models": {
    "providers": {
      "openai": {
        "apiKey": "sk-xxxxxxxxxxxx"
      }
    }
  }
}
```

**推荐**：
```json
{
  "models": {
    "providers": {
      "openai": {
        "apiKey": {
          "source": "env",
          "provider": "default",
          "id": "OPENAI_API_KEY"
        }
      }
    }
  }
}
```

### 2. 分离环境配置

不同环境（开发/生产）使用不同的配置文件或环境变量。

### 3. 使用 comment 字段

在 `bindings` 中使用 `comment` 字段记录路由规则的意图：

```json
{
  "bindings": [
    {
      "agentId": "support-agent",
      "match": {
        "channel": "feishu"
      },
      "comment": "飞书默认路由 - 客服智能体"
    }
  ]
}
```

### 4. 渐进式配置

从最小化配置开始，逐步添加功能：
1. 先配置 `models` 和 `agents.defaults`
2. 再配置 `channels` 和 `plugins`
3. 最后配置 `bindings` 和高级功能

---

## 常见问题 FAQ

### Q1: 为什么飞书机器人一直提示需要配对？

**原因**：渠道配置使用了 `"pairing"` 模式。

**解决方案**：

**方案 A：改为开放模式（激进）**
```json
{
  "channels": {
    "feishu": {
      "dmPolicy": "open",
      "groupPolicy": "open"
    }
  }
}
```
重启实例后，直接可用。

**方案 B：批准配对请求（安全）**
```bash
python skills/openclaw-channel/scripts/channel_manager.py approve-pairing <实例名> feishu
python skills/openclaw-manager/scripts/instance_manager.py restart <实例名>
```

---

### Q2: 为什么访问 Control UI 提示 token mismatch？

**原因**：`gateway.auth.mode = "token"` 但 URL 中没有携带 token。

**解决方案**：

**方案 A：使用正确的 URL（安全）**
```
http://127.0.0.1:18900/#token=你的token值
```

**方案 B：关闭认证（激进）**
```json
{
  "gateway": {
    "auth": {
      "mode": "none"
    }
  }
}
```
重启后直接访问 `http://127.0.0.1:18900`

---

### Q3: Docker 容器中如何访问 Control UI？

**问题**：容器内绑定 `0.0.0.0`，但外部访问报错。

**解决方案**：
```json
{
  "gateway": {
    "bind": "custom",
    "customBindHost": "0.0.0.0",
    "trustedProxies": ["172.24.0.0/16"],
    "controlUi": {
      "allowedOrigins": [
        "http://localhost:18900",
        "http://127.0.0.1:18900"
      ],
      "dangerouslyDisableDeviceAuth": true
    },
    "auth": {
      "mode": "none"                  // Docker 环境建议无认证
    }
  }
}
```

---

### Q4: 如何让多个智能体使用不同的模型？

**配置示例**：
```json
{
  "agents": {
    "defaults": {
      "model": {
        "primary": "bailian/qwen3.5-plus"
      }
    },
    "list": [
      {
        "id": "general-agent",
        "name": "通用助手"
        // 继承 defaults，使用 qwen3.5-plus
      },
      {
        "id": "coding-agent",
        "name": "编程助手",
        "model": {
          "primary": "bailian/qwen3-coder-plus"  // 覆盖为编程模型
        }
      },
      {
        "id": "long-context-agent",
        "name": "长文档助手",
        "model": {
          "primary": "bailian/kimi-k2.5"  // 覆盖为长上下文模型
        }
      }
    ]
  }
}
```

---

### Q5: 为什么配置了 `models` 字典但无法切换模型？

**原因**：可能是以下之一：
1. 模型名称拼写错误
2. 模型引用格式错误（缺少 `provider/`）
3. 该模型未在 `models.providers` 中定义

**排查步骤**：

1. 检查模型是否在 providers 中定义：
```json
{
  "models": {
    "providers": {
      "bailian": {
        "models": [
          { "id": "qwen3.5-plus", ... }  // 必须存在
        ]
      }
    }
  }
}
```

2. 检查 `agents.defaults.models` 引用格式：
```json
{
  "agents": {
    "defaults": {
      "models": {
        "bailian/qwen3.5-plus": {}  // 注意：provider/model-id
      }
    }
  }
}
```

3. 使用 `/model` 指令测试：
```
/model bailian/qwen3.5-plus    ✓ 正确
/model qwen3.5-plus            ✗ 错误（缺少 provider）
```

---

### Q6: `model.primary` 和 `models` 有什么关系？

**关系**：
- `model.primary` 是**初始使用的模型**
- `models` 是**可以切换到的模型池**
- `primary` **必须**在 `models` 中存在

**正确配置**：
```json
{
  "model": {
    "primary": "bailian/qwen3.5-plus"  // 初始模型
  },
  "models": {
    "bailian/qwen3.5-plus": {},        // ✓ primary 必须在这里
    "bailian/kimi-k2.5": {}            // 可选的其他模型
  }
}
```

**错误配置**：
```json
{
  "model": {
    "primary": "bailian/qwen3.5-plus"  // 初始模型
  },
  "models": {
    "bailian/kimi-k2.5": {}            // ✗ primary 不在这里！
  }
}
```
会报错：`Unknown model "bailian/qwen3.5-plus"`

---

## 总结

`openclaw.json` 是 OpenClaw 的核心配置文件，通过理解其结构和字段含义，你可以：
- ✅ 配置多个 AI 模型提供商
- ✅ 创建和管理多个智能体
- ✅ 连接飞书、QQ、企微等消息平台
- ✅ 设置灵活的消息路由规则
- ✅ 控制访问权限和安全策略
- ✅ 在开发和生产环境间灵活切换

**关键要点**：
1. 配置由 Zod Schema 严格验证，错误会在启动时提示
2. 大部分字段都有合理的默认值，可以渐进式配置
3. 敏感信息（API Key、Token）建议使用密钥引用而非明文
4. Docker 环境需要特殊的网关配置（bind、trustedProxies 等）
5. 根据使用场景选择合适的配置模式（激进/混合/安全）

**配置模式选择建议**：
- 🎓 **学习阶段** → 激进模式（零门槛，快速上手）
- 👥 **团队协作** → 混合模式（便利性和安全性平衡）
- 🚀 **生产部署** → 安全模式（完整的访问控制）

---

**文档作者**: OpenClaw 管理助手  
**最后更新**: 2026-03-12  
**源码版本**: OpenClaw 2026.3.11
