# AGENTS.md 配置说明

> **AGENTS.md 是整个技能包平台激活的核心入口文件**

## 🎯 文件重要性

### 为什么 AGENTS.md 如此重要？

`AGENTS.md` 是 **Cursor IDE 读取的第一个文件**，它定义了：

1. **如何与用户交互** - AI 助手的角色和对话风格
2. **如何识别意图** - 将用户的自然语言映射到具体操作
3. **如何编排流程** - 自动串联多个技能包完成复杂任务
4. **如何智能决策** - 自动选择合适的配置和参数
5. **如何处理错误** - 友好的错误提示和智能恢复

### 与技能包的关系

```
AGENTS.md (入口)
    ↓
  意图识别
    ↓
┌─────────────────────────────────┐
│  调度 6 个技能包                 │
│  - openclaw-manager (安装/管理)  │
│  - openclaw-deploy (部署)        │
│  - openclaw-plugin (插件)        │
│  - openclaw-channel (渠道)       │
│  - openclaw-model (模型)         │
│  - openclaw-agent (智能体)       │
└─────────────────────────────────┘
    ↓
  自动流程编排
    ↓
  执行并反馈结果
```

---

## 🧠 核心设计理念

### 理念 1: 用户只需表达意图

**传统方式**（不好）:
```
用户: 创建实例
AI: 请使用以下命令：
    python instance_manager.py create \
      --name xxx \
      --workspace-path /path/to/workspace \
      --log-level INFO
```

**智能方式**（好）:
```
用户: 创建实例
AI: 好的！给实例起个名字吧？（或者我帮你生成 openclaw-prod-01）
用户: 就叫 prod-01
AI: ✅ 实例 'openclaw-prod-01' 已创建！
```

### 理念 2: 自动流程编排

当用户说"创建一个飞书机器人"时，AI 应该自动串联 7 个步骤：

```
用户意图: "创建飞书客服机器人"
           ↓
自动流程:
  [1/7] openclaw-manager    → 创建实例
  [2/7] openclaw-plugin     → 安装飞书插件
  [3/7] openclaw-channel    → 配置飞书渠道（询问凭证）
  [4/7] openclaw-model      → 添加 GPT-3.5（自动选择）
  [5/7] openclaw-agent      → 创建客服智能体
  [6/7] openclaw-agent      → 绑定模型和渠道
  [7/7] openclaw-manager    → 启动实例
           ↓
结果反馈: "✅ 飞书客服机器人已就绪！"
```

**用户只看到**：询问凭证 + 最终结果  
**AI 自动完成**：7个技术步骤

### 理念 3: 智能参数决策

AI 应该自动决策大部分参数，只询问必需信息：

| 参数 | AI决策 | 询问用户？ | 理由 |
|-----|--------|-----------|-----|
| 实例名称 | openclaw-prod-01 | 可选 | 可自动生成 |
| 工作空间路径 | 读取 global.yaml | ❌ | 配置文件已定义 |
| 部署模式 | 根据环境自动选择 | ❌ | 开发用主机，生产用Docker |
| AI模型 | 根据用途自动选择 | ❌ | 客服用3.5，技术用4 |
| 日志级别 | INFO | ❌ | 标准配置 |
| App ID | - | ✅ | 必需，无法推测 |
| API Key | - | ✅ | 必需，无法推测 |

---

## 📐 AGENTS.md 结构解析

### 第1部分: 核心能力定义

```markdown
## 🎯 你的核心能力

### 智能意图识别
- ✅ 理解用户意图（创建、部署、配置、查看状态等）
- ✅ 自动决策技术方案（选择合适的工具和配置）
- ✅ 编排执行流程（调用多个技能包完成复杂任务）
```

**作用**: 告诉 Cursor AI "你是谁"、"你能做什么"

### 第2部分: 技能包清单

```markdown
## 📚 可用的技能包（自动加载）

### 🔧 openclaw-manager（P0 核心）
**路径**: `.cursor/skills/openclaw-manager/SKILL.md`  
**功能**: OpenClaw 安装、实例创建和生命周期管理  
**何时使用**: 
- 用户说"安装"、"创建实例"、"启动"、"查看状态"
```

**作用**: 定义有哪些技能包、什么时候使用

### 第3部分: 意图识别规则表 🔥

```markdown
## 🔍 意图识别规则表

| 用户表达 | 识别为 | 调用技能包 | 自动决策 |
|---------|--------|-----------|---------|
| "创建实例" | CREATE_INSTANCE | manager | 命名规范 |
| "我想要飞书机器人" | CREATE_WITH_PLATFORM | manager+plugin+channel | 平台=飞书 |
```

**作用**: **最关键！** 将用户语言映射到具体操作

### 第4部分: 自动流程编排

```markdown
### 模式2: 多步编排（Complex）

**用户说**: "创建一个飞书客服机器人"

**执行**:
阶段1: 信息收集 → 询问必需信息
阶段2: 自动决策 → 选择模型、部署方式
阶段3: 流程编排 → 7步自动串联
阶段4: 验证 → 健康检查
阶段5: 反馈 → 友好告知结果
```

**作用**: 定义复杂任务如何拆解和执行

### 第5部分: 智能决策表

```markdown
| 场景 | 用户意图 | 自动决策 | 说明 |
|------|---------|---------|------|
| 创建实例 | 没说环境 | openclaw-prod-01 | 默认生产 |
| 选择模型 | 没说具体 | 客服→gpt-3.5<br>技术→gpt-4 | 根据用途 |
```

**作用**: AI 如何"猜"用户想要什么

### 第6部分: 对话模板

```markdown
用户: 创建一个实例

你: 好的！我来帮您创建...
    请告诉我：
    1️⃣ 名字？
    2️⃣ 用途？
    3️⃣ 对接平台？
```

**作用**: 标准化对话风格，保持一致性

### 第7部分: 工具调用路径

```python
# 创建实例
python skills/openclaw-manager/scripts/instance_manager.py create <id>

# 配置渠道
python skills/openclaw-channel/scripts/channel_manager.py add ...
```

**作用**: 告诉 AI 如何调用底层工具

---

## 🎯 意图识别的工作原理

### 示例 1: "创建一个飞书机器人"

**步骤 1: 关键词提取**
```
关键词:
  - "创建" → 创建类意图
  - "飞书" → 平台类型
  - "机器人" → 目标对象
```

**步骤 2: 意图映射**
```
意图识别表查询:
  "创建" + "平台" → CREATE_WITH_PLATFORM
```

**步骤 3: 技能包选择**
```
CREATE_WITH_PLATFORM 需要:
  ✅ openclaw-manager  (创建实例)
  ✅ openclaw-plugin   (安装平台插件)
  ✅ openclaw-channel  (配置渠道)
```

**步骤 4: 参数决策**
```
自动决策:
  - platform = "feishu" (从关键词"飞书"推断)
  - instance_name = "openclaw-prod-01" (自动生成)
  - deploy_mode = "host" (默认)
  
需要询问:
  - app_id, app_secret (无法推断)
```

**步骤 5: 流程编排**
```
执行序列:
  1. create_instance()
  2. install_plugin(platform="feishu")
  3. 询问 app_id/app_secret
  4. configure_channel(加密凭证)
  5. start_instance()
```

### 示例 2: "查看状态"

**简单意图，直接执行**:
```
关键词: "查看"、"状态"
  ↓
意图: LIST_INSTANCES
  ↓
调用: openclaw-manager list
  ↓
格式化输出 → 反馈用户
```

---

## 🔄 自动流程编排的实现

### 复杂任务的拆解

**用户需求**: "创建飞书客服机器人"

**AI 的执行计划**:

```python
# 伪代码示例
def handle_create_feishu_chatbot(user_input):
    # 阶段1: 信息收集
    name = ask_or_generate_name()
    app_id, app_secret = ask_feishu_credentials()
    
    # 阶段2: 自动决策
    model = "gpt-3.5-turbo"  # 客服场景自动选择
    deploy_mode = "host"      # 默认主机模式
    
    # 阶段3: 流程编排
    console.print("⏳ [1/7] 创建实例...")
    result1 = create_instance(name)
    
    console.print("✅ [2/7] 安装飞书插件...")
    result2 = install_plugin(name, "feishu")
    
    console.print("✅ [3/7] 配置渠道（凭证加密）...")
    result3 = configure_channel(name, "feishu", app_id, app_secret)
    
    console.print("✅ [4/7] 添加 GPT-3.5 模型...")
    result4 = add_model(name, model, provider="openai")
    
    console.print("✅ [5/7] 创建客服智能体...")
    result5 = create_agent(name, "customer-service")
    
    console.print("✅ [6/7] 绑定配置...")
    result6 = bind_agent_model_channel(name, "customer-service", model, "feishu")
    
    console.print("✅ [7/7] 启动实例...")
    result7 = start_instance(name)
    
    # 阶段4: 验证
    health = health_check(name)
    
    # 阶段5: 友好反馈
    return f"""
    🎉 飞书客服机器人已创建完成！
    
    📋 实例信息：
    - 名称: {name}
    - 状态: ✅ 运行中
    - 平台: 飞书
    - 模型: GPT-3.5 Turbo
    
    🚀 下一步：
    在飞书中 @你的机器人 测试吧！
    """
```

**关键点**:
- 用户只看到最少的询问（App ID/Secret）
- AI 自动完成 7 个技术步骤
- 结果用友好语言呈现

---

## 📊 意图识别覆盖度

### 创建类意图（4种）

| 意图 | 关键词 | 技能包数量 |
|-----|--------|-----------|
| CREATE_INSTANCE | 创建、实例 | 1 |
| CREATE_WITH_PLATFORM | 创建、飞书/QQ等 | 3 |
| CREATE_SERVICE | 搭建、系统 | 6 |
| DEPLOY_PRODUCTION | 部署、生产 | 2 |

### 查询类意图（4种）

| 意图 | 关键词 | 响应方式 |
|-----|--------|---------|
| LIST_INSTANCES | 查看、所有 | 列表展示 |
| INSTANCE_STATUS | 状态、xxx | 详细信息 |
| VIEW_LOGS | 日志、查看 | 实时流 |
| HEALTH_CHECK | 健康、检查 | 健康报告 |

### 配置类意图（3种）

| 意图 | 关键词 | 处理方式 |
|-----|--------|---------|
| ADD_CHANNEL | 添加、渠道 | 询问凭证→加密 |
| ADD_MODEL | 添加、模型、GPT | 询问Key→配置 |
| CREATE_AGENT | 创建、智能体 | 识别角色→配置 |

### 操作类意图（4种）

| 意图 | 关键词 | 执行动作 |
|-----|--------|---------|
| START_INSTANCE | 启动、start | 启动实例 |
| STOP_INSTANCE | 停止、stop | 停止实例 |
| RESTART_INSTANCE | 重启、restart | 重启实例 |
| DELETE_INSTANCE | 删除、delete | 确认后删除 |

**总计**: **15种意图** 覆盖所有常见操作

---

## 🎨 对话风格设计

### 原则: 像真人管家一样

**✅ 好的对话**:
```
用户: 创建实例
AI: 好的！我来帮您创建。给实例起个名字？（建议：openclaw-prod-01）
```

**❌ 不好的对话**:
```
用户: 创建实例
AI: 执行命令: python instance_manager.py create
    参数:
      --name: 必填
      --workspace-path: 可选
```

### 隐藏技术细节

| 技术术语 | 用户友好语言 |
|---------|-------------|
| `instance_manager.py create` | "正在创建实例..." |
| `--workspace-path /path` | "使用默认工作空间" |
| `exit code 0` | "✅ 创建成功！" |
| `Port 3000 EADDRINUSE` | "端口 3000 被占用，我帮您用 3001 可以吗？" |

---

## 🎯 智能决策表详解

### 决策维度 1: 环境识别

```
用户说话内容                     识别为        决策
───────────────────────────────────────────────────────
"创建一个测试实例"              → 测试环境   → openclaw-test-01
"部署到生产"                    → 生产环境   → openclaw-prod-01
未明确说明                      → 生产环境   → openclaw-prod-01（默认）
```

### 决策维度 2: 模型选择

```
用途                           自动选择的模型        理由
─────────────────────────────────────────────────────────────
客服、咨询                    gpt-3.5-turbo       快速响应，成本低
技术支持、编程                gpt-4               专业、准确
内容创作、写作                gpt-4               创造力强
翻译                          gpt-3.5-turbo       足够准确，成本低
用户未说明                    gpt-3.5-turbo       通用默认
```

### 决策维度 3: 部署模式

```
场景                           自动选择           理由
───────────────────────────────────────────────────────
开发/测试                     主机模式(host)     快速启动，便于调试
生产环境                      Docker             隔离性好，易于管理
用户说"集群"、"高可用"        K8s               支持扩展和自动恢复
用户未说明                    主机模式           默认最简单方式
```

### 决策维度 4: 命名规范

```
场景                           命名规则           示例
──────────────────────────────────────────────────────────
用户提供名称                  使用用户名称        my-bot
用户未提供+生产环境           openclaw-prod-XX    openclaw-prod-01
用户未提供+测试环境           openclaw-test-XX    openclaw-test-01
批量创建                      基础名-序号         openclaw-test-01/02/03
```

---

## 🔧 工具调用策略

### 策略 1: 静默执行

**原则**: AI 执行工具时，不展示命令本身

```python
# ❌ 不要这样
tell_user("执行: python instance_manager.py create openclaw-prod-01")

# ✅ 应该这样
console.print("⏳ 正在创建实例 openclaw-prod-01...")
run_tool("python instance_manager.py create openclaw-prod-01")
console.print("✅ 实例已创建！")
```

### 策略 2: 智能参数传递

**原则**: 从上下文自动获取参数

```python
# 用户说: "为 prod-01 添加飞书渠道，App ID 是 xxx"

# AI 自动提取:
instance_id = "openclaw-prod-01"  # 从"prod-01"推断
platform = "feishu"                # 从"飞书"推断
app_id = "xxx"                     # 用户明确提供

# 自动调用
add_channel(instance_id, platform, app_id, app_secret=None)  # 会继续询问 secret
```

### 策略 3: 错误智能处理

**原则**: 不展示原始错误，提供解决方案

```python
try:
    start_instance("openclaw-prod-01")
except PortInUseError as e:
    # ❌ 不要直接展示错误
    # raise e
    
    # ✅ 智能处理
    occupying_process = find_process_on_port(3000)
    tell_user(f"""
    ⚠️ 端口 3000 被 {occupying_process} 占用。
    
    我可以帮您：
    1. 停止 {occupying_process}，释放端口
    2. 为新实例使用 3001 端口
    
    您选择哪种？
    """)
```

---

## 🚀 激活和使用

### 激活方式

AGENTS.md 在以下情况会被 Cursor 读取：

1. **项目级激活**
   ```
   项目根目录有 AGENTS.md
   ↓
   Cursor 自动读取
   ↓
   所有 AI 交互都遵循此配置
   ```

2. **通过软链接激活**
   ```
   .cursor/skills/openclaw-*/SKILL.md
   ↓
   AGENTS.md 引用这些技能包
   ↓
   形成完整的技能包系统
   ```

### 使用流程

```
┌─────────────────┐
│  用户打开项目    │
│  启动 Cursor AI  │
└────────┬────────┘
         ↓
┌─────────────────┐
│ Cursor 读取      │
│ AGENTS.md       │
└────────┬────────┘
         ↓
┌─────────────────┐
│ AI 获得能力：    │
│ - 意图识别       │
│ - 流程编排       │
│ - 智能决策       │
└────────┬────────┘
         ↓
┌─────────────────┐
│ 用户用自然语言   │
│ 表达需求         │
└────────┬────────┘
         ↓
┌─────────────────┐
│ AI 自动完成      │
│ 整个流程         │
└─────────────────┘
```

---

## 💡 设计亮点

### 1. 三层意图识别

```
Layer 1: 操作类型识别
  创建/查询/配置/操作

Layer 2: 目标对象识别
  实例/插件/渠道/模型/智能体

Layer 3: 上下文信息提取
  平台类型/环境/用途/名称
```

### 2. 自适应流程

```
简单任务 (如查看状态)
  → Simple 模式 → 1步完成

中等任务 (如创建实例)
  → Complex 模式 → 3-5步串联

复杂任务 (如完整系统)
  → Complex 模式 → 7步串联

不明确任务 (如"我想做个助手")
  → Interactive 模式 → 引导式提问
```

### 3. 渐进式信息收集

```
第1轮对话:
  用户: "创建机器人"
  AI: "好的！用途是什么？" (最重要的信息)

第2轮对话:
  用户: "客服"
  AI: (自动决策: 模型=gpt-3.5, 部署=host)
      "需要对接哪个平台？"

第3轮对话:
  用户: "飞书"
  AI: "飞书的 App ID 和 Secret 是？" (最后的必需信息)
  
第4轮对话:
  用户: 提供凭证
  AI: 自动执行7步 → 完成！
```

**优势**: 每次只问最关键的问题，不一次性抛出大量选项

---

## 📋 最佳实践

### DO ✅

1. **意图识别要宽泛**
   ```
   "创建"、"新建"、"搭建"、"建立" → 都识别为创建意图
   ```

2. **决策要自动**
   ```
   能推断的参数不问用户
   ```

3. **反馈要友好**
   ```
   "✅ 完成！" 而不是 "exit code 0"
   ```

4. **错误要智能**
   ```
   提供解决方案而不是错误堆栈
   ```

### DON'T ❌

1. **不要让用户做技术选择**
   ```
   ❌ "选择部署模式: 1. process  2. docker  3. k8s"
   ✅ 自动决策，或询问"是生产环境吗？"
   ```

2. **不要展示命令**
   ```
   ❌ "执行: python xxx.py --arg value"
   ✅ "正在配置..."
   ```

3. **不要一次问太多问题**
   ```
   ❌ 一次问名称、用途、平台、模型、部署模式...
   ✅ 每次只问最关键的1-2个问题
   ```

---

## 🎓 学习机制

### 从用户行为学习偏好

**会话内学习**:
```
用户第1次: "创建实例 my-bot-01"
用户第2次: "再创建一个"

AI 应该:
  识别命名模式: my-bot-{num}
  自动建议: my-bot-02
```

**跨会话学习**（可选，需持久化）:
```
用户常用:
  - 部署方式: Docker
  - 平台: 飞书
  - 模型: GPT-4

下次自动:
  "您常用飞书和GPT-4，这次也这样配置吗？"
```

---

## 🎯 成功标准

### 用户体验指标

**成功的标志**:
- ✅ 用户需求在 **3 个回合内** 完成
- ✅ 用户没有困惑（不问"什么是 xxx"）
- ✅ 用户没有手动执行命令
- ✅ 用户说"好"、"可以"等表示满意

**失败的标志**:
- ❌ 用户问"怎么操作"
- ❌ 用户抱怨"太复杂"
- ❌ 需要 5 个以上回合才能完成
- ❌ 用户需要查文档

### AI 性能指标

| 指标 | 目标 | 说明 |
|-----|------|------|
| 意图识别准确率 | >90% | 正确识别用户需求 |
| 自动决策率 | >80% | 不需要用户选择 |
| 流程完成率 | >95% | 成功完成完整流程 |
| 平均交互轮数 | <4 | 快速完成任务 |

---

## 🔗 与技能包的协作

### AGENTS.md 的职责

```
AGENTS.md (智能调度层)
  ├── 意图识别
  ├── 智能决策
  ├── 流程编排
  └── 结果呈现
```

### 技能包的职责

```
SKILL.md (执行层)
  ├── 工具定义
  ├── 命令封装
  ├── 参数说明
  └── 使用示例
```

### 协作示例

**AGENTS.md 说**:
```
"用户说'创建飞书机器人'时，调用 openclaw-manager 和 openclaw-plugin"
```

**openclaw-manager/SKILL.md 说**:
```
"我提供 create_instance() 工具，参数是 name, workspace_path"
```

**openclaw-plugin/SKILL.md 说**:
```
"我提供 install_plugin() 工具，参数是 instance, platform"
```

**AI 的执行**:
```python
# 步骤1: AGENTS.md 识别意图 → CREATE_WITH_PLATFORM
# 步骤2: 决策参数 → name=prod-01, platform=feishu
# 步骤3: 调用技能包工具
create_instance(name="openclaw-prod-01", workspace_path=get_from_config())
install_plugin(instance="openclaw-prod-01", platform="feishu")
# 步骤4: 反馈结果
tell_user("✅ 飞书机器人已创建！")
```

---

## 🧪 测试建议

### 功能测试

**测试意图识别**:
```
测试用例 1:
  输入: "创建实例"
  期望: AI 询问名称和用途

测试用例 2:
  输入: "我想要一个飞书机器人"
  期望: AI 识别出平台，询问凭证

测试用例 3:
  输入: "查看状态"
  期望: AI 调用 list 并展示结果
```

**测试自动决策**:
```
测试用例 4:
  场景: 用户说"创建客服机器人"但没说模型
  期望: AI 自动选择 gpt-3.5-turbo

测试用例 5:
  场景: 用户说"部署到生产"但没说模式
  期望: AI 自动选择 Docker
```

**测试流程编排**:
```
测试用例 6:
  场景: "创建飞书客服机器人"
  期望: AI 自动完成 7 步流程，只询问必需信息
```

---

## 📚 相关文档

- [快速开始](快速开始.md) - 5分钟入门
- [使用示例](使用示例.md) - 7个实战场景
- [技能包索引](技能包索引.md) - 所有技能包的详细说明
- [架构设计](架构设计.md) - 系统架构和设计决策

---

## 🌟 核心价值

```
┌──────────────────────────────────────────────┐
│                                              │
│  没有 AGENTS.md:                             │
│    用户需要记命令、传参数、做选择            │
│                                              │
│  有了 AGENTS.md:                             │
│    用户只需说"想要什么"                      │
│    AI 自动理解、决策、执行、反馈             │
│                                              │
│  这就是智能技能包平台的价值！                │
│                                              │
└──────────────────────────────────────────────┘
```

---

**记住**: AGENTS.md 是整个技能包系统的**大脑**，负责理解、决策、编排。技能包是**双手**，负责执行具体操作。🧠🤝✋
