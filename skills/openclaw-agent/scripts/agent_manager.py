#!/usr/bin/env python3
"""
OpenClaw 智能体管理器

管理 OpenClaw 实例中的智能体（Agents）
"""

import sys
import json
import argparse
import subprocess
from pathlib import Path
from typing import Optional, Dict, Any, List

# 添加项目根目录到路径
project_root = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(project_root))

from shared.configs.path_manager import PathManager


class AgentManager:
    """智能体管理器"""
    
    def __init__(self):
        self.pm = PathManager()
    
    def create(self, instance_name: str, agent_id: str, agent_name: str, 
               model: Optional[str] = None) -> bool:
        """
        创建智能体
        
        Args:
            instance_name: 实例名称
            agent_id: 智能体ID（英文）
            agent_name: 智能体名称（中文）
            model: 模型（可选）
        
        Returns:
            是否成功
        """
        print(f"\n{'=' * 80}")
        print(f"🤖 创建智能体: {agent_name} ({agent_id})")
        print(f"{'=' * 80}\n")
        
        # 1. 加载实例配置
        instance_path = self.pm.get_instance_path(instance_name)
        config_file = instance_path / '.openclaw' / 'openclaw.json'
        
        if not config_file.exists():
            print(f"❌ 实例不存在: {instance_name}")
            return False
        
        print(f"✅ 实例: {instance_name}")
        print(f"   配置: {config_file}")
        
        # 2. 读取配置
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
        except Exception as e:
            print(f"❌ 读取配置失败: {e}")
            return False
        
        # 3. 添加智能体
        if 'agents' not in config:
            config['agents'] = {}
        
        # 修正：OpenClaw 的智能体列表字段是 'list' 而不是 'agents'
        if 'list' not in config['agents']:
            config['agents']['list'] = []
        
        # 检查是否已存在
        agents = config['agents'].get('list', [])
        if isinstance(agents, list):
            for agent in agents:
                if agent.get('id') == agent_id:
                    print(f"❌ 智能体已存在: {agent_id}")
                    return False
        
        # 创建新智能体
        new_agent = {
            "id": agent_id,
            "name": agent_name
        }
        
        if model:
            new_agent['model'] = model
        
        if isinstance(agents, list):
            agents.append(new_agent)
        else:
            agents = [new_agent]
        
        config['agents']['list'] = agents
        
        # 4. 在文件系统中创建智能体目录
        agent_dir = instance_path / 'agents' / agent_id
        try:
            agent_dir.mkdir(parents=True, exist_ok=True)
            (agent_dir / 'agent').mkdir(exist_ok=True)
            (agent_dir / 'sessions').mkdir(exist_ok=True)
            print(f"✅ 已创建智能体目录: {agent_dir}")
        except Exception as e:
            print(f"⚠️ 创建智能体目录失败: {e}")
        
        # 4. 保存配置
        try:
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            print(f"✅ 智能体已创建")
            print(f"\n📋 智能体信息:")
            print(f"   ID: {agent_id}")
            print(f"   名称: {agent_name}")
            print(f"   实例: {instance_name}")
            if model:
                print(f"   模型: {model}")
            
            print(f"\n🎯 下一步:")
            print(f"   查看智能体: python {__file__} list {instance_name}")
            print(f"   重启实例: python skills/openclaw-manager/scripts/instance_manager.py restart {instance_name}")
            
            return True
        except Exception as e:
            print(f"❌ 保存配置失败: {e}")
            return False
    
    def list(self, instance_name: str) -> List[Dict[str, Any]]:
        """
        列出实例中的所有智能体
        
        Args:
            instance_name: 实例名称
        
        Returns:
            智能体列表
        """
        print(f"\n{'=' * 80}")
        print(f"📋 智能体列表: {instance_name}")
        print(f"{'=' * 80}\n")
        
        # 1. 加载实例配置
        instance_path = self.pm.get_instance_path(instance_name)
        config_file = instance_path / '.openclaw' / 'openclaw.json'
        
        if not config_file.exists():
            print(f"❌ 实例不存在: {instance_name}")
            return []
        
        # 2. 读取智能体列表
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
            
            # 修正：OpenClaw 的智能体列表字段是 'list'
            agents = config.get('agents', {}).get('list', [])
            
            if not agents:
                print("实例中没有配置智能体")
                print(f"\n🎯 创建智能体:")
                print(f"   python {__file__} create {instance_name} <ID> <名称>")
                return []
            
            # 显示表格
            print(f"{'ID':<20} {'名称':<30} {'模型':<30}")
            print("-" * 80)
            
            for agent in agents:
                agent_id = agent.get('id', 'N/A')
                name = agent.get('name', 'N/A')
                model = agent.get('model', '(默认)')
                
                print(f"{agent_id:<20} {name:<30} {model:<30}")
            
            print(f"\n总计: {len(agents)} 个智能体")
            return agents
            
        except Exception as e:
            print(f"❌ 读取失败: {e}")
            return []
    
    def bind_channel(self, instance_name: str, agent_id: str, channel: str, account_id: Optional[str] = None) -> bool:
        """
        将智能体绑定到渠道
        
        Args:
            instance_name: 实例名称
            agent_id: 智能体ID
            channel: 渠道名称 (如 feishu, qq)
            account_id: 账号ID (可选，用于多账号场景)
        """
        print(f"\n{'=' * 80}")
        print(f"🔗 绑定渠道: {agent_id} -> {channel}" + (f" ({account_id})" if account_id else ""))
        print(f"{'=' * 80}\n")
        
        # 1. 加载实例配置
        instance_path = self.pm.get_instance_path(instance_name)
        config_file = instance_path / '.openclaw' / 'openclaw.json'
        
        if not config_file.exists():
            print(f"❌ 实例不存在: {instance_name}")
            return False
            
        # 2. 读取配置
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
        except Exception as e:
            print(f"❌ 读取配置失败: {e}")
            return False
            
        # 3. 检查智能体是否存在
        agents = config.get('agents', {}).get('list', config.get('agents', {}).get('agents', []))
        agent_exists = False
        for agent in agents:
            if agent.get('id') == agent_id:
                agent_exists = True
                break
                
        if not agent_exists and agent_id != "main":
            print(f"❌ 智能体不存在: {agent_id}")
            return False
            
        # 4. 添加绑定规则
        if 'bindings' not in config:
            config['bindings'] = []
            
        # 检查是否已存在相同的绑定
        for binding in config['bindings']:
            match = binding.get('match', {})
            if match.get('channel') == channel and match.get('accountId') == account_id:
                print(f"⚠️ 渠道 {channel}" + (f"({account_id})" if account_id else "") + f" 已绑定到智能体 {binding.get('agentId')}")
                print(f"🔄 正在更新绑定...")
                binding['agentId'] = agent_id
                break
        else:
            # 添加新绑定
            new_binding = {
                "agentId": agent_id,
                "match": {
                    "channel": channel
                }
            }
            if account_id:
                new_binding["match"]["accountId"] = account_id
                new_binding["comment"] = f"{channel} ({account_id}) -> {agent_id}"
            else:
                new_binding["comment"] = f"{channel} -> {agent_id}"
                
            config['bindings'].append(new_binding)
            
        # 5. 保存配置
        try:
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            print(f"✅ 绑定成功！")
            print(f"   渠道: {channel}")
            if account_id:
                print(f"   账号: {account_id}")
            print(f"   智能体: {agent_id}")
            return True
        except Exception as e:
            print(f"❌ 保存配置失败: {e}")
            return False

    def delete(self, instance_name: str, agent_id: str) -> bool:
        """
        删除智能体
        
        Args:
            instance_name: 实例名称
            agent_id: 智能体ID
        
        Returns:
            是否成功
        """
        print(f"\n{'=' * 80}")
        print(f"🗑️  删除智能体: {agent_id}")
        print(f"{'=' * 80}\n")
        
        # 1. 加载实例配置
        instance_path = self.pm.get_instance_path(instance_name)
        config_file = instance_path / '.openclaw' / 'openclaw.json'
        
        if not config_file.exists():
            print(f"❌ 实例不存在: {instance_name}")
            return False
        
        # 2. 读取配置
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
            
            agents = config.get('agents', {}).get('agents', [])
            
            # 找到并删除
            new_agents = [a for a in agents if a.get('id') != agent_id]
            
            if len(new_agents) == len(agents):
                print(f"❌ 智能体不存在: {agent_id}")
                return False
            
            config['agents']['agents'] = new_agents
            
            # 3. 保存配置
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            print(f"✅ 智能体已删除: {agent_id}")
            print(f"\n⚠️  请重启实例使更改生效:")
            print(f"   python skills/openclaw-manager/scripts/instance_manager.py restart {instance_name}")
            
            return True
            
        except Exception as e:
            print(f"❌ 删除失败: {e}")
            return False
    
    def _load_config(self) -> Dict[str, Any]:
        """加载模型配置（从全局）"""
        if not self.pm.get_models_config().exists():
            return {}
        
        try:
            with open(self.pm.get_models_config(), 'r') as f:
                return json.load(f)
        except:
            return {}


def main():
    """命令行入口"""
    parser = argparse.ArgumentParser(description='OpenClaw 智能体管理器')
    subparsers = parser.add_subparsers(dest='command', help='命令')
    
    # create 命令
    create_parser = subparsers.add_parser('create', help='创建智能体')
    create_parser.add_argument('instance', help='实例名称')
    create_parser.add_argument('agent_id', help='智能体ID（英文）')
    create_parser.add_argument('agent_name', help='智能体名称（中文）')
    create_parser.add_argument('--model', help='模型（如 bailian/qwen3.5-plus）')
    
    # list 命令
    list_parser = subparsers.add_parser('list', help='列出智能体')
    list_parser.add_argument('instance', help='实例名称')
    
    # bind-channel 命令
    bind_parser = subparsers.add_parser('bind-channel', help='绑定渠道')
    bind_parser.add_argument('instance', help='实例名称')
    bind_parser.add_argument('agent_id', help='智能体ID')
    bind_parser.add_argument('channel', help='渠道名称 (如 feishu)')
    bind_parser.add_argument('--account-id', help='账号ID (多账号场景使用)')
    
    # delete 命令
    delete_parser = subparsers.add_parser('delete', help='删除智能体')
    delete_parser.add_argument('instance', help='实例名称')
    delete_parser.add_argument('agent_id', help='智能体ID')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # 创建管理器
    manager = AgentManager()
    
    # 执行命令
    try:
        if args.command == 'create':
            manager.create(args.instance, args.agent_id, args.agent_name, args.model)
        elif args.command == 'list':
            manager.list(args.instance)
        elif args.command == 'bind-channel':
            manager.bind_channel(args.instance, args.agent_id, args.channel, args.account_id)
        elif args.command == 'delete':
            manager.delete(args.instance, args.agent_id)
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
