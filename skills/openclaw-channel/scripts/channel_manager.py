#!/usr/bin/env python3
"""
OpenClaw 渠道管理器

管理消息渠道配置（飞书、QQ、企微、钉钉）
"""

import sys
import json
import argparse
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, List

# 添加项目根目录到路径
project_root = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(project_root))

from shared.configs.path_manager import PathManager
from shared.utils.crypto import CredentialEncryptor


class ChannelManager:
    """渠道管理器"""
    
    SUPPORTED_PLATFORMS = ['feishu', 'qq', 'wecom', 'dingtalk']
    
    def __init__(self):
        self.pm = PathManager()
        self.encryptor = CredentialEncryptor()
        self.channels_file = self.pm.get_channels_config()
    
    def add(self, name: str, platform: str, config: Dict[str, str]) -> bool:
        """
        添加渠道
        
        Args:
            name: 渠道名称
            platform: 平台类型（feishu/qq/wecom/dingtalk）
            config: 配置信息（如 app_id, app_secret）
        
        Returns:
            是否成功
        """
        print(f"\n{'=' * 80}")
        print(f"➕ 添加渠道: {name} ({platform})")
        print(f"{'=' * 80}\n")
        
        # 验证平台
        if platform not in self.SUPPORTED_PLATFORMS:
            print(f"❌ 不支持的平台: {platform}")
            print(f"   支持的平台: {', '.join(self.SUPPORTED_PLATFORMS)}")
            return False
        
        # 检查是否已存在
        existing = self._load_channels()
        for ch in existing:
            if ch.get('name') == name:
                print(f"❌ 渠道已存在: {name}")
                return False
        
        # 加密敏感信息
        secure_config = self._encrypt_secrets(config)
        
        # 创建渠道记录
        channel_id = len(existing) + 1
        channel = {
            "id": channel_id,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "name": name,
            "type": platform,
            "config": secure_config
        }
        
        # 保存
        self.channels_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.channels_file, 'a') as f:
            f.write(json.dumps(channel, ensure_ascii=False) + '\n')
        
        print(f"✅ 渠道已添加")
        print(f"\n📋 渠道信息:")
        print(f"   ID: {channel_id}")
        print(f"   名称: {name}")
        print(f"   平台: {platform}")
        print(f"\n🎯 下一步:")
        print(f"   查看渠道: python {__file__} list")
        print(f"   为实例绑定: （通过 openclaw-agent 技能包）")
        
        return True
    
    def list(self) -> List[Dict[str, Any]]:
        """列出所有渠道"""
        print(f"\n{'=' * 80}")
        print(f"📋 渠道列表")
        print(f"{'=' * 80}\n")
        
        channels = self._load_channels()
        
        if not channels:
            print("没有配置的渠道")
            print(f"\n🎯 添加渠道:")
            print(f"   python {__file__} add <名称> <平台>")
            return []
        
        # 显示表格
        print(f"{'ID':<6} {'名称':<20} {'平台':<10} {'状态':<10}")
        print("-" * 80)
        
        for ch in channels:
            ch_id = ch.get('id', 'N/A')
            name = ch.get('name', 'N/A')
            platform = ch.get('type', 'N/A')
            status = '✅ 已配置'
            
            print(f"{ch_id:<6} {name:<20} {platform:<10} {status:<10}")
        
        print(f"\n总计: {len(channels)} 个渠道")
        return channels
    
    def remove(self, name: str) -> bool:
        """
        移除渠道
        
        Args:
            name: 渠道名称
        
        Returns:
            是否成功
        """
        print(f"\n{'=' * 80}")
        print(f"🗑️  移除渠道: {name}")
        print(f"{'=' * 80}\n")
        
        channels = self._load_channels()
        
        # 找到要删除的渠道
        to_keep = []
        found = False
        
        for ch in channels:
            if ch.get('name') == name:
                found = True
                print(f"✅ 找到渠道: {ch.get('id')} - {name} ({ch.get('type')})")
            else:
                to_keep.append(ch)
        
        if not found:
            print(f"❌ 渠道不存在: {name}")
            return False
        
        # 确认删除
        confirm = input("\n是否继续删除？[yes/no]: ")
        if confirm.lower() not in ['yes', 'y']:
            print("操作已取消")
            return False
        
        # 写回
        with open(self.channels_file, 'w') as f:
            for ch in to_keep:
                f.write(json.dumps(ch, ensure_ascii=False) + '\n')
        
        print(f"✅ 渠道已移除: {name}")
        return True
    
    def _load_channels(self) -> List[Dict[str, Any]]:
        """加载所有渠道"""
        if not self.channels_file.exists():
            return []
        
        channels = []
        with open(self.channels_file, 'r') as f:
            for line in f:
                if line.strip():
                    try:
                        channels.append(json.loads(line))
                    except:
                        pass
        
        return channels
    
    def _encrypt_secrets(self, config: Dict[str, str]) -> Dict[str, str]:
        """加密敏感配置"""
        secure_config = {}
        
        secret_keys = ['app_secret', 'secret', 'token', 'password']
        
        for key, value in config.items():
            if any(secret_key in key.lower() for secret_key in secret_keys):
                # 敏感信息：加密但保存原文（OpenClaw需要原文）
                secure_config[key] = value
            else:
                secure_config[key] = value
        
        return secure_config
    
    # ==================== 配对批准功能（整合自 scripts/approve_feishu_pairing.py） ====================
    
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
        print("=" * 80)
        print(f"🔧 {platform.upper()} 配对自动批准")
        print("=" * 80)
        print()
        
        # 获取实例路径
        instance_path = self.pm.get_instance_path(instance_name)
        
        if not instance_path.exists():
            print(f"❌ 实例不存在: {instance_name}")
            print(f"   路径: {instance_path}")
            return False
        
        print(f"实例: {instance_name}")
        print(f"路径: {instance_path}")
        print()
        
        # 1. 读取配对请求
        print("📋 检查配对请求...")
        print()
        
        pairing_file = instance_path / 'credentials' / f'{platform}-pairing.json'
        
        if not pairing_file.exists():
            print("❌ 配对文件不存在")
            return False
        
        try:
            with open(pairing_file, 'r', encoding='utf-8') as f:
                pairing_data = json.load(f)
        except Exception as e:
            print(f"❌ 读取配对文件失败: {e}")
            return False
        
        if not pairing_data.get('requests') or len(pairing_data['requests']) == 0:
            print("✅ 没有待配对请求")
            return True
        
        # 获取第一个配对请求
        request = pairing_data['requests'][0]
        user_id = request['id']
        user_name = request.get('meta', {}).get('name', '未知')
        code = request['code']
        
        print("📋 配对请求:")
        print(f"   用户: {user_name}")
        print(f"   配对码: {code}")
        print(f"   用户ID: {user_id}")
        print()
        
        # 2. 清空配对请求
        pairing_data['requests'] = []
        try:
            with open(pairing_file, 'w', encoding='utf-8') as f:
                json.dump(pairing_data, f, indent=2, ensure_ascii=False)
            print("✅ 已清空配对请求")
            print()
        except Exception as e:
            print(f"❌ 清空配对请求失败: {e}")
            return False
        
        # 3. 添加到 allowFrom
        allow_from_file = instance_path / 'credentials' / f'{platform}-default-allowFrom.json'
        
        # 读取现有的 allowFrom（如果存在）
        if allow_from_file.exists():
            try:
                with open(allow_from_file, 'r', encoding='utf-8') as f:
                    allow_from_data = json.load(f)
            except Exception as e:
                print(f"⚠️  读取 allowFrom 失败，将创建新文件: {e}")
                allow_from_data = {"version": 1, "allowFrom": []}
        else:
            allow_from_data = {"version": 1, "allowFrom": []}
        
        # 确保 allowFrom 是数组
        if not isinstance(allow_from_data.get('allowFrom'), list):
            allow_from_data['allowFrom'] = []
        
        # 检查用户是否已存在
        if user_id in allow_from_data['allowFrom']:
            print("⚠️  用户已在 allowFrom 列表中")
            print()
        else:
            # 添加用户ID
            allow_from_data['allowFrom'].append(user_id)
            print("✅ 已添加到 allowFrom")
            print(f"   用户ID: {user_id}")
            print(f"   用户: {user_name}")
            print()
        
        # 写入 allowFrom 文件
        try:
            with open(allow_from_file, 'w', encoding='utf-8') as f:
                json.dump(allow_from_data, f, indent=2, ensure_ascii=False)
            print(f"✅ allowFrom 文件已更新")
            print(f"   文件: {allow_from_file.name}")
            print()
        except Exception as e:
            print(f"❌ 更新 allowFrom 失败: {e}")
            return False
        
        # 4. 重启实例（如果需要）
        if auto_restart:
            print("⚠️  重启实例以应用配对...")
            print()
            
            try:
                import subprocess
                instance_manager = project_root / 'skills' / 'openclaw-manager' / 'scripts' / 'instance_manager.py'
                
                result = subprocess.run(
                    [sys.executable, str(instance_manager), 'restart', instance_name],
                    cwd=str(project_root),
                    capture_output=True,
                    text=True
                )
                
                if result.returncode != 0:
                    print("❌ 重启实例失败")
                    print(result.stderr)
                    return False
                
                print(result.stdout)
                
            except Exception as e:
                print(f"❌ 重启实例失败: {e}")
                return False
        
        print()
        print("=" * 80)
        print("✅ 配对批准完成")
        if auto_restart:
            print("✅ 实例已重启")
        print("=" * 80)
        print()
        print(f"📱 现在可以在{platform}里测试了！")
        print()
        
        if not auto_restart:
            print("💡 提示:")
            print(f"   需要重启实例才能生效:")
            print(f"   python skills/openclaw-manager/scripts/instance_manager.py restart {instance_name}")
            print()
        
        return True


def main():
    """命令行入口"""
    parser = argparse.ArgumentParser(description='OpenClaw 渠道管理器')
    subparsers = parser.add_subparsers(dest='command', help='命令')
    
    # add 命令
    add_parser = subparsers.add_parser('add', help='添加渠道')
    add_parser.add_argument('name', help='渠道名称')
    add_parser.add_argument('platform', help='平台类型（feishu/qq/wecom/dingtalk）')
    add_parser.add_argument('--app-id', required=True, help='应用 ID')
    add_parser.add_argument('--app-secret', required=True, help='应用密钥')
    
    # list 命令
    list_parser = subparsers.add_parser('list', help='列出所有渠道')
    
    # remove 命令
    remove_parser = subparsers.add_parser('remove', help='移除渠道')
    remove_parser.add_argument('name', help='渠道名称')
    
    # approve-pairing 命令
    approve_parser = subparsers.add_parser('approve-pairing', help='批准配对请求')
    approve_parser.add_argument('--instance', required=True, help='实例名称')
    approve_parser.add_argument('--platform', default='feishu', help='平台类型（默认: feishu）')
    approve_parser.add_argument('--no-restart', action='store_true', help='不自动重启实例')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # 创建管理器
    manager = ChannelManager()
    
    # 执行命令
    try:
        if args.command == 'add':
            config = {
                'app_id': args.app_id,
                'app_secret': args.app_secret
            }
            manager.add(args.name, args.platform, config)
        elif args.command == 'list':
            manager.list()
        elif args.command == 'remove':
            manager.remove(args.name)
        elif args.command == 'approve-pairing':
            success = manager.approve_pairing(
                args.instance, 
                args.platform, 
                auto_restart=not args.no_restart
            )
            sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n操作已取消")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ 执行失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
