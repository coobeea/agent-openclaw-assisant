#!/usr/bin/env python3
"""
统一路径管理器

从 global.yaml 读取配置，支持环境变量覆盖，提供统一的路径获取接口。
所有脚本都应该通过这个模块获取路径，而不是硬编码。

优先级:
1. 环境变量（最高优先级，允许临时覆盖）
2. global.yaml 配置
3. 合理的默认值

使用示例:
    from shared.configs.path_manager import PathManager
    
    pm = PathManager()
    workspace_root = pm.get_workspace_root()
    lobsters_dir = pm.get_lobsters_dir()
    instance_path = pm.get_instance_path("openclaw-test-01")
"""

import os
import yaml
import shutil
from pathlib import Path
from typing import Optional, Dict, Any


class PathManager:
    """统一路径管理器"""
    
    def __init__(self, config_file: Optional[Path] = None):
        """
        初始化路径管理器
        
        Args:
            config_file: global.yaml 路径（可选）
        """
        self.project_root = Path(__file__).resolve().parent.parent.parent
        self.config_file = config_file or (self.project_root / 'shared' / 'configs' / 'global.yaml')
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return yaml.safe_load(f) or {}
            except Exception as e:
                print(f"⚠️  配置文件加载失败: {e}")
                return {}
        else:
            # 尝试加载模板
            template_file = self.config_file.parent / 'global.yaml.template'
            if template_file.exists():
                try:
                    with open(template_file, 'r', encoding='utf-8') as f:
                        return yaml.safe_load(f) or {}
                except Exception:
                    return {}
            return {}
    
    def get_workspace_root(self) -> Path:
        """
        获取工作空间根目录
        
        优先级:
        1. 环境变量 OPENCLAW_ASSISTANT_WORKSPACE
        2. global.yaml 中的 workspace_root
        3. 默认值: {PROJECT_ROOT}/workspace
        
        Returns:
            工作空间根目录的绝对路径
        """
        # 1. 环境变量
        env_value = os.getenv('OPENCLAW_ASSISTANT_WORKSPACE')
        if env_value:
            path = Path(env_value)
            return path if path.is_absolute() else self.project_root / path
        
        # 2. global.yaml
        config_value = self.config.get('global', {}).get('workspace_root')
        if config_value:
            path = Path(config_value)
            return path if path.is_absolute() else self.project_root / path
        
        # 3. 默认值
        return self.project_root / 'workspace'
    
    def get_lobsters_dir(self) -> Path:
        """
        获取实例（龙虾）存储目录
        
        Returns:
            实例目录: {WORKSPACE_ROOT}/lobsters
        """
        return self.get_workspace_root() / 'lobsters'
    
    def get_data_dir(self) -> Path:
        """
        获取数据目录
        
        Returns:
            数据目录: {WORKSPACE_ROOT}/data
        """
        return self.get_workspace_root() / 'data'
    
    def get_logs_dir(self) -> Path:
        """
        获取日志目录
        
        Returns:
            日志目录: {WORKSPACE_ROOT}/logs
        """
        return self.get_workspace_root() / 'logs'
    
    def get_instance_path(self, instance_name: str) -> Path:
        """
        获取特定实例的工作空间路径
        
        Args:
            instance_name: 实例名称
        
        Returns:
            实例工作空间路径: {LOBSTERS_DIR}/{instance_name}
        """
        return self.get_lobsters_dir() / instance_name
    
    def get_instance_config(self, instance_name: str) -> Path:
        """
        获取实例的配置文件路径
        
        Args:
            instance_name: 实例名称
        
        Returns:
            配置文件路径: {instance_path}/.openclaw/openclaw.json
        """
        return self.get_instance_path(instance_name) / '.openclaw' / 'openclaw.json'
    
    def get_agents_db(self) -> Path:
        """
        获取实例记录数据库路径
        
        Returns:
            agents.jsonl 路径: {DATA_DIR}/agents.jsonl
        """
        return self.get_data_dir() / 'agents.jsonl'
    
    def get_models_config(self) -> Path:
        """
        获取模型配置文件路径
        
        Returns:
            models.json 路径: {DATA_DIR}/models.json
        """
        return self.get_data_dir() / 'models.json'
    
    def get_channels_config(self) -> Path:
        """
        获取渠道配置文件路径
        
        Returns:
            channels.jsonl 路径: {DATA_DIR}/channels.jsonl
        """
        return self.get_data_dir() / 'channels.jsonl'
    
    def ensure_directories(self):
        """确保所有必要目录存在"""
        dirs = [
            self.get_workspace_root(),
            self.get_lobsters_dir(),
            self.get_data_dir(),
            self.get_logs_dir()
        ]
        
        for d in dirs:
            d.mkdir(parents=True, exist_ok=True)
    
    def get_openclaw_cli(self) -> Path:
        """
        获取 OpenClaw CLI 路径
        
        优先级:
        1. 环境变量 OPENCLAW_CLI_PATH
        2. 全局命令 openclaw
        3. 项目相邻目录 ../openclaw/dist/index.js
        4. Home 目录常见位置
        5. 默认值 openclaw
        
        Returns:
            OpenClaw CLI 路径（可能是命令名或文件路径）
        """
        # 1. 环境变量
        env_path = os.getenv('OPENCLAW_CLI_PATH')
        if env_path:
            path = Path(env_path)
            if not path.is_absolute():
                path = (self.project_root / path).resolve()
            return path
        
        # 2. 全局命令
        if shutil.which('openclaw'):
            return Path('openclaw')
        
        # 3. 项目相邻目录
        candidate = self.project_root.parent / 'openclaw/dist/index.js'
        if candidate.exists():
            return candidate
        
        # 4. Home 目录（常见位置 1）
        candidate = Path.home() / 'git/git_agents/openclaw/dist/index.js'
        if candidate.exists():
            return candidate
        
        # 5. Home 目录（常见位置 2）
        candidate = Path.home() / 'openclaw/dist/index.js'
        if candidate.exists():
            return candidate
        
        # 6. 默认值
        return Path('openclaw')
    
    def should_use_node_prefix(self) -> bool:
        """
        判断是否需要使用 Node.js 前缀
        
        规则:
        - 如果 CLI 是 .js/.mjs 文件 → 需要 node 前缀
        - 如果 CLI 是命令名 → 不需要 node 前缀
        - 可通过 OPENCLAW_USE_NODE 环境变量覆盖
        
        Returns:
            是否需要 node 前缀
        """
        # 环境变量覆盖
        env_value = os.getenv('OPENCLAW_USE_NODE')
        if env_value:
            return env_value.lower() in ('true', '1', 'yes')
        
        # 自动判断
        cli_str = str(self.get_openclaw_cli())
        return cli_str.endswith('.js') or cli_str.endswith('.mjs')
    
    def get_next_port(self) -> int:
        """
        获取下一个可用端口
        
        Returns:
            可用端口号
        """
        DEFAULT_PORT_START = 18800
        DEFAULT_PORT_STEP = 100
        
        agents_db = self.get_agents_db()
        if not agents_db.exists():
            return DEFAULT_PORT_START
        
        import json
        max_port = DEFAULT_PORT_START - DEFAULT_PORT_STEP
        
        with open(agents_db, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and line != '{}':
                    try:
                        agent = json.loads(line)
                        port = agent.get('gateway_port', 0)
                        if port > max_port:
                            max_port = port
                    except json.JSONDecodeError:
                        continue
        
        return max_port + DEFAULT_PORT_STEP
    
    def print_config_info(self):
        """打印当前配置信息（用于调试）"""
        print("=" * 80)
        print("统一配置信息")
        print("=" * 80)
        
        print(f"项目根目录: {self.project_root}")
        print(f"配置文件: {self.config_file}")
        print(f"  存在: {'✅' if self.config_file.exists() else '❌'}")
        print()
        
        # 工作空间
        print("工作空间根目录:")
        workspace_root = self.get_workspace_root()
        env_value = os.getenv('OPENCLAW_ASSISTANT_WORKSPACE')
        config_value = self.config.get('global', {}).get('workspace_root')
        
        if env_value:
            print(f"  来源: 环境变量 OPENCLAW_ASSISTANT_WORKSPACE")
            print(f"  值: {env_value}")
        elif config_value:
            print(f"  来源: global.yaml")
            print(f"  值: {config_value}")
        else:
            print(f"  来源: 默认值")
            print(f"  值: workspace/")
        print(f"  绝对路径: {workspace_root}")
        print()
        
        print(f"实例目录: {self.get_lobsters_dir()}")
        print(f"数据目录: {self.get_data_dir()}")
        print(f"日志目录: {self.get_logs_dir()}")
        print(f"实例记录: {self.get_agents_db()}")
        print(f"模型配置: {self.get_models_config()}")
        print(f"渠道配置: {self.get_channels_config()}")
        print()
        
        # OpenClaw CLI
        print("OpenClaw CLI:")
        openclaw_cli = self.get_openclaw_cli()
        cli_env = os.getenv('OPENCLAW_CLI_PATH')
        cli_str = str(openclaw_cli)
        
        if cli_env:
            print(f"  来源: 环境变量 OPENCLAW_CLI_PATH")
            print(f"  值: {cli_env}")
        elif cli_str == 'openclaw' and shutil.which('openclaw'):
            print(f"  来源: 全局命令（自动检测）")
        elif cli_str.endswith('.js'):
            print(f"  来源: 自动检测到源码路径")
        else:
            print(f"  来源: 默认值")
        print(f"  路径: {openclaw_cli}")
        print(f"  使用 Node 前缀: {self.should_use_node_prefix()}")
        
        print("=" * 80)


# 全局单例
_path_manager = None


def get_path_manager() -> PathManager:
    """获取全局路径管理器单例"""
    global _path_manager
    if _path_manager is None:
        _path_manager = PathManager()
    return _path_manager


# 便捷函数
def get_workspace_root() -> Path:
    """获取工作空间根目录"""
    return get_path_manager().get_workspace_root()


def get_lobsters_dir() -> Path:
    """获取实例目录"""
    return get_path_manager().get_lobsters_dir()


def get_data_dir() -> Path:
    """获取数据目录"""
    return get_path_manager().get_data_dir()


def get_logs_dir() -> Path:
    """获取日志目录"""
    return get_path_manager().get_logs_dir()


def get_instance_path(instance_name: str) -> Path:
    """获取实例工作空间路径"""
    return get_path_manager().get_instance_path(instance_name)


def get_agents_db() -> Path:
    """获取实例记录数据库路径"""
    return get_path_manager().get_agents_db()


def get_models_config() -> Path:
    """获取模型配置文件路径"""
    return get_path_manager().get_models_config()


def get_channels_config() -> Path:
    """获取渠道配置文件路径"""
    return get_path_manager().get_channels_config()


def ensure_directories():
    """确保所有必要目录存在"""
    get_path_manager().ensure_directories()


def get_openclaw_cli() -> Path:
    """获取 OpenClaw CLI 路径"""
    return get_path_manager().get_openclaw_cli()


def should_use_node_prefix() -> bool:
    """判断是否需要使用 Node.js 前缀"""
    return get_path_manager().should_use_node_prefix()


def get_next_port() -> int:
    """获取下一个可用端口"""
    return get_path_manager().get_next_port()


def print_config_info():
    """打印当前配置信息"""
    get_path_manager().print_config_info()


if __name__ == '__main__':
    # 测试和验证
    print("🧪 测试统一路径管理器\n")
    
    pm = PathManager()
    pm.print_config_info()
    
    print("\n🔧 确保目录存在...")
    ensure_directories()
    
    print("\n✅ 测试完成！")
    print("\n示例实例路径:")
    print(f"  openclaw-test-01: {get_instance_path('openclaw-test-01')}")
    print(f"  openclaw-prod-01: {get_instance_path('openclaw-prod-01')}")
    print(f"\n下一个可用端口: {get_next_port()}")
