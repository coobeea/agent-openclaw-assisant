#!/usr/bin/env python3
"""
OpenClaw 模型管理器

管理 AI 模型配置和 API Keys
"""

import sys
import json
import argparse
from pathlib import Path
from typing import Optional, Dict, Any, List

# 添加项目根目录到路径
project_root = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(project_root))

from shared.configs.path_manager import PathManager


class ModelManager:
    """模型管理器"""
    
    SUPPORTED_PROVIDERS = {
        'bailian': 'https://dashscope.aliyuncs.com/compatible-mode/v1',
        'openai': 'https://api.openai.com/v1',
        'anthropic': 'https://api.anthropic.com/v1',
        'silicon': 'https://api.siliconflow.cn/v1',
        'ollama': 'http://localhost:11434/v1'
    }
    
    def __init__(self):
        self.pm = PathManager()
        self.models_file = self.pm.get_models_config()
    
    def add(self, provider: str, model_id: str, api_key: str, base_url: Optional[str] = None) -> bool:
        """
        添加模型
        
        Args:
            provider: 提供商（bailian/openai/anthropic等）
            model_id: 模型ID（如 qwen3.5-plus）
            api_key: API密钥
            base_url: API地址（可选，使用默认值）
        
        Returns:
            是否成功
        """
        print(f"\n{'=' * 80}")
        print(f"➕ 添加模型: {provider}/{model_id}")
        print(f"{'=' * 80}\n")
        
        # 验证提供商
        if provider not in self.SUPPORTED_PROVIDERS:
            print(f"❌ 不支持的提供商: {provider}")
            print(f"   支持的提供商: {', '.join(self.SUPPORTED_PROVIDERS.keys())}")
            return False
        
        # 加载现有配置
        config = self._load_config()
        
        # 确保 providers 存在
        if 'providers' not in config:
            config['providers'] = {}
        
        # 确保该 provider 存在
        if provider not in config['providers']:
            config['providers'][provider] = {
                "id": provider,
                "name": provider.capitalize(),
                "baseUrl": base_url or self.SUPPORTED_PROVIDERS[provider],
                "apiKey": api_key,
                "api": "openai-completions",
                "enabled": True,
                "models": []
            }
        else:
            # 更新 API Key
            config['providers'][provider]['apiKey'] = api_key
            config['providers'][provider]['enabled'] = True
            if base_url:
                config['providers'][provider]['baseUrl'] = base_url
        
        # 添加模型（如果不存在）
        models = config['providers'][provider].get('models', [])
        model_exists = any(m.get('id') == model_id for m in models)
        
        if not model_exists:
            models.append({
                "id": model_id,
                "name": model_id.capitalize()
            })
            config['providers'][provider]['models'] = models
        
        # 保存
        self._save_config(config)
        
        print(f"✅ 模型已添加")
        print(f"\n📋 模型信息:")
        print(f"   提供商: {provider}")
        print(f"   模型ID: {model_id}")
        print(f"   完整名称: {provider}/{model_id}")
        print(f"   API地址: {config['providers'][provider]['baseUrl']}")
        print(f"\n🎯 下一步:")
        print(f"   查看模型: python {__file__} list")
        print(f"   设为默认: python {__file__} set-default {provider}/{model_id}")
        
        return True
    
    def list(self) -> List[Dict[str, Any]]:
        """列出所有模型"""
        print(f"\n{'=' * 80}")
        print(f"📋 模型列表")
        print(f"{'=' * 80}\n")
        
        config = self._load_config()
        providers = config.get('providers', {})
        
        if not providers:
            print("没有配置的模型")
            print(f"\n🎯 添加模型:")
            print(f"   python {__file__} add <提供商> <模型ID> <API Key>")
            return []
        
        # 显示表格
        print(f"{'提供商':<15} {'模型ID':<30} {'状态':<10}")
        print("-" * 80)
        
        model_list = []
        for provider_name, provider_config in providers.items():
            enabled = provider_config.get('enabled', True)  # 默认为 True
            has_key = bool(provider_config.get('apiKey', '').strip())
            status = '✅ 可用' if (enabled and has_key) else '⚠️  未配置'
            
            models = provider_config.get('models', [])
            if not models:
                # 没有模型列表，显示提供商本身
                print(f"{provider_name:<15} {'(通用)':<30} {status:<10}")
                model_list.append({
                    'provider': provider_name,
                    'model': None,
                    'full_name': provider_name,
                    'status': status
                })
            else:
                # 显示所有模型
                for model in models:
                    model_id = model.get('id', 'N/A')
                    full_name = f"{provider_name}/{model_id}"
                    print(f"{provider_name:<15} {model_id:<30} {status:<10}")
                    model_list.append({
                        'provider': provider_name,
                        'model': model_id,
                        'full_name': full_name,
                        'status': status
                    })
        
        print(f"\n总计: {len(model_list)} 个模型配置")
        return model_list
    
    def set_default(self, model_full_name: str) -> bool:
        """
        设置默认模型
        
        Args:
            model_full_name: 完整模型名（如 bailian/qwen3.5-plus）
        
        Returns:
            是否成功
        """
        print(f"\n{'=' * 80}")
        print(f"⭐ 设置默认模型: {model_full_name}")
        print(f"{'=' * 80}\n")
        
        # 验证模型存在
        config = self._load_config()
        
        try:
            provider, model_id = model_full_name.split('/', 1)
        except ValueError:
            print(f"❌ 模型名格式错误，应为: provider/model")
            print(f"   示例: bailian/qwen3.5-plus")
            return False
        
        if provider not in config.get('providers', {}):
            print(f"❌ 提供商不存在: {provider}")
            return False
        
        # 设置默认模型（在 global 配置中）
        if 'global' not in config:
            config['global'] = {}
        config['global']['defaultModel'] = model_full_name
        
        # 保存
        self._save_config(config)
        
        print(f"✅ 默认模型已设置")
        print(f"\n📋 模型信息:")
        print(f"   提供商: {provider}")
        print(f"   模型: {model_id}")
        print(f"   完整名称: {model_full_name}")
        
        return True
    
    def _load_config(self) -> Dict[str, Any]:
        """加载模型配置"""
        if not self.models_file.exists():
            return {}
        
        try:
            with open(self.models_file, 'r') as f:
                return json.load(f)
        except:
            return {}
    
    def _save_config(self, config: Dict[str, Any]):
        """保存模型配置"""
        self.models_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(self.models_file, 'w') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
    
    # ==================== 配置修复功能（整合自 scripts/fix_all_models.py） ====================
    
    def fix_config(self, instance_name: Optional[str] = None) -> int:
        """
        修复模型配置
        
        Args:
            instance_name: 实例名称（None=所有实例）
        
        Returns:
            退出码 (0=成功, 1=失败)
        """
        print("=" * 80)
        print("🔧 修复龙虾实例模型配置")
        print("=" * 80)
        print()
        
        # 读取全局模型配置
        global_models_file = self.pm.get_data_dir() / 'models.json'
        
        if not global_models_file.exists():
            print(f"❌ 全局模型配置不存在: {global_models_file}")
            print(f"   请先配置全局模型: workspace/data/models.json")
            return 1
        
        print(f"📖 读取全局模型配置: {global_models_file}")
        with open(global_models_file, 'r') as f:
            global_models = json.load(f)
        
        # 检查配置格式
        if 'providers' not in global_models:
            print(f"❌ 全局配置格式错误，缺少 'providers' 字段")
            return 1
        
        print(f"✅ 全局配置格式正确")
        print()
        
        # 获取要修复的实例
        if instance_name:
            instance_path = self.pm.get_instance_path(instance_name)
            if not instance_path.exists():
                print(f"❌ 实例不存在: {instance_name}")
                return 1
            instances = [instance_path]
            print(f"📋 修复单个实例: {instance_name}\n")
        else:
            lobsters_dir = self.pm.get_lobsters_dir()
            if not lobsters_dir.exists():
                print(f"⚠️  实例目录不存在: {lobsters_dir}")
                return 0
            instances = [d for d in lobsters_dir.iterdir() if d.is_dir()]
            if not instances:
                print(f"ℹ️  没有找到实例")
                return 0
            print(f"📋 找到 {len(instances)} 个实例，开始修复...\n")
        
        # 修复每个实例
        success_count = 0
        skip_count = 0
        fail_count = 0
        
        for instance_path in instances:
            result = self._fix_instance_config(instance_path, global_models)
            if result == 'fixed':
                success_count += 1
            elif result == 'skip':
                skip_count += 1
            else:
                fail_count += 1
        
        # 总结
        print()
        print("=" * 80)
        print("📊 修复完成")
        print("=" * 80)
        print(f"总实例数: {len(instances)}")
        print(f"已修复: {success_count}")
        print(f"无需修复: {skip_count}")
        print(f"修复失败: {fail_count}")
        print()
        
        if success_count > 0:
            print("⚠️  注意: 请重启修复过的实例以应用配置\n")
        
        return 0 if fail_count == 0 else 1
    
    def _fix_instance_config(self, instance_path: Path, global_models: dict) -> str:
        """
        修复单个实例的模型配置
        
        Returns:
            'fixed': 已修复, 'skip': 无需修复, 'fail': 修复失败
        """
        config_file = instance_path / '.openclaw' / 'openclaw.json'
        
        if not config_file.exists():
            print(f"  ⚠️  {instance_path.name}: 配置文件不存在")
            return 'fail'
        
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
            
            # 检查是否已有 models 配置
            has_models = 'models' in config and 'providers' in config.get('models', {})
            
            if has_models:
                print(f"  ✅ {instance_path.name}: 配置完整，无需修复")
                return 'skip'
            
            print(f"  ⚠️  {instance_path.name}: 缺少 models 配置，开始修复...")
            
            # 添加 models 配置
            if 'providers' in global_models:
                if 'models' not in config:
                    config['models'] = {}
                config['models']['providers'] = global_models['providers']
            
            # 确保 agents.defaults.models 存在
            if 'agents' not in config:
                config['agents'] = {}
            if 'defaults' not in config['agents']:
                config['agents']['defaults'] = {}
            if 'models' not in config['agents']['defaults']:
                config['agents']['defaults']['models'] = {}
            
            # 添加所有模型到可用列表
            for provider, provider_config in global_models.get('providers', {}).items():
                models = provider_config.get('models', [])
                for model_info in models:
                    model_id = f"{provider}/{model_info['id']}"
                    if model_id not in config['agents']['defaults']['models']:
                        config['agents']['defaults']['models'][model_id] = {}
            
            # 备份原配置
            backup_file = config_file.with_suffix('.json.backup')
            with open(backup_file, 'w') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            # 保存修复后的配置
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            print(f"  ✅ {instance_path.name}: 配置已修复")
            return 'fixed'
            
        except Exception as e:
            print(f"  ❌ {instance_path.name}: 修复失败 - {e}")
            return 'fail'
    
    # ==================== 模板初始化功能 ====================
    
    def list_templates(self) -> List[Dict[str, Any]]:
        """列出所有可用的模型模板"""
        templates_dir = Path(__file__).parent.parent / 'templates'
        
        if not templates_dir.exists():
            return []
        
        templates = []
        for template_file in templates_dir.glob('*.json'):
            try:
                with open(template_file, 'r') as f:
                    template = json.load(f)
                    templates.append({
                        'file': template_file.name,
                        'name': template.get('name', template_file.stem),
                        'description': template.get('description', ''),
                        'provider': template.get('provider', ''),
                        'model_count': len(template.get('models', []))
                    })
            except Exception as e:
                print(f"⚠️ 读取模板失败 {template_file.name}: {e}")
        
        return templates
    
    def init_from_template(self, template_name: str, api_key: str, 
                          instance_name: Optional[str] = None,
                          set_as_default: bool = True) -> bool:
        """
        从模板初始化模型配置
        
        Args:
            template_name: 模板名称（如 bailian-coding-models）
            api_key: API密钥
            instance_name: 实例名称（None=仅更新全局配置）
            set_as_default: 是否将第一个模型设为默认
        
        Returns:
            是否成功
        """
        print("=" * 80)
        print(f"🚀 从模板初始化模型配置")
        print("=" * 80)
        print()
        
        # 查找模板文件
        templates_dir = Path(__file__).parent.parent / 'templates'
        template_file = templates_dir / f"{template_name}.json"
        
        if not template_file.exists():
            print(f"❌ 模板不存在: {template_file}")
            print(f"\n可用模板:")
            for tpl in self.list_templates():
                print(f"  - {tpl['file'].replace('.json', '')}: {tpl['name']}")
            return False
        
        # 读取模板
        print(f"📖 读取模板: {template_file.name}")
        with open(template_file, 'r') as f:
            template = json.load(f)
        
        provider = template['provider']
        base_url = template['baseUrl']
        api_type = template.get('api', 'openai-completions')
        models = template['models']
        
        print(f"   提供商: {provider}")
        print(f"   API地址: {base_url}")
        print(f"   模型数量: {len(models)}")
        print()
        
        # 1. 更新全局配置
        print("📝 更新全局模型配置...")
        
        if not self.models_file.exists():
            config = {"providers": {}}
        else:
            with open(self.models_file, 'r') as f:
                config = json.load(f)
        
        if 'providers' not in config:
            config['providers'] = {}
        
        config['providers'][provider] = {
            'baseUrl': base_url,
            'apiKey': api_key,
            'api': api_type,
            'models': models
        }
        
        with open(self.models_file, 'w') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        print(f"   ✅ 全局配置已更新")
        print(f"   ✅ 已添加 {len(models)} 个模型:")
        for model in models[:5]:  # 只显示前5个
            img_support = " 📷" if "image" in model.get('input', []) else ""
            print(f"      - {model['id']}{img_support}")
        if len(models) > 5:
            print(f"      ... 等 {len(models)} 个模型")
        print()
        
        # 2. 更新实例配置（如果指定）
        if instance_name:
            print(f"📝 更新实例配置: {instance_name}")
            instance_path = self.pm.get_instance_path(instance_name)
            config_file = instance_path / '.openclaw' / 'openclaw.json'
            
            if not config_file.exists():
                print(f"   ⚠️ 实例配置不存在，跳过")
            else:
                with open(config_file, 'r') as f:
                    instance_config = json.load(f)
                
                # 更新 models 部分
                if 'models' not in instance_config:
                    instance_config['models'] = {}
                if 'providers' not in instance_config['models']:
                    instance_config['models']['providers'] = {}
                
                instance_config['models']['providers'][provider] = {
                    'baseUrl': base_url,
                    'apiKey': api_key,
                    'api': api_type,
                    'models': models
                }
                
                # 更新 agents.defaults.models 列表
                if 'agents' not in instance_config:
                    instance_config['agents'] = {}
                if 'defaults' not in instance_config['agents']:
                    instance_config['agents']['defaults'] = {}
                if 'models' not in instance_config['agents']['defaults']:
                    instance_config['agents']['defaults']['models'] = {}
                
                # 添加所有模型到可用列表
                for model in models:
                    model_full_name = f"{provider}/{model['id']}"
                    instance_config['agents']['defaults']['models'][model_full_name] = {}
                
                # 设置默认模型（如果需要）
                if set_as_default and models:
                    if 'model' not in instance_config['agents']['defaults']:
                        instance_config['agents']['defaults']['model'] = {}
                    instance_config['agents']['defaults']['model']['primary'] = f"{provider}/{models[0]['id']}"
                    print(f"   ✅ 默认模型设为: {provider}/{models[0]['id']}")
                
                # 保存配置
                with open(config_file, 'w') as f:
                    json.dump(instance_config, f, indent=2, ensure_ascii=False)
                
                print(f"   ✅ 实例配置已更新")
        
        print()
        print("=" * 80)
        print("🎉 模板初始化完成！")
        print("=" * 80)
        print()
        print("🎯 下一步:")
        if instance_name:
            print(f"   重启实例: python skills/openclaw-manager/scripts/instance_manager.py restart {instance_name}")
        print(f"   查看模型: python skills/openclaw-model/scripts/model_manager.py list")
        print()
        
        return True


def main():
    """命令行入口"""
    parser = argparse.ArgumentParser(description='OpenClaw 模型管理器')
    subparsers = parser.add_subparsers(dest='command', help='命令')
    
    # add 命令
    add_parser = subparsers.add_parser('add', help='添加模型')
    add_parser.add_argument('provider', help='提供商（bailian/openai/anthropic等）')
    add_parser.add_argument('model_id', help='模型ID（如 qwen3.5-plus）')
    add_parser.add_argument('api_key', help='API密钥')
    add_parser.add_argument('--base-url', help='API地址（可选）')
    
    # list 命令
    list_parser = subparsers.add_parser('list', help='列出所有模型')
    
    # set-default 命令
    default_parser = subparsers.add_parser('set-default', help='设置默认模型')
    default_parser.add_argument('model', help='模型名（如 bailian/qwen3.5-plus）')
    
    # fix-config 命令
    fix_parser = subparsers.add_parser('fix-config', help='修复实例模型配置')
    fix_parser.add_argument('instance', nargs='?', help='实例名称（可选，不指定则修复所有）')
    
    # list-templates 命令
    list_tpl_parser = subparsers.add_parser('list-templates', help='列出可用的模型模板')
    
    # init-from-template 命令
    init_parser = subparsers.add_parser('init-from-template', help='从模板初始化模型配置')
    init_parser.add_argument('template', help='模板名称（如 bailian-coding-models）')
    init_parser.add_argument('api_key', help='API密钥')
    init_parser.add_argument('--instance', help='实例名称（可选，不指定则仅更新全局配置）')
    init_parser.add_argument('--no-default', action='store_true', help='不设置默认模型')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # 创建管理器
    manager = ModelManager()
    
    # 执行命令
    try:
        if args.command == 'add':
            manager.add(args.provider, args.model_id, args.api_key, args.base_url)
        elif args.command == 'list':
            manager.list()
        elif args.command == 'set-default':
            manager.set_default(args.model)
        elif args.command == 'fix-config':
            exit_code = manager.fix_config(args.instance)
            sys.exit(exit_code)
        elif args.command == 'list-templates':
            templates = manager.list_templates()
            if not templates:
                print("📋 没有可用的模板")
            else:
                print("=" * 80)
                print("📋 可用的模型模板")
                print("=" * 80)
                print()
                for tpl in templates:
                    print(f"📦 {tpl['file'].replace('.json', '')}")
                    print(f"   名称: {tpl['name']}")
                    print(f"   描述: {tpl['description']}")
                    print(f"   提供商: {tpl['provider']}")
                    print(f"   模型数: {tpl['model_count']}")
                    print()
        elif args.command == 'init-from-template':
            set_default = not args.no_default
            manager.init_from_template(args.template, args.api_key, args.instance, set_default)
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
