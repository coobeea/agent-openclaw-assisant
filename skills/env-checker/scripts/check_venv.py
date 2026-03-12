#!/usr/bin/env python3
"""
虚拟环境检查脚本（跨平台）
功能：检查项目根目录下的虚拟环境是否存在
输出：标准化的 JSON 格式，易于解析

使用方法：
    python check_venv.py [--project-root PATH]
    
退出码：
    0 - 虚拟环境存在且可用
    1 - 虚拟环境不存在或不可用
"""

import os
import sys
import json
import argparse
import subprocess
from pathlib import Path


def find_project_root():
    """
    查找项目根目录（向上查找直到找到 skills/env-checker 目录）
    """
    current = Path(__file__).resolve().parent
    
    # 从脚本所在目录向上查找
    while current.parent != current:
        env_checker_path = current / "skills" / "env-checker"
        if env_checker_path.exists():
            return current
        current = current.parent
    
    # 如果找不到，返回当前工作目录
    return Path.cwd()


def check_venv(project_root: Path, venv_name: str = ".venv"):
    """
    检查虚拟环境是否存在
    
    Args:
        project_root: 项目根目录
        venv_name: 虚拟环境目录名（默认 .venv）
        
    Returns:
        dict: 检查结果
    """
    venv_dir = project_root / venv_name
    
    # 根据操作系统确定 Python 可执行文件路径
    if sys.platform == "win32":
        venv_python = venv_dir / "Scripts" / "python.exe"
    else:
        venv_python = venv_dir / "bin" / "python"
    
    result = {
        "exists": False,
        "venv_dir": str(venv_dir),
        "venv_python": str(venv_python),
        "project_root": str(project_root),
        "platform": sys.platform,
    }
    
    # 检查虚拟环境是否存在
    if not venv_dir.exists():
        result["message"] = f"虚拟环境目录不存在: {venv_dir}"
        result["setup_command"] = get_setup_command(project_root)
        return result
    
    # 检查 Python 可执行文件是否存在
    if not venv_python.exists():
        result["message"] = f"Python 可执行文件不存在: {venv_python}"
        result["setup_command"] = get_setup_command(project_root)
        return result
    
    # 检查 Python 是否可用
    try:
        output = subprocess.check_output(
            [str(venv_python), "--version"],
            stderr=subprocess.STDOUT,
            text=True,
            timeout=5
        )
        python_version = output.strip()
        
        result["exists"] = True
        result["python_version"] = python_version
        result["message"] = f"虚拟环境可用: {python_version}"
        return result
        
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError) as e:
        result["message"] = f"Python 不可用: {e}"
        result["setup_command"] = get_setup_command(project_root)
        return result


def get_setup_command(project_root: Path):
    """
    获取创建虚拟环境的命令
    
    Args:
        project_root: 项目根目录
        
    Returns:
        str: 创建命令
    """
    setup_script = project_root / "skills" / "env-checker" / "scripts"
    
    if sys.platform == "win32":
        setup_bat = setup_script / "setup.bat"
        return str(setup_bat)
    else:
        setup_sh = setup_script / "setup.sh"
        return f"bash {setup_sh}"


def main():
    parser = argparse.ArgumentParser(
        description="检查项目虚拟环境是否存在",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 自动检测项目根目录
  python check_venv.py
  
  # 指定项目根目录
  python check_venv.py --project-root /path/to/project
  
  # JSON 格式输出
  python check_venv.py --json
"""
    )
    
    parser.add_argument(
        "--project-root",
        type=Path,
        help="项目根目录路径（默认自动检测）"
    )
    
    parser.add_argument(
        "--venv-name",
        default=".venv",
        help="虚拟环境目录名（默认: .venv）"
    )
    
    parser.add_argument(
        "--json",
        action="store_true",
        help="以 JSON 格式输出"
    )
    
    args = parser.parse_args()
    
    # 确定项目根目录
    if args.project_root:
        project_root = args.project_root.resolve()
    else:
        project_root = find_project_root()
    
    # 检查虚拟环境
    result = check_venv(project_root, args.venv_name)
    
    # 输出结果
    if args.json:
        # JSON 格式
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        # 人类可读格式
        if result["exists"]:
            print(f"✅ 虚拟环境存在")
            print(f"   Python: {result['venv_python']}")
            print(f"   版本: {result['python_version']}")
        else:
            print(f"❌ 虚拟环境不存在")
            print(f"   目录: {result['venv_dir']}")
            print(f"   创建命令: {result['setup_command']}")
    
    # 设置退出码
    sys.exit(0 if result["exists"] else 1)


if __name__ == "__main__":
    main()
