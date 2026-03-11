"""
共享工具函数
提供跨技能包使用的通用功能
"""

import os
import yaml
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional, List


class OpenClawUtils:
    """OpenClaw 通用工具类"""
    
    def __init__(self, workspace_root: str = "./workspace"):
        self.workspace_root = Path(workspace_root)
        self.project_root = Path(__file__).parent.parent.parent
    
    def get_instance_path(self, instance_id: str) -> Path:
        """获取实例工作空间路径"""
        return self.workspace_root / instance_id
    
    def get_instance_config_path(self, instance_id: str, config_name: str = "openclaw.yaml") -> Path:
        """获取实例配置文件路径"""
        return self.get_instance_path(instance_id) / "config" / config_name
    
    def list_instances(self) -> List[str]:
        """列出所有实例"""
        if not self.workspace_root.exists():
            return []
        
        instances = []
        for item in self.workspace_root.iterdir():
            if item.is_dir() and item.name.startswith("openclaw-"):
                instances.append(item.name)
        return sorted(instances)
    
    def instance_exists(self, instance_id: str) -> bool:
        """检查实例是否存在"""
        return self.get_instance_path(instance_id).exists()
    
    def load_config(self, config_path: Path) -> Dict[str, Any]:
        """加载 YAML 配置文件"""
        if not config_path.exists():
            raise FileNotFoundError(f"配置文件不存在: {config_path}")
        
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def save_config(self, config_path: Path, data: Dict[str, Any]) -> None:
        """保存配置到 YAML 文件"""
        config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(config_path, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, allow_unicode=True, default_flow_style=False)
    
    def run_command(self, command: List[str], cwd: Optional[Path] = None) -> tuple[int, str, str]:
        """
        执行命令并返回结果
        
        Returns:
            (exit_code, stdout, stderr)
        """
        result = subprocess.run(
            command,
            cwd=cwd,
            capture_output=True,
            text=True
        )
        return result.returncode, result.stdout, result.stderr
    
    def validate_instance_id(self, instance_id: str) -> bool:
        """
        验证实例 ID 格式
        格式: openclaw-{env}-{num} 或 openclaw-{name}
        """
        if not instance_id.startswith("openclaw-"):
            return False
        
        # 检查是否只包含字母、数字和连字符
        rest = instance_id[9:]  # 去掉 "openclaw-" 前缀
        return all(c.isalnum() or c == '-' for c in rest)
    
    def get_global_config(self) -> Dict[str, Any]:
        """获取全局配置"""
        global_config_path = self.project_root / "shared" / "configs" / "global.yaml"
        
        if not global_config_path.exists():
            # 如果不存在，返回默认配置
            return self._get_default_config()
        
        return self.load_config(global_config_path)
    
    def _get_default_config(self) -> Dict[str, Any]:
        """返回默认配置"""
        return {
            "global": {
                "workspace_root": "./workspace",
                "log_level": "info"
            },
            "openclaw": {
                "version": "latest",
                "install_method": "npm"
            },
            "instance": {
                "name_prefix": "openclaw",
                "auto_start": True,
                "auto_restart": True
            }
        }
    
    def ensure_workspace_exists(self, instance_id: str) -> Path:
        """
        确保实例工作空间目录存在
        
        注意：我们只创建实例的顶层目录，不预定义内部结构。
        实例内部的目录结构由 OpenClaw 自己创建和管理。
        
        Args:
            instance_id: 实例 ID
        
        Returns:
            实例工作空间路径
        """
        instance_path = self.get_instance_path(instance_id)
        instance_path.mkdir(parents=True, exist_ok=True)
        return instance_path


def get_project_root() -> Path:
    """获取项目根目录"""
    return Path(__file__).parent.parent.parent


def load_global_config() -> Dict[str, Any]:
    """加载全局配置（快捷函数）"""
    utils = OpenClawUtils()
    return utils.get_global_config()


def validate_instance_id(instance_id: str) -> bool:
    """验证实例 ID 格式（快捷函数）"""
    utils = OpenClawUtils()
    return utils.validate_instance_id(instance_id)


if __name__ == "__main__":
    # 测试代码
    utils = OpenClawUtils()
    
    print("项目根目录:", utils.project_root)
    print("工作空间根目录:", utils.workspace_root)
    
    # 测试实例 ID 验证
    test_ids = [
        "openclaw-prod-01",
        "openclaw-dev-01",
        "openclaw-test",
        "invalid-name",
        "openclaw-"
    ]
    
    for test_id in test_ids:
        is_valid = utils.validate_instance_id(test_id)
        print(f"{test_id}: {'✅' if is_valid else '❌'}")
