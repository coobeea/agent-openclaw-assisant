#!/usr/bin/env python3
"""
自动修复所有龙虾实例的模型配置

用途: 批量修复已有实例的 "Unknown model" 问题
"""
import json
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

from shared.configs.path_manager import PathManager


def fix_instance_model_config(instance_path: Path, global_models: dict) -> bool:
    """
    修复单个实例的模型配置
    
    Args:
        instance_path: 实例路径
        global_models: 全局模型配置
    
    Returns:
        是否成功
    """
    config_file = instance_path / '.openclaw' / 'openclaw.json'
    
    if not config_file.exists():
        print(f"  ⚠️  配置文件不存在: {config_file}")
        return False
    
    try:
        # 读取实例配置
        with open(config_file, 'r') as f:
            config = json.load(f)
        
        # 检查是否已有 models 配置
        has_models = 'models' in config and 'providers' in config.get('models', {})
        
        if has_models:
            print(f"  ✅ {instance_path.name}: 配置完整，无需修复")
            return True
        
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
        
        # 添加所有 bailian 模型到可用列表
        if 'bailian' in global_models.get('providers', {}):
            bailian_models = global_models['providers']['bailian'].get('models', [])
            for model_info in bailian_models:
                model_id = f"bailian/{model_info['id']}"
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
        print(f"     备份: {backup_file.name}")
        return True
        
    except Exception as e:
        print(f"  ❌ {instance_path.name}: 修复失败 - {e}")
        return False


def main():
    """主函数"""
    print("=" * 80)
    print("🔧 批量修复龙虾实例模型配置")
    print("=" * 80)
    print()
    
    pm = PathManager()
    
    # 读取全局模型配置
    global_models_file = pm.get_data_dir() / 'models.json'
    
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
    
    if 'bailian' not in global_models['providers']:
        print(f"❌ 全局配置缺少 'bailian' provider")
        return 1
    
    print(f"✅ 全局配置格式正确")
    print(f"   Provider: bailian")
    print(f"   模型数量: {len(global_models['providers']['bailian'].get('models', []))}")
    print()
    
    # 遍历所有实例
    lobsters_dir = pm.get_lobsters_dir()
    
    if not lobsters_dir.exists():
        print(f"⚠️  实例目录不存在: {lobsters_dir}")
        return 0
    
    instances = [d for d in lobsters_dir.iterdir() if d.is_dir()]
    
    if not instances:
        print(f"⚠️  没有找到实例")
        return 0
    
    print(f"📋 找到 {len(instances)} 个实例，开始修复...")
    print()
    
    # 修复每个实例
    success_count = 0
    skip_count = 0
    fail_count = 0
    
    for instance_path in instances:
        result = fix_instance_model_config(instance_path, global_models)
        if result:
            if "无需修复" in str(result):
                skip_count += 1
            else:
                success_count += 1
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
        print("⚠️  注意: 请重启修复过的实例以应用配置")
        print()
        print("重启命令:")
        for instance_path in instances:
            print(f"  python3 skills/openclaw-manager/scripts/instance_manager.py restart {instance_path.name}")
    
    return 0 if fail_count == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
