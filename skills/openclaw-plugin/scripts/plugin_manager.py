#!/usr/bin/env python3
"""
OpenClaw 插件管理工具

管理 OpenClaw 实例的插件（飞书、QQ、企微、钉钉等平台插件）
"""

import sys
import json
import subprocess
import argparse
from pathlib import Path
from typing import Optional, Dict, Any, List

# 添加项目根目录到路径
project_root = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(project_root))

from shared.configs.path_manager import PathManager


class PluginManager:
    """插件管理器"""
    
    # 支持的插件及其npm包名
    AVAILABLE_PLUGINS = {
        'feishu': '@lobehub/chat-plugin-feishu',
        'qq': '@lobehub/chat-plugin-qq',
        'wecom': '@lobehub/chat-plugin-wecom',
        'dingtalk': '@lobehub/chat-plugin-dingtalk'
    }
    
    def __init__(self):
        self.pm = PathManager()
    
    def list_available(self) -> List[str]:
        """列出所有可用插件"""
        print(f"\n{'=' * 80}")
        print(f"📦 可用插件列表")
        print(f"{'=' * 80}\n")
        
        for plugin, package in self.AVAILABLE_PLUGINS.items():
            print(f"  • {plugin:12} ({package})")
        
        print(f"\n总计: {len(self.AVAILABLE_PLUGINS)} 个插件\n")
        return list(self.AVAILABLE_PLUGINS.keys())
    
    def list_installed(self, instance_name: str) -> List[Dict[str, Any]]:
        """列出实例已安装的插件"""
        print(f"\n{'=' * 80}")
        print(f"📋 已安装插件: {instance_name}")
        print(f"{'=' * 80}\n")
        
        # 获取实例路径
        instance_path = self.pm.get_instance_path(instance_name)
        plugins_dir = instance_path / 'plugins'
        
        if not plugins_dir.exists():
            print("  (无已安装插件)\n")
            return []
        
        # 扫描插件目录
        installed = []
        for plugin_dir in plugins_dir.iterdir():
            if plugin_dir.is_dir() and plugin_dir.name in self.AVAILABLE_PLUGINS:
                # 检查package.json
                pkg_file = plugin_dir / 'package.json'
                if pkg_file.exists():
                    try:
                        with open(pkg_file, 'r') as f:
                            pkg_data = json.load(f)
                        version = pkg_data.get('version', 'unknown')
                        installed.append({
                            'name': plugin_dir.name,
                            'version': version,
                            'path': str(plugin_dir)
                        })
                        print(f"  ✅ {plugin_dir.name:12} v{version}")
                    except:
                        print(f"  ⚠️  {plugin_dir.name:12} (配置损坏)")
        
        if not installed:
            print("  (无已安装插件)\n")
        else:
            print(f"\n总计: {len(installed)} 个插件\n")
        
        return installed
    
    def install(self, plugin_name: str, instance_name: str) -> bool:
        """
        安装插件
        
        Args:
            plugin_name: 插件名（feishu/qq/wecom/dingtalk）
            instance_name: 实例名称
        
        Returns:
            是否成功
        """
        print(f"\n{'=' * 80}")
        print(f"📦 安装插件: {plugin_name} → {instance_name}")
        print(f"{'=' * 80}\n")
        
        # 验证插件
        if plugin_name not in self.AVAILABLE_PLUGINS:
            print(f"❌ 未知插件: {plugin_name}")
            print(f"   可用插件: {', '.join(self.AVAILABLE_PLUGINS.keys())}")
            return False
        
        # 获取实例路径
        instance_path = self.pm.get_instance_path(instance_name)
        if not instance_path.exists():
            print(f"❌ 实例不存在: {instance_name}")
            return False
        
        print(f"✅ 实例路径: {instance_path}")
        
        # 创建plugins目录
        plugins_dir = instance_path / 'plugins'
        plugins_dir.mkdir(exist_ok=True)
        plugin_dir = plugins_dir / plugin_name
        
        # 检查是否已安装
        if plugin_dir.exists():
            print(f"⚠️  插件已安装: {plugin_name}")
            return True
        
        # 使用npm安装
        package_name = self.AVAILABLE_PLUGINS[plugin_name]
        print(f"📦 安装包: {package_name}")
        
        try:
            result = subprocess.run(
                ['npm', 'install', '--prefix', str(plugin_dir), package_name],
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if result.returncode == 0:
                print(f"✅ 插件安装成功: {plugin_name}\n")
                return True
            else:
                print(f"❌ 安装失败:")
                print(result.stderr)
                return False
                
        except subprocess.TimeoutExpired:
            print(f"❌ 安装超时（超过120秒）")
            return False
        except Exception as e:
            print(f"❌ 安装失败: {e}")
            return False
    
    def uninstall(self, plugin_name: str, instance_name: str) -> bool:
        """卸载插件"""
        print(f"\n{'=' * 80}")
        print(f"🗑️  卸载插件: {plugin_name} ← {instance_name}")
        print(f"{'=' * 80}\n")
        
        # 获取插件路径
        instance_path = self.pm.get_instance_path(instance_name)
        plugin_dir = instance_path / 'plugins' / plugin_name
        
        if not plugin_dir.exists():
            print(f"⚠️  插件未安装: {plugin_name}")
            return True
        
        # 删除插件目录
        import shutil
        try:
            shutil.rmtree(plugin_dir)
            print(f"✅ 插件已卸载: {plugin_name}\n")
            return True
        except Exception as e:
            print(f"❌ 卸载失败: {e}")
            return False


def main():
    parser = argparse.ArgumentParser(description='OpenClaw 插件管理器')
    subparsers = parser.add_subparsers(dest='command', help='命令')
    
    # list-available
    subparsers.add_parser('list-available', help='列出可用插件')
    
    # list
    parser_list = subparsers.add_parser('list', help='列出已安装插件')
    parser_list.add_argument('instance', help='实例名称')
    
    # install
    parser_install = subparsers.add_parser('install', help='安装插件')
    parser_install.add_argument('plugin', help='插件名称')
    parser_install.add_argument('instance', help='实例名称')
    
    # uninstall
    parser_uninstall = subparsers.add_parser('uninstall', help='卸载插件')
    parser_uninstall.add_argument('plugin', help='插件名称')
    parser_uninstall.add_argument('instance', help='实例名称')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    manager = PluginManager()
    
    if args.command == 'list-available':
        manager.list_available()
    elif args.command == 'list':
        manager.list_installed(args.instance)
    elif args.command == 'install':
        success = manager.install(args.plugin, args.instance)
        sys.exit(0 if success else 1)
    elif args.command == 'uninstall':
        success = manager.uninstall(args.plugin, args.instance)
        sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
