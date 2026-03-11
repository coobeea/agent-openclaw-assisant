#!/usr/bin/env python3
"""
飞书配对自动批准脚本
用法: python approve_feishu_pairing.py <instance-name>
"""

import json
import sys
from pathlib import Path
import subprocess


def approve_pairing(instance_name: str) -> bool:
    """
    自动批准飞书配对请求并重启实例
    
    Args:
        instance_name: 实例名称
        
    Returns:
        是否成功
    """
    print("=" * 50)
    print("🔧 飞书配对自动批准脚本")
    print("=" * 50)
    print()
    
    # 获取项目根目录
    project_root = Path(__file__).parent.parent
    instance_path = project_root / 'workspace' / 'lobsters' / instance_name
    
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
    
    pairing_file = instance_path / 'credentials' / 'feishu-pairing.json'
    
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
    
    # 3. 添加到 allowFrom（OpenClaw真正使用的文件）
    allow_from_file = instance_path / 'credentials' / 'feishu-default-allowFrom.json'
    
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
    
    # 4. 重启实例
    print("⚠️  重启实例以应用配对...")
    print()
    
    instance_manager = project_root / 'skills' / 'openclaw-manager' / 'scripts' / 'instance_manager.py'
    
    try:
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
    print("=" * 50)
    print("✅ 配对批准完成并已重启实例")
    print("=" * 50)
    print()
    print("📱 现在可以在飞书里测试了！")
    print()
    print("💡 提示:")
    print("   如果还是没反应，尝试：")
    print(f"   1. 清空去重缓存: rm -f {instance_path}/feishu/dedup/default.json")
    print("   2. 再次重启实例")
    print()
    
    return True


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("❌ 缺少实例名称")
        print()
        print(f"用法: python {Path(__file__).name} <instance-name>")
        print()
        print("示例:")
        print(f"  python {Path(__file__).name} openclaw-feishu-demo")
        sys.exit(1)
    
    instance_name = sys.argv[1]
    
    success = approve_pairing(instance_name)
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
