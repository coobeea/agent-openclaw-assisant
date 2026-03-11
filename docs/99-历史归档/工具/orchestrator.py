#!/usr/bin/env python3
"""
OpenClaw 自动化编排层

核心职责:
1. 意图识别 - 理解用户的自然语言输入
2. 智能决策 - 自动选择参数（模型、端口、部署方式等）
3. 流程编排 - 自动串联多个技能包完成完整流程
4. 一步到位 - 用户说"创建龙虾"就自动完成所有步骤

使用示例:
    from scripts.orchestrator import Orchestrator
    
    orch = Orchestrator()
    result = orch.execute("创建一个飞书客服机器人，名字叫客服001")
"""

import sys
import re
import json
import random
import argparse
from pathlib import Path
from typing import Dict, Any, List, Optional

# 添加项目根目录到路径
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from shared.configs.path_manager import PathManager

# 导入各个管理器
sys.path.insert(0, str(project_root / 'skills' / 'openclaw-manager' / 'scripts'))
from instance_manager import InstanceManager

sys.path.insert(0, str(project_root / 'skills' / 'openclaw-channel' / 'scripts'))
from channel_manager import ChannelManager

sys.path.insert(0, str(project_root / 'skills' / 'openclaw-model' / 'scripts'))
from model_manager import ModelManager

sys.path.insert(0, str(project_root / 'skills' / 'openclaw-agent' / 'scripts'))
from agent_manager import AgentManager


class Orchestrator:
    """自动化编排器"""
    
    def __init__(self):
        self.pm = PathManager()
        self.instance_mgr = InstanceManager()
        self.channel_mgr = ChannelManager()
        self.model_mgr = ModelManager()
        self.agent_mgr = AgentManager()
    
    def execute(self, user_input: str, **kwargs) -> Dict[str, Any]:
        """
        执行用户请求（核心入口）
        
        Args:
            user_input: 用户的自然语言输入
            **kwargs: 额外参数（可覆盖自动决策）
        
        Returns:
            执行结果字典
        """
        print(f"\n{'=' * 80}")
        print(f"🎯 用户请求: {user_input}")
        print(f"{'=' * 80}\n")
        
        # 1. 意图识别
        intent = self._recognize_intent(user_input)
        print(f"✅ 识别意图: {intent['intent']}")
        if intent['keywords']:
            print(f"   关键词: {', '.join(intent['keywords'])}")
        
        # 2. 提取参数
        params = self._extract_params(user_input, intent)
        print(f"\n✅ 提取参数:")
        for key, value in params.items():
            print(f"   {key}: {value}")
        
        # 3. 智能决策（填充缺失参数）
        config = self._auto_decide_config(intent, params, **kwargs)
        print(f"\n✅ 智能决策:")
        for key, value in config.items():
            if key not in params or params[key] != value:
                print(f"   {key}: {value} (自动)")
        
        # 4. 执行流程
        print(f"\n{'=' * 80}")
        print(f"🚀 开始执行...")
        print(f"{'=' * 80}\n")
        
        try:
            result = self._execute_workflow(intent['intent'], config)
            
            print(f"\n{'=' * 80}")
            print(f"🎉 执行完成！")
            print(f"{'=' * 80}\n")
            
            return {
                'success': True,
                'intent': intent,
                'config': config,
                'result': result
            }
        except Exception as e:
            print(f"\n❌ 执行失败: {e}")
            import traceback
            traceback.print_exc()
            
            return {
                'success': False,
                'intent': intent,
                'config': config,
                'error': str(e)
            }
    
    def _recognize_intent(self, text: str) -> Dict[str, Any]:
        """
        意图识别
        
        支持的意图:
        - CREATE_INSTANCE: 创建实例
        - CREATE_AGENT: 创建智能体
        - LIST_INSTANCES: 查看实例
        - INSTANCE_STATUS: 查看状态
        - START: 启动
        - STOP: 停止
        - DELETE: 删除
        - CONFIG: 配置
        - HELP: 帮助
        """
        text = text.lower()
        
        # 提取关键词
        keywords = []
        
        # 创建类
        if re.search(r'创建|新建|建立|搭建|想要|需要|搞|弄', text):
            keywords.append('CREATE')
        
        # 查看类
        if re.search(r'查看|看|显示|列出|有哪些|有啥|列表', text):
            keywords.append('LIST')
        
        # 配置类
        if re.search(r'配置|设置|修改', text):
            keywords.append('CONFIG')
        
        # 启停类
        if re.search(r'启动|开始|运行|跑', text):
            keywords.append('START')
        if re.search(r'停止|关闭|关掉|停掉', text):
            keywords.append('STOP')
        
        # 删除类
        if re.search(r'删除|移除|清理', text):
            keywords.append('DELETE')
        
        # 对象类
        if re.search(r'龙虾|实例|instance', text):
            keywords.append('INSTANCE')
        
        # 机器人关键词（更细致的判断）
        if '智能体' in text or 'agent' in text:
            keywords.append('AGENT')
        elif '机器人' in text:
            # 如果有平台关键词，机器人指的是完整实例，否则是智能体
            has_platform = any(p in text for p in ['飞书', 'qq', '企微', '钉钉', 'feishu', 'wecom', 'dingtalk'])
            if has_platform:
                keywords.append('INSTANCE')  # 飞书机器人 = 实例
            else:
                keywords.append('AGENT')  # 客服机器人 = 智能体
        
        # 平台类
        if re.search(r'飞书|feishu|lark', text):
            keywords.append('FEISHU')
        if re.search(r'qq|QQ', text):
            keywords.append('QQ')
        if re.search(r'企微|企业微信|wecom', text):
            keywords.append('WECOM')
        if re.search(r'钉钉|dingtalk', text):
            keywords.append('DINGTALK')
        if re.search(r'模型|model', text):
            keywords.append('MODEL')
        if re.search(r'渠道|channel', text):
            keywords.append('CHANNEL')
        
        # 帮助类
        if re.search(r'帮助|help|怎么|如何|不会', text):
            keywords.append('HELP')
        
        # 决定意图
        intent = 'UNKNOWN'
        
        # 优先处理帮助
        if 'HELP' in keywords:
            intent = 'HELP'
        
        # 创建类意图
        elif 'CREATE' in keywords:
            # 判断创建什么
            # 优先检查平台关键词（创建XX平台机器人 = 创建实例+平台）
            if any(platform in keywords for platform in ['FEISHU', 'QQ', 'WECOM', 'DINGTALK']):
                # 创建飞书机器人 = 创建实例 + 配置飞书渠道
                intent = 'CREATE_WITH_PLATFORM'
            # 然后检查是否明确说"智能体"（在实例中创建agent）
            elif '智能体' in text and ('INSTANCE' in keywords or '实例' in text):
                intent = 'CREATE_AGENT'
            # 否则都是创建实例
            else:
                intent = 'CREATE_INSTANCE'
        
        # 查看类意图
        elif 'LIST' in keywords:
            if 'AGENT' in keywords:
                intent = 'LIST_AGENTS'
            elif 'MODEL' in keywords:
                intent = 'LIST_MODELS'
            elif 'CHANNEL' in keywords:
                intent = 'LIST_CHANNELS'
            else:
                intent = 'LIST_INSTANCES'
        
        # 配置类意图
        elif 'CONFIG' in keywords:
            intent = 'CONFIG'
        
        # 启停类意图
        elif 'START' in keywords:
            intent = 'START'
        elif 'STOP' in keywords:
            intent = 'STOP'
        
        # 删除类意图
        elif 'DELETE' in keywords:
            intent = 'DELETE'
        
        return {
            'intent': intent,
            'keywords': keywords,
            'raw_text': text
        }
    
    def _extract_params(self, text: str, intent: Dict[str, Any]) -> Dict[str, Any]:
        """
        从用户输入提取参数
        
        Returns:
            参数字典
        """
        params = {}
        
        # 提取名称（引号内或"叫"、"名字"后面的内容）
        name_match = re.search(r'[叫名字是为](["\'])([^"\']+)\1', text)
        if not name_match:
            name_match = re.search(r'[叫名字是为]([^\s，。！？]+)', text)
        if name_match:
            if isinstance(name_match.group(1), str) and name_match.group(1) in ['"', "'"]:
                params['name'] = name_match.group(2)
            else:
                params['name'] = name_match.group(1)
        
        # 提取平台
        if 'FEISHU' in intent['keywords']:
            params['platform'] = 'feishu'
        elif 'QQ' in intent['keywords']:
            params['platform'] = 'qq'
        elif 'WECOM' in intent['keywords']:
            params['platform'] = 'wecom'
        elif 'DINGTALK' in intent['keywords']:
            params['platform'] = 'dingtalk'
        
        # 提取模型
        model_match = re.search(r'(bailian|openai|anthropic|silicon|ollama)/([a-zA-Z0-9\.\-]+)', text)
        if model_match:
            params['model'] = f"{model_match.group(1)}/{model_match.group(2)}"
        
        # 提取端口
        port_match = re.search(r'端口[:：\s]*(\d+)', text)
        if port_match:
            params['port'] = int(port_match.group(1))
        
        # 提取实例名（如果是操作现有实例）
        if intent['intent'] in ['START', 'STOP', 'DELETE', 'INSTANCE_STATUS', 'LIST_AGENTS']:
            instance_match = re.search(r'(openclaw-[a-zA-Z0-9\-]+)', text)
            if instance_match:
                params['instance'] = instance_match.group(1)
        
        return params
    
    def _auto_decide_config(self, intent: Dict[str, Any], params: Dict[str, Any], **overrides) -> Dict[str, Any]:
        """
        智能决策配置
        
        自动填充缺失的参数
        """
        config = params.copy()
        config.update(overrides)
        
        # 1. 实例名称
        if 'name' not in config:
            # 根据意图和平台自动生成
            intent_type = intent['intent']
            platform = config.get('platform', '')
            
            if intent_type in ['CREATE_INSTANCE', 'CREATE_WITH_PLATFORM']:
                if platform:
                    prefix = platform
                elif '开发' in intent['raw_text'] or 'dev' in intent['raw_text']:
                    prefix = 'dev'
                elif '测试' in intent['raw_text'] or 'test' in intent['raw_text']:
                    prefix = 'test'
                elif '生产' in intent['raw_text'] or 'prod' in intent['raw_text']:
                    prefix = 'prod'
                else:
                    prefix = 'test'
                
                # 生成唯一ID
                suffix = random.randint(1000, 9999)
                config['name'] = f"openclaw-{prefix}-{suffix}"
        
        # 2. 模型选择
        if 'model' not in config:
            # 自动选择模型
            config['model'] = 'bailian/qwen3.5-plus'
        
        # 3. 端口分配
        if 'port' not in config:
            config['port'] = None  # None = 自动分配
        
        # 4. 部署模式
        if 'deploy_mode' not in config:
            if 'docker' in intent['raw_text'] or '容器' in intent['raw_text']:
                config['deploy_mode'] = 'docker'
            else:
                config['deploy_mode'] = 'host'
        
        # 5. 环境类型
        if 'env' not in config:
            if '生产' in intent['raw_text'] or 'prod' in intent['raw_text']:
                config['env'] = 'prod'
            elif '开发' in intent['raw_text'] or 'dev' in intent['raw_text']:
                config['env'] = 'test'
            else:
                config['env'] = 'test'
        
        return config
    
    def _execute_workflow(self, intent: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行工作流
        
        根据意图编排执行步骤
        """
        result = {}
        
        if intent == 'CREATE_INSTANCE':
            # 流程: 创建实例
            result = self._workflow_create_instance(config)
        
        elif intent == 'CREATE_WITH_PLATFORM':
            # 流程: 创建实例 + 配置渠道
            result = self._workflow_create_with_platform(config)
        
        elif intent == 'CREATE_AGENT':
            # 流程: 创建智能体
            result = self._workflow_create_agent(config)
        
        elif intent == 'LIST_INSTANCES':
            # 流程: 列出实例
            result['instances'] = self.instance_mgr.list()
        
        elif intent == 'LIST_AGENTS':
            # 流程: 列出智能体
            instance = config.get('instance')
            if not instance:
                print("❌ 请指定实例名称")
                return {}
            result['agents'] = self.agent_mgr.list(instance)
        
        elif intent == 'LIST_MODELS':
            # 流程: 列出模型
            result['models'] = self.model_mgr.list()
        
        elif intent == 'LIST_CHANNELS':
            # 流程: 列出渠道
            result['channels'] = self.channel_mgr.list()
        
        elif intent == 'START':
            # 流程: 启动实例
            instance = config.get('instance') or config.get('name')
            if not instance:
                print("❌ 请指定实例名称")
                return {}
            pid = self.instance_mgr.start(instance)
            result['pid'] = pid
        
        elif intent == 'STOP':
            # 流程: 停止实例
            instance = config.get('instance') or config.get('name')
            if not instance:
                print("❌ 请指定实例名称")
                return {}
            success = self.instance_mgr.stop(instance)
            result['stopped'] = success
        
        elif intent == 'DELETE':
            # 流程: 删除实例
            instance = config.get('instance') or config.get('name')
            if not instance:
                print("❌ 请指定实例名称")
                return {}
            success = self.instance_mgr.delete(instance, force=config.get('force', False))
            result['deleted'] = success
        
        elif intent == 'HELP':
            # 显示帮助
            self._show_help()
            result['help_shown'] = True
        
        else:
            print(f"⚠️  暂不支持的意图: {intent}")
            self._show_help()
            result['help_shown'] = True
        
        return result
    
    def _workflow_create_instance(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        工作流: 创建实例
        
        步骤:
        1. 创建实例
        2. 启动实例
        """
        print(f"📋 执行流程: 创建实例\n")
        
        name = config['name']
        model = config.get('model')
        port = config.get('port')
        
        # 步骤1: 创建
        print("步骤 1/2: 创建实例")
        instance_info = self.instance_mgr.create(name, model, port)
        if not instance_info:
            raise Exception("创建实例失败")
        
        # 步骤2: 启动
        print("\n步骤 2/2: 启动实例")
        pid = self.instance_mgr.start(name)
        if not pid:
            raise Exception("启动实例失败")
        
        return {
            'instance': instance_info,
            'pid': pid
        }
    
    def _workflow_create_with_platform(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        工作流: 创建实例 + 配置平台渠道
        
        步骤:
        1. 创建实例
        2. 添加渠道
        3. 创建智能体（绑定渠道）
        4. 启动实例
        """
        print(f"📋 执行流程: 创建{config.get('platform', '')}机器人\n")
        
        name = config['name']
        platform = config['platform']
        model = config.get('model')
        port = config.get('port')
        
        # 步骤1: 创建实例
        print("步骤 1/4: 创建实例")
        instance_info = self.instance_mgr.create(name, model, port)
        if not instance_info:
            raise Exception("创建实例失败")
        
        # 步骤2: 添加渠道（需要用户提供凭证）
        print("\n步骤 2/4: 配置渠道")
        if 'app_id' in config and 'app_secret' in config:
            channel_name = f"{name}-{platform}"
            channel_config = {
                'app_id': config['app_id'],
                'app_secret': config['app_secret']
            }
            success = self.channel_mgr.add(channel_name, platform, channel_config)
            if not success:
                print("⚠️  渠道配置失败，可稍后手动配置")
        else:
            print("⚠️  缺少渠道凭证（app_id, app_secret），请稍后手动配置")
            print(f"\n🎯 手动配置:")
            print(f"   python skills/openclaw-channel/scripts/channel_manager.py add {name}-{platform} {platform} --app-id <ID> --app-secret <SECRET>")
        
        # 步骤3: 创建智能体（TODO: 需要 OpenClaw 支持）
        print("\n步骤 3/4: 创建智能体")
        print("⚠️  暂时跳过（使用默认 main 智能体）")
        
        # 步骤4: 启动实例
        print("\n步骤 4/4: 启动实例")
        pid = self.instance_mgr.start(name)
        if not pid:
            raise Exception("启动实例失败")
        
        return {
            'instance': instance_info,
            'platform': platform,
            'pid': pid
        }
    
    def _workflow_create_agent(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        工作流: 创建智能体
        
        步骤:
        1. 在指定实例中创建智能体
        2. 提示重启实例
        """
        print(f"📋 执行流程: 创建智能体\n")
        
        instance = config.get('instance')
        agent_id = config.get('agent_id')
        agent_name = config.get('name')
        model = config.get('model')
        
        if not instance or not agent_id or not agent_name:
            print("❌ 缺少必要参数")
            print("   需要: instance, agent_id, name")
            raise Exception("缺少必要参数")
        
        # 创建智能体
        success = self.agent_mgr.create(instance, agent_id, agent_name, model)
        if not success:
            raise Exception("创建智能体失败")
        
        return {
            'instance': instance,
            'agent_id': agent_id,
            'agent_name': agent_name
        }
    
    def _show_help(self):
        """显示帮助信息"""
        print(f"\n{'=' * 80}")
        print(f"📖 OpenClaw 龙虾军团管理助手")
        print(f"{'=' * 80}\n")
        
        print("🎯 您可以这样说:\n")
        
        print("**创建机器人**:")
        print("  • 创建一个龙虾")
        print("  • 搞个机器人")
        print("  • 创建一个飞书客服机器人，名字叫客服001")
        print("  • 新建一个测试实例")
        
        print("\n**查看和管理**:")
        print("  • 有哪些龙虾")
        print("  • 看一下实例列表")
        print("  • 查看 openclaw-test-01 的状态")
        print("  • 停止 openclaw-test-01")
        
        print("\n**配置**:")
        print("  • 配置飞书渠道")
        print("  • 添加 AI 模型")
        print("  • 查看所有模型")
        
        print(f"\n{'=' * 80}")


def main():
    """命令行入口"""
    parser = argparse.ArgumentParser(description='OpenClaw 自动化编排器')
    parser.add_argument('query', nargs='*', help='用户查询（自然语言）')
    parser.add_argument('--name', help='实例名称（覆盖自动生成）')
    parser.add_argument('--model', help='模型（覆盖自动选择）')
    parser.add_argument('--port', type=int, help='端口（覆盖自动分配）')
    parser.add_argument('--platform', help='平台（feishu/qq/wecom/dingtalk）')
    parser.add_argument('--app-id', help='应用ID')
    parser.add_argument('--app-secret', help='应用密钥')
    
    args = parser.parse_args()
    
    if not args.query:
        print("请输入您的需求（自然语言）\n")
        print("示例:")
        print("  python orchestrator.py 创建一个飞书客服机器人")
        print("  python orchestrator.py 有哪些龙虾")
        print("  python orchestrator.py 停止 openclaw-test-01")
        return
    
    # 组合查询文本
    query = ' '.join(args.query)
    
    # 准备覆盖参数
    overrides = {}
    if args.name:
        overrides['name'] = args.name
    if args.model:
        overrides['model'] = args.model
    if args.port:
        overrides['port'] = args.port
    if args.platform:
        overrides['platform'] = args.platform
    if args.app_id:
        overrides['app_id'] = args.app_id
    if args.app_secret:
        overrides['app_secret'] = args.app_secret
    
    # 创建编排器并执行
    orch = Orchestrator()
    result = orch.execute(query, **overrides)
    
    # 输出结果（JSON格式，供其他工具调用）
    if result.get('success'):
        print(f"\n✅ 执行成功")
        sys.exit(0)
    else:
        print(f"\n❌ 执行失败")
        sys.exit(1)


if __name__ == '__main__':
    main()
