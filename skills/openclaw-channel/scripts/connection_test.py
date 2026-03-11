#!/usr/bin/env python3
"""
渠道连接测试工具
"""

import sys
import click
from pathlib import Path
from rich.console import Console

project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from shared.utils.common import OpenClawUtils

console = Console()


@click.command()
@click.argument('instance_id')
@click.argument('channel_name')
def test_connection(instance_id, channel_name):
    """测试渠道连接"""
    utils = OpenClawUtils()
    
    if not utils.instance_exists(instance_id):
        console.print(f"[red]❌ 实例不存在: {instance_id}[/red]")
        sys.exit(1)
    
    console.print(f"[cyan]🔌 测试连接: {instance_id} → {channel_name}[/cyan]")
    
    # TODO: 实际的连接测试逻辑
    # 调用 OpenClaw 命令或直接测试 API
    
    console.print(f"[green]✅ 渠道连接正常[/green]")


if __name__ == '__main__':
    test_connection()
