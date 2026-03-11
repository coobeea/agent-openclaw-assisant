#!/usr/bin/env python3
"""
OpenClaw 自动化编排层

提供端到端的自动化工作流，串联多个manager完成复杂任务。

工作流示例:
- 快速创建飞书机器人（创建实例 + 配置模型 + 安装插件 + 配置渠道）
- 批量部署多个实例
- 健康检查和自动修复
"""

import sys
import time
from pathlib import Path
from typing import Optional, Dict, Any, List

# 添加项目根目录到路径
project_root = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(project_root))

# 导入各个管理器
scripts_dir = Path(__file__).parent
sys.path.insert(0, str(scripts_dir))

from instance_manager import InstanceManager
from shared.configs.path_manager import PathManager

# 导入其他管理器
sys.path.insert(0, str(project_root / 'skills' / 'openclaw-channel' / 'scripts'))
from channel_manager import ChannelManager

sys.path.insert(0, str(project_root / 'skills' / 'openclaw-model' / 'scripts'))
from model_manager import ModelManager

sys.path.insert(0, str(project_root / 'skills' / 'openclaw-plugin' / 'scripts'))
from plugin_manager import PluginManager

sys.path.insert(0, str(project_root / 'skills' / 'openclaw-agent' / 'scripts'))
from agent_manager import AgentManager


class Orchestrator:
    """编排器 - 协调多个管理器完成复杂工作流"""
    
    def __init__(self):
        self.pm = PathManager()
        self.instance_mgr = InstanceManager()
        self.channel_mgr = ChannelManager()
        self.model_mgr = ModelManager()
        self.plugin_mgr = PluginManager()
        self.agent_mgr = AgentManager()
    
    def create_feishu_bot(
        self,
        instance_name: str,
        app_id: str,
        app_secret: str,
        api_key: str,
        model: str = "bailian/qwen3.5-plus",
        port: Optional[int] = None
    ) -> bool:
        """
        快速创建飞书机器人
        
        一键完成:
        1. 创建实例
        2. 配置百炼模型
        3. 安装飞书插件
        4. 配置飞书渠道
        5. 启动实例
        
        Args:
            instance_name: 实例名称（如 openclaw-feishu-001）
            app_id: 飞书App ID
            app_secret: 飞书App Secret
            api_key: 百炼API Key
            model: 模型名称
            port: 端口（可选）
        
        Returns:
            是否全部成功
        """
        print(f"\n{'=' * 80}")
        print(f"🚀 快速创建飞书机器人: {instance_name}")
        print(f"{'=' * 80}\n")
        
        steps = [
            "1. 创建实例",
            "2. 配置模型",
            "3. 安装插件", 
            "4. 配置渠道",
            "5. 启动实例"
        ]
        
        for step in steps:
            print(f"  {step}")
        print()
        
        try:
            # Step 1: 创建实例
            print(f"\n{'─' * 80}")
            print("Step 1/5: 创建实例")
            print(f"{'─' * 80}\n")
            
            result = self.instance_mgr.create(instance_name, model=model, port=port)
            if not result:
                print("❌ 创建实例失败")
                return False
            
            instance_path = result['workspace_path']
            print(f"✅ 实例已创建: {instance_path}")
            time.sleep(1)
            
            # Step 2: 配置模型（已在创建时完成）
            print(f"\n{'─' * 80}")
            print("Step 2/5: 配置模型")
            print(f"{'─' * 80}\n")
            
            # 初始化百炼模型模板
            provider = model.split('/')[0]  # bailian
            model_id = model.split('/')[1]  # qwen3.5-plus
            
            # 读取配置
            config_file = Path(instance_path) / '.openclaw' / 'openclaw.json'
            if config_file.exists():
                with open(config_file, 'r') as f:
                    config = json.load(f)
                
                # 检查模型是否已配置
                if 'providers' in config and provider in config['providers']:
                    print(f"✅ 模型已配置: {model}")
                else:
                    print(f"⚠️  模型配置可能不完整，请手动检查")
            
            time.sleep(1)
            
            # Step 3: 安装飞书插件
            print(f"\n{'─' * 80}")
            print("Step 3/5: 安装飞书插件")
            print(f"{'─' * 80}\n")
            
            if not self.plugin_mgr.install('feishu', instance_name):
                print("⚠️  插件安装失败（非致命错误，可以手动安装）")
            
            time.sleep(1)
            
            # Step 4: 配置飞书渠道
            print(f"\n{'─' * 80}")
            print("Step 4/5: 配置飞书渠道")
            print(f"{'─' * 80}\n")
            
            channel_config = {
                'app_id': app_id,
                'app_secret': app_secret
            }
            
            if not self.channel_mgr.add(f"{instance_name}-feishu", 'feishu', channel_config):
                print("❌ 渠道配置失败")
                return False
            
            time.sleep(1)
            
            # Step 5: 启动实例
            print(f"\n{'─' * 80}")
            print("Step 5/5: 启动实例")
            print(f"{'─' * 80}\n")
            
            start_result = self.instance_mgr.start(instance_name)
            if not start_result:
                print("❌ 启动实例失败")
                return False
            
            # 成功摘要
            print(f"\n{'=' * 80}")
            print("🎉 飞书机器人创建完成！")
            print(f"{'=' * 80}\n")
            
            print(f"✅ 实例名称: {instance_name}")
            print(f"✅ 运行端口: {start_result.get('port', '未知')}")
            print(f"✅ PID: {start_result.get('pid', '未知')}")
            print(f"✅ 模型: {model}")
            print(f"✅ 渠道: 飞书")
            print()
            print("📝 后续步骤:")
            print("  1. 配置飞书机器人回调地址")
            print("  2. 在飞书群中@机器人测试")
            print()
            
            return True
            
        except Exception as e:
            print(f"\n❌ 创建失败: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def quick_start_demo(self) -> bool:
        """
        快速启动演示实例（用于测试和演示）
        
        创建一个配置了默认设置的演示实例
        """
        print(f"\n{'=' * 80}")
        print(f"🚀 快速启动演示")
        print(f"{'=' * 80}\n")
        
        instance_name = f"openclaw-demo-{int(time.time()) % 10000}"
        
        print(f"📦 将创建演示实例: {instance_name}")
        print("⚠️  注意: 需要手动提供 API Key 和飞书凭证")
        print()
        
        # 交互式获取配置
        try:
            api_key = input("请输入百炼 API Key: ").strip()
            app_id = input("请输入飞书 App ID: ").strip()
            app_secret = input("请输入飞书 App Secret: ").strip()
            
            if not api_key or not app_id or not app_secret:
                print("❌ 配置不完整，取消创建")
                return False
            
            return self.create_feishu_bot(
                instance_name=instance_name,
                app_id=app_id,
                app_secret=app_secret,
                api_key=api_key
            )
            
        except KeyboardInterrupt:
            print("\n\n❌ 用户取消")
            return False
    
    def health_check_all(self) -> Dict[str, Any]:
        """
        检查所有实例的健康状态
        
        Returns:
            健康检查报告
        """
        print(f"\n{'=' * 80}")
        print(f"🏥 健康检查 - 所有实例")
        print(f"{'=' * 80}\n")
        
        instances = self.instance_mgr.list()
        
        report = {
            'total': len(instances),
            'running': 0,
            'stopped': 0,
            'error': 0,
            'details': []
        }
        
        for inst in instances:
            status = self.instance_mgr.status(inst['name'])
            
            if status and status['running']:
                report['running'] += 1
                health = '✅ 健康'
            elif status and not status['running']:
                report['stopped'] += 1
                health = '⏸️  已停止'
            else:
                report['error'] += 1
                health = '❌ 异常'
            
            report['details'].append({
                'name': inst['name'],
                'status': health,
                'port': status.get('port') if status else None,
                'pid': status.get('pid') if status else None
            })
            
            print(f"  {inst['name']:30} {health}")
        
        # 统计
        print(f"\n{'─' * 80}")
        print(f"📊 统计:")
        print(f"  总计: {report['total']} 个实例")
        print(f"  运行: {report['running']} 个")
        print(f"  停止: {report['stopped']} 个")
        print(f"  异常: {report['error']} 个")
        print()
        
        return report


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='OpenClaw 编排器')
    subparsers = parser.add_subparsers(dest='command', help='工作流')
    
    # create-feishu-bot
    parser_feishu = subparsers.add_parser('create-feishu-bot', help='快速创建飞书机器人')
    parser_feishu.add_argument('instance', help='实例名称')
    parser_feishu.add_argument('--app-id', required=True, help='飞书App ID')
    parser_feishu.add_argument('--app-secret', required=True, help='飞书App Secret')
    parser_feishu.add_argument('--api-key', required=True, help='百炼API Key')
    parser_feishu.add_argument('--model', default='bailian/qwen3.5-plus', help='模型')
    parser_feishu.add_argument('--port', type=int, help='端口')
    
    # quick-start-demo
    subparsers.add_parser('quick-start-demo', help='快速启动演示（交互式）')
    
    # health-check-all
    subparsers.add_parser('health-check', help='检查所有实例健康状态')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    orch = Orchestrator()
    
    if args.command == 'create-feishu-bot':
        success = orch.create_feishu_bot(
            instance_name=args.instance,
            app_id=args.app_id,
            app_secret=args.app_secret,
            api_key=args.api_key,
            model=args.model,
            port=args.port
        )
        sys.exit(0 if success else 1)
    
    elif args.command == 'quick-start-demo':
        success = orch.quick_start_demo()
        sys.exit(0 if success else 1)
    
    elif args.command == 'health-check':
        orch.health_check_all()


if __name__ == '__main__':
    main()
