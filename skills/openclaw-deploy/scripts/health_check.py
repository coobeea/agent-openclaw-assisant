#!/usr/bin/env python3
"""
OpenClaw 健康检查工具
"""

import sys
import click
import requests
import psutil
from pathlib import Path
from rich.console import Console

project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from shared.utils.common import OpenClawUtils

console = Console()


@click.command()
@click.argument('instance_id')
@click.option('--port', default=3000, help='实例端口')
def health_check(instance_id, port):
    """检查实例健康状态"""
    utils = OpenClawUtils()
    
    if not utils.instance_exists(instance_id):
        console.print(f"[red]❌ 实例不存在: {instance_id}[/red]")
        sys.exit(1)
    
    console.print(f"\n[cyan]🏥 健康检查: {instance_id}[/cyan]\n")
    
    checks = []
    
    # 1. 检查工作空间
    instance_path = utils.get_instance_path(instance_id)
    workspace_ok = instance_path.exists()
    checks.append(("工作空间", workspace_ok))
    
    # 2. 检查端口
    port_ok = _check_port(port)
    checks.append((f"端口 {port}", port_ok))
    
    # 3. 检查 HTTP 响应
    http_ok = _check_http(port)
    checks.append(("HTTP 响应", http_ok))
    
    # 4. 检查资源使用（简单示例）
    cpu_percent = psutil.cpu_percent(interval=1)
    mem_percent = psutil.virtual_memory().percent
    checks.append((f"CPU 使用率 {cpu_percent}%", cpu_percent < 80))
    checks.append((f"内存使用率 {mem_percent}%", mem_percent < 80))
    
    # 显示结果
    for check_name, ok in checks:
        status = "[green]✅[/green]" if ok else "[red]❌[/red]"
        console.print(f"{status} {check_name}")
    
    all_ok = all(ok for _, ok in checks)
    
    if all_ok:
        console.print(f"\n[green]✅ 实例健康状态良好[/green]")
    else:
        console.print(f"\n[yellow]⚠️ 实例存在问题，请检查[/yellow]")
        sys.exit(1)


def _check_port(port):
    """检查端口是否监听"""
    for conn in psutil.net_connections():
        if conn.laddr.port == port and conn.status == 'LISTEN':
            return True
    return False


def _check_http(port):
    """检查 HTTP 响应"""
    try:
        response = requests.get(f"http://localhost:{port}/health", timeout=5)
        return response.status_code == 200
    except:
        return False


if __name__ == '__main__':
    health_check()
