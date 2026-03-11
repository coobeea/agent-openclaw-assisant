#!/usr/bin/env python3
"""
OpenClaw CLI 调用封装

提供便捷的 Python 接口来调用 OpenClaw CLI 命令
"""
import subprocess
import os
import json
import sys
from pathlib import Path
from typing import Dict, List, Optional, Union

# 导入统一路径管理器
project_root = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(project_root))

from shared.configs.path_manager import get_openclaw_cli, should_use_node_prefix

# 兼容旧代码
OPENCLAW_CLI = get_openclaw_cli()
USE_NODE_PREFIX = should_use_node_prefix()


class OpenClawCLI:
    """OpenClaw CLI 封装类"""
    
    def __init__(
        self,
        cli_path: Optional[Path] = None,
        use_node: Optional[bool] = None
    ):
        """
        初始化 OpenClaw CLI
        
        Args:
            cli_path: CLI 路径（默认从 PathManager 获取）
            use_node: 是否使用 node 前缀（默认从 PathManager 获取）
        """
        self.cli_path = cli_path or get_openclaw_cli()
        self.use_node = use_node if use_node is not None else should_use_node_prefix()
    
    def run(
        self,
        args: List[str],
        workspace_dir: Optional[Path] = None,
        config_file: Optional[Path] = None,
        state_dir: Optional[Path] = None,
        env_overrides: Optional[Dict[str, str]] = None,
        capture_output: bool = True,
        timeout: Optional[int] = None,
        check: bool = False
    ) -> subprocess.CompletedProcess:
        """
        运行 OpenClaw CLI 命令
        
        Args:
            args: OpenClaw 命令参数
            workspace_dir: 工作目录
            config_file: 配置文件路径（设置 OPENCLAW_CONFIG_PATH）
            state_dir: 状态目录（设置 OPENCLAW_STATE_DIR）
            env_overrides: 额外的环境变量
            capture_output: 是否捕获输出
            timeout: 超时时间（秒）
            check: 是否检查返回码并抛出异常
        
        Returns:
            subprocess.CompletedProcess 对象
        """
        # 准备环境变量
        env = os.environ.copy()
        
        if config_file:
            env['OPENCLAW_CONFIG_PATH'] = str(config_file)
        
        if state_dir:
            env['OPENCLAW_STATE_DIR'] = str(state_dir)
        
        if env_overrides:
            env.update(env_overrides)
        
        # 准备命令
        if self.use_node:
            cmd = ['node', str(self.cli_path)] + args
        else:
            cmd = [str(self.cli_path)] + args
        
        # 执行命令
        return subprocess.run(
            cmd,
            env=env,
            cwd=str(workspace_dir) if workspace_dir else None,
            capture_output=capture_output,
            text=True,
            timeout=timeout,
            check=check
        )
    
    def setup_workspace(
        self,
        workspace_dir: Path,
        **kwargs
    ) -> subprocess.CompletedProcess:
        """
        初始化 OpenClaw 工作空间
        
        Args:
            workspace_dir: 工作空间目录
            **kwargs: 传递给 run() 的额外参数
        
        Returns:
            subprocess.CompletedProcess 对象
        """
        return self.run(['setup', '--workspace', str(workspace_dir)], **kwargs)
    
    def config_set(
        self,
        key: str,
        value: Union[str, int, bool],
        config_file: Optional[Path] = None,
        state_dir: Optional[Path] = None,
        **kwargs
    ) -> subprocess.CompletedProcess:
        """
        设置配置项
        
        Args:
            key: 配置键（如 'gateway.auth.token'）
            value: 配置值
            config_file: 配置文件路径
            state_dir: 状态目录
            **kwargs: 传递给 run() 的额外参数
        
        Returns:
            subprocess.CompletedProcess 对象
        """
        return self.run(
            ['config', 'set', key, str(value)],
            config_file=config_file,
            state_dir=state_dir,
            **kwargs
        )
    
    def config_get(
        self,
        key: str,
        config_file: Optional[Path] = None,
        state_dir: Optional[Path] = None,
        **kwargs
    ) -> subprocess.CompletedProcess:
        """
        获取配置项
        
        Args:
            key: 配置键
            config_file: 配置文件路径
            state_dir: 状态目录
            **kwargs: 传递给 run() 的额外参数
        
        Returns:
            subprocess.CompletedProcess 对象
        """
        return self.run(
            ['config', 'get', key],
            config_file=config_file,
            state_dir=state_dir,
            **kwargs
        )
    
    def config_validate(
        self,
        config_file: Optional[Path] = None,
        state_dir: Optional[Path] = None,
        **kwargs
    ) -> subprocess.CompletedProcess:
        """
        验证配置
        
        Args:
            config_file: 配置文件路径
            state_dir: 状态目录
            **kwargs: 传递给 run() 的额外参数
        
        Returns:
            subprocess.CompletedProcess 对象
        """
        return self.run(
            ['config', 'validate'],
            config_file=config_file,
            state_dir=state_dir,
            **kwargs
        )
    
    def gateway_start(
        self,
        port: Optional[int] = None,
        config_file: Optional[Path] = None,
        state_dir: Optional[Path] = None,
        workspace_dir: Optional[Path] = None,
        background: bool = True,
        **kwargs
    ) -> subprocess.Popen | subprocess.CompletedProcess:
        """
        启动 Gateway
        
        Args:
            port: 端口号
            config_file: 配置文件路径
            state_dir: 状态目录
            workspace_dir: 工作目录
            background: 是否在后台运行
            **kwargs: 传递给 run() 的额外参数
        
        Returns:
            如果 background=True，返回 Popen 对象；否则返回 CompletedProcess 对象
        """
        args = ['gateway']
        if port:
            args.extend(['--port', str(port)])
        
        # 准备环境变量
        env = os.environ.copy()
        if config_file:
            env['OPENCLAW_CONFIG_PATH'] = str(config_file)
        if state_dir:
            env['OPENCLAW_STATE_DIR'] = str(state_dir)
        if kwargs.get('env_overrides'):
            env.update(kwargs['env_overrides'])
        
        # 准备命令
        if self.use_node:
            cmd = ['node', str(self.cli_path)] + args
        else:
            cmd = [str(self.cli_path)] + args
        
        if background:
            # 后台运行
            return subprocess.Popen(
                cmd,
                env=env,
                cwd=str(workspace_dir) if workspace_dir else None,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                start_new_session=True
            )
        else:
            # 前台运行
            return self.run(
                args,
                config_file=config_file,
                state_dir=state_dir,
                workspace_dir=workspace_dir,
                **kwargs
            )
    
    def agents_list(
        self,
        config_file: Optional[Path] = None,
        state_dir: Optional[Path] = None,
        **kwargs
    ) -> subprocess.CompletedProcess:
        """
        列出智能体
        
        Args:
            config_file: 配置文件路径
            state_dir: 状态目录
            **kwargs: 传递给 run() 的额外参数
        
        Returns:
            subprocess.CompletedProcess 对象
        """
        return self.run(
            ['agents', 'list'],
            config_file=config_file,
            state_dir=state_dir,
            **kwargs
        )
    
    def agents_add(
        self,
        agent_id: str,
        workspace: Optional[Path] = None,
        config_file: Optional[Path] = None,
        state_dir: Optional[Path] = None,
        **kwargs
    ) -> subprocess.CompletedProcess:
        """
        添加智能体
        
        Args:
            agent_id: 智能体 ID
            workspace: 智能体工作空间
            config_file: 配置文件路径
            state_dir: 状态目录
            **kwargs: 传递给 run() 的额外参数
        
        Returns:
            subprocess.CompletedProcess 对象
        """
        args = ['agents', 'add', agent_id]
        if workspace:
            args.extend(['--workspace', str(workspace)])
        
        return self.run(
            args,
            config_file=config_file,
            state_dir=state_dir,
            **kwargs
        )
    
    def get_version(self) -> str:
        """
        获取 OpenClaw 版本
        
        Returns:
            版本字符串
        """
        result = self.run(['--version'], capture_output=True)
        if result.returncode == 0:
            return result.stdout.strip()
        return "Unknown"


# 全局实例（方便直接导入使用）
cli = OpenClawCLI()


# ============================================================================
# 便捷函数
# ============================================================================

def run_openclaw(*args, **kwargs) -> subprocess.CompletedProcess:
    """
    便捷函数：运行 OpenClaw CLI 命令
    
    等价于 cli.run(*args, **kwargs)
    """
    return cli.run(*args, **kwargs)


def check_openclaw_available() -> tuple[bool, str]:
    """
    检查 OpenClaw CLI 是否可用
    
    Returns:
        tuple: (是否可用, 版本信息或错误信息)
    """
    try:
        version = cli.get_version()
        return True, version
    except Exception as e:
        return False, str(e)


if __name__ == "__main__":
    # 测试
    print("测试 OpenClaw CLI...")
    print("=" * 80)
    
    is_available, info = check_openclaw_available()
    
    if is_available:
        print(f"✅ OpenClaw CLI 可用")
        print(f"   版本: {info}")
        print(f"   路径: {cli.cli_path}")
        print(f"   使用 Node 前缀: {cli.use_node}")
    else:
        print(f"❌ OpenClaw CLI 不可用")
        print(f"   错误: {info}")
    
    print("=" * 80)
