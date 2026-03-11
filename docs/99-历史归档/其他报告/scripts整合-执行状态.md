# Scripts 整合 - 执行状态

> **开始时间**: 2026-03-11  
> **状态**: 进行中  
> **目标**: 将根目录 scripts/ 整合到技能包，删除外部脚本

---

## 📋 整合任务清单

### ✅ 已完成

- [x] 制定整合方案
- [x] 用户确认方案

---

### 🚧 进行中

#### 任务 1: health_check.py → openclaw-manager

**源文件**: `scripts/health_check.py` (255行)  
**目标**: `skills/openclaw-manager/scripts/instance_manager.py`

**需要添加的方法**:
```python
class InstanceManager:
    # 新增方法
    def health_check(self, instance_name: Optional[str] = None) -> Dict[str, Any]:
        """
        健康检查
        
        Args:
            instance_name: 实例名称（None=检查所有）
        
        Returns:
            检查结果
        """
        pass
    
    def _check_naming_convention(self, name: str) -> Tuple[bool, str]:
        """检查命名规范"""
        pass
    
    def _check_pairing_status(self, instance_path: Path) -> Tuple[bool, str]:
        """检查配对状态"""
        pass
    
    def _check_model_config(self, instance_path: Path) -> Tuple[bool, str]:
        """检查模型配置"""
        pass
```

**新增命令**:
```bash
python skills/openclaw-manager/scripts/instance_manager.py health-check
python skills/openclaw-manager/scripts/instance_manager.py health-check openclaw-feishu-demo
```

---

#### 任务 2: approve_feishu_pairing.py → openclaw-channel

**源文件**: `scripts/approve_feishu_pairing.py` (187行)  
**目标**: `skills/openclaw-channel/scripts/channel_manager.py`

**需要添加的方法**:
```python
class ChannelManager:
    # 新增方法
    def approve_pairing(self, instance_name: str, platform: str = 'feishu', 
                       auto_restart: bool = True) -> bool:
        """
        批准配对请求
        
        Args:
            instance_name: 实例名称
            platform: 平台（feishu/qq/wecom/dingtalk）
            auto_restart: 是否自动重启实例
        
        Returns:
            是否成功
        """
        pass
    
    def _read_pairing_requests(self, instance_path: Path, platform: str) -> List[Dict]:
        """读取配对请求"""
        pass
    
    def _approve_user(self, instance_path: Path, platform: str, user_id: str) -> bool:
        """批准用户"""
        pass
```

**新增命令**:
```bash
python skills/openclaw-channel/scripts/channel_manager.py approve-pairing \
  --instance openclaw-feishu-demo \
  --platform feishu
```

---

#### 任务 3: fix_all_models.py → openclaw-model

**源文件**: `scripts/fix_all_models.py` (178行)  
**目标**: `skills/openclaw-model/scripts/model_manager.py`

**需要添加的方法**:
```python
class ModelManager:
    # 新增方法
    def fix_config(self, instance_name: Optional[str] = None) -> Dict[str, Any]:
        """
        修复模型配置
        
        Args:
            instance_name: 实例名称（None=所有实例）
        
        Returns:
            修复结果
        """
        pass
    
    def _fix_instance_config(self, instance_path: Path, global_models: dict) -> bool:
        """修复单个实例"""
        pass
    
    def _sync_models_config(self, instance_path: Path) -> bool:
        """同步模型配置"""
        pass
```

**新增命令**:
```bash
python skills/openclaw-model/scripts/model_manager.py fix-config
python skills/openclaw-model/scripts/model_manager.py fix-config openclaw-feishu-demo
```

---

### 📦 待归档

- [ ] `scripts/clean_hardcoded_paths.py` → `docs/99-历史归档/工具/`
- [ ] `scripts/orchestrator.py` → `docs/99-历史归档/工具/`
- [ ] 删除 `scripts/` 目录

---

### 📝 待更新文档

#### AGENTS.md
- [ ] 删除"辅助工具（scripts/）"部分
- [ ] 更新技能包功能说明
- [ ] 添加新增命令

#### 技能包 SKILL.md
- [ ] `skills/openclaw-manager/SKILL.md` - 添加 health-check
- [ ] `skills/openclaw-channel/SKILL.md` - 添加 approve-pairing
- [ ] `skills/openclaw-model/SKILL.md` - 添加 fix-config

#### 问题解决文档
- [ ] `docs/02-问题解决/飞书配对-真正的解决方案.md` - 更新命令
- [ ] `docs/02-问题解决/模型Unknown问题-解决方案.md` - 更新命令
- [ ] `docs/02-问题解决/README.md` - 更新索引

---

## 🎯 执行计划

### 阶段 1: 整合功能（预计 2-3 小时）

1. **整合 health_check** 
   - 复制 HealthChecker 类到 instance_manager.py
   - 添加 health-check 命令到 argparse
   - 测试功能

2. **整合 approve_pairing**
   - 复制 approve_pairing 函数到 channel_manager.py
   - 重构为类方法
   - 添加 approve-pairing 命令
   - 测试功能

3. **整合 fix_config**
   - 复制 fix_instance_model_config 到 model_manager.py
   - 重构为类方法
   - 添加 fix-config 命令
   - 测试功能

---

### 阶段 2: 清理和归档（预计 30分钟）

1. **归档临时工具**
   ```bash
   mkdir -p docs/99-历史归档/工具
   mv scripts/clean_hardcoded_paths.py docs/99-历史归档/工具/
   mv scripts/orchestrator.py docs/99-历史归档/工具/
   ```

2. **删除 scripts/ 目录**
   ```bash
   # 先移动已整合的脚本到归档
   mv scripts/health_check.py docs/99-历史归档/工具/
   mv scripts/approve_feishu_pairing.py docs/99-历史归档/工具/
   mv scripts/fix_all_models.py docs/99-历史归档/工具/
   
   # 删除 scripts/ 目录
   rm -rf scripts/
   ```

---

### 阶段 3: 更新文档（预计 1小时）

1. **更新 AGENTS.md**
   - 删除"技能包 vs 辅助工具"部分
   - 更新技能包功能列表
   - 添加新增命令示例

2. **更新技能包 SKILL.md**
   - 每个技能包添加新功能说明

3. **更新问题解决文档**
   - 修改所有引用外部脚本的地方
   - 更新命令示例

---

### 阶段 4: 测试验证（预计 1小时）

1. **测试新增命令**
   ```bash
   # 健康检查
   python skills/openclaw-manager/scripts/instance_manager.py health-check
   
   # 配对批准
   python skills/openclaw-channel/scripts/channel_manager.py approve-pairing \
     --instance openclaw-feishu-demo
   
   # 配置修复
   python skills/openclaw-model/scripts/model_manager.py fix-config
   ```

2. **验证文档**
   - 检查所有文档链接
   - 验证命令正确性

---

## 🚧 当前阻塞点

**需要用户确认**:
1. 是否立即开始执行整合？
2. 是否需要保留 scripts/ 中的脚本作为备份，还是直接移到归档？
3. 测试环境是否准备好？（需要有可测试的实例）

---

## 💡 建议

### 方案 A: 逐步整合（推荐）

**优势**:
- 风险低，每完成一个测试一个
- 发现问题可及时调整
- 保留旧脚本作为参考

**步骤**:
1. 整合 health_check → 测试 → 归档旧脚本
2. 整合 approve_pairing → 测试 → 归档旧脚本
3. 整合 fix_config → 测试 → 归档旧脚本
4. 更新所有文档
5. 删除 scripts/

---

### 方案 B: 一次性整合

**优势**:
- 快速完成
- 一次性解决问题

**劣势**:
- 风险高
- 出问题难以定位

---

## 📊 预期结果

### 整合前
```
项目/
├── skills/              # 功能不完整
└── scripts/             # ❌ 5个外部脚本
    ├── health_check.py
    ├── approve_feishu_pairing.py
    ├── fix_all_models.py
    ├── clean_hardcoded_paths.py
    └── orchestrator.py
```

### 整合后
```
项目/
├── skills/              # ✅ 完整功能
│   ├── openclaw-manager/
│   │   └── scripts/instance_manager.py  (包含 health-check)
│   ├── openclaw-channel/
│   │   └── scripts/channel_manager.py   (包含 approve-pairing)
│   └── openclaw-model/
│       └── scripts/model_manager.py     (包含 fix-config)
│
└── docs/
    └── 99-历史归档/工具/  # ✅ 旧脚本归档
```

---

## ❓ 下一步

**用户决策**:
1. ✅ 采用方案A（逐步整合）还是方案B（一次性整合）？
2. ✅ 现在开始执行，还是需要先准备测试环境？
3. ✅ 旧脚本是否需要保留备份？

---

**状态**: 等待用户确认  
**更新时间**: 2026-03-11
