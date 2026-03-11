# 共享工具函数

本目录包含跨技能包使用的通用工具函数。

## 工具列表

### common.py - 通用工具

**主要功能:**
- 实例路径管理（支持可配置的工作空间路径）
- 配置文件加载和保存
- 命令执行
- 实例 ID 验证
- 全局配置管理
- 工作空间目录创建（仅创建顶层目录，不预定义内部结构）

**重要说明:**
- ⚠️ 工作空间路径通过 `global.yaml` 配置，不硬编码
- ⚠️ 我们只创建实例的顶层目录，内部结构由 OpenClaw 管理
- ⚠️ 不同版本的 OpenClaw 可能有不同的内部目录结构

**使用示例:**

```python
from shared.utils.common import OpenClawUtils

utils = OpenClawUtils()

# 获取实例路径
instance_path = utils.get_instance_path("openclaw-prod-01")

# 加载配置
config = utils.load_config(instance_path / "config" / "openclaw.yaml")

# 验证实例 ID
if utils.validate_instance_id("openclaw-prod-01"):
    print("实例 ID 有效")

# 列出所有实例
instances = utils.list_instances()
print(f"共有 {len(instances)} 个实例")
```

### logger.py - 日志工具

**主要功能:**
- 统一的日志格式
- 彩色控制台输出
- 文件日志记录
- 实例专用 logger

**使用示例:**

```python
from shared.utils.logger import setup_logger, get_instance_logger

# 设置基础 logger
logger = setup_logger("my-script", log_level="INFO")
logger.info("脚本开始运行")

# 获取实例专用 logger
instance_logger = get_instance_logger("openclaw-prod-01")
instance_logger.info("实例启动")
```

### crypto.py - 加密工具

**主要功能:**
- 敏感信息加密/解密
- 密钥文件管理
- 字典字段加密
- 密码生成
- 敏感值遮罩

**使用示例:**

```python
from shared.utils.crypto import CredentialEncryptor, mask_sensitive_value

# 创建加密器
encryptor = CredentialEncryptor()

# 加密 API 密钥
api_key = "sk-1234567890abcdef"
encrypted = encryptor.encrypt(api_key)
print(f"加密后: {encrypted}")

# 解密
decrypted = encryptor.decrypt(encrypted)
print(f"解密后: {decrypted}")

# 加密配置中的敏感字段
config = {
    "app_id": "cli_xxxxx",
    "app_secret": "my-secret"
}
encrypted_config = encryptor.encrypt_dict(config, ["app_secret"])

# 遮罩显示
masked = mask_sensitive_value("sk-1234567890abcdef", show_chars=4)
print(f"遮罩后: {masked}")  # 输出: sk-1...cdef
```

## 工具依赖

所有工具的依赖已在项目根目录的 `requirements.txt` 中定义：

```txt
pyyaml>=6.0.1          # YAML 解析
python-dotenv>=1.0.0   # 环境变量
cryptography>=41.0.7   # 加密功能
colorlog>=6.8.0        # 彩色日志
```

## 导入方式

### 方式一：相对导入（推荐用于技能包脚本）

```python
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from shared.utils.common import OpenClawUtils
from shared.utils.logger import setup_logger
from shared.utils.crypto import CredentialEncryptor
```

### 方式二：绝对导入（如果安装为包）

```python
from shared.utils.common import OpenClawUtils
from shared.utils.logger import setup_logger
from shared.utils.crypto import CredentialEncryptor
```

## 测试工具

每个工具文件都包含测试代码，可以直接运行：

```bash
# 测试通用工具
python shared/utils/common.py

# 测试日志工具
python shared/utils/logger.py

# 测试加密工具
python shared/utils/crypto.py
```

## 添加新工具

如果需要添加新的共享工具：

1. 在本目录创建新的 `.py` 文件
2. 编写工具函数，添加文档注释
3. 包含测试代码（`if __name__ == "__main__"`）
4. 更新本 README.md
5. 如有新的依赖，更新 `requirements.txt`

## 工具设计原则

1. **无状态优先**: 工具函数应尽量无状态
2. **错误处理**: 明确的错误提示和异常处理
3. **类型提示**: 使用 Python 类型注解
4. **文档注释**: 每个函数都有 docstring
5. **可测试**: 包含独立的测试代码

---

**注意**: 这些工具函数会被所有技能包的脚本使用，修改时请注意向后兼容性。
