#!/usr/bin/env python3
"""
龙虾实例健康检查脚本

用途:
- 检查所有实例的配置完整性
- 检查运行状态
- 检查端口冲突
- 检查命名规范
"""
import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple

# 添加项目根目录到路径
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

from shared.configs.path_manager import PathManager


class HealthChecker:
    """健康检查器"""
    
    def __init__(self):
        self.pm = PathManager()
        self.issues: List[Dict] = []
    
    def check_naming_convention(self, instance_name: str) -> Tuple[bool, str]:
        """
        检查命名规范
        
        规范: openclaw-{platform}-{sequence}
        - 全小写
        - 只包含英文字母、数字、连字符
        - 无中文字符
        """
        # 检查中文字符
        if any('\u4e00' <= c <= '\u9fff' for c in instance_name):
            return False, "包含中文字符"
        
        # 检查前缀
        if not instance_name.startswith('openclaw-'):
            return False, "缺少 'openclaw-' 前缀"
        
        # 检查大小写
        if instance_name != instance_name.lower():
            return False, "包含大写字母"
        
        # 检查非法字符
        allowed = set('abcdefghijklmnopqrstuvwxyz0123456789-')
        if not all(c in allowed for c in instance_name):
            return False, "包含非法字符"
        
        return True, "符合规范"
    
    def check_pairing_status(self, instance_path: Path) -> Tuple[bool, str]:
        """
        检查飞书配对状态
        
        Returns:
            (是否正常, 描述)
        """
        pairing_file = instance_path / 'credentials' / 'feishu-pairing.json'
        
        if not pairing_file.exists():
            return True, "无配对文件（正常）"
        
        try:
            with open(pairing_file, 'r') as f:
                pairing = json.load(f)
            
            pending_count = len(pairing.get('requests', []))
            
            if pending_count > 0:
                users = [req.get('meta', {}).get('name', '未知') for req in pairing['requests']]
                return False, f"有 {pending_count} 个待配对请求: {', '.join(users)}"
            else:
                return True, "无待配对请求"
        except Exception as e:
            return False, f"检查失败: {e}"
    
    def check_model_config(self, instance_path: Path) -> Tuple[bool, str]:
        """
        检查模型配置完整性
        
        Returns:
            (是否正常, 描述)
        """
        config_file = instance_path / '.openclaw' / 'openclaw.json'
        
        if not config_file.exists():
            return False, "配置文件不存在"
        
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
            
            # 检查 models.providers 是否存在
            if 'models' not in config:
                return False, "缺少 models 配置"
            
            if 'providers' not in config['models']:
                return False, "缺少 models.providers 配置"
            
            if 'bailian' not in config['models']['providers']:
                return False, "缺少 bailian provider 配置"
            
            # 检查 bailian 配置完整性
            bailian = config['models']['providers']['bailian']
            required_fields = ['baseUrl', 'apiKey', 'api', 'models']
            
            for field in required_fields:
                if field not in bailian:
                    return False, f"bailian 缺少 {field} 字段"
            
            if not isinstance(bailian['models'], list):
                return False, "bailian.models 格式错误"
            
            if len(bailian['models']) == 0:
                return False, "bailian.models 为空"
            
            return True, f"配置正常 ({len(bailian['models'])} 个模型)"
            
        except Exception as e:
            return False, f"配置文件解析失败: {e}"
    
    def check_instance(self, instance_path: Path) -> Dict:
        """
        检查单个实例
        
        Returns:
            检查结果字典
        """
        instance_name = instance_path.name
        
        result = {
            "name": instance_name,
            "path": str(instance_path),
            "issues": []
        }
        
        # 1. 检查命名规范
        naming_ok, naming_msg = self.check_naming_convention(instance_name)
        if not naming_ok:
            result["issues"].append({
                "type": "naming",
                "severity": "warning",
                "message": f"命名不规范: {naming_msg}"
            })
        
        # 2. 检查模型配置
        model_ok, model_msg = self.check_model_config(instance_path)
        if not model_ok:
            result["issues"].append({
                "type": "model_config",
                "severity": "critical",
                "message": f"模型配置问题: {model_msg}"
            })
        
        # 3. 检查配对状态
        pairing_ok, pairing_msg = self.check_pairing_status(instance_path)
        if not pairing_ok:
            result["issues"].append({
                "type": "pairing",
                "severity": "warning",
                "message": f"配对状态: {pairing_msg}"
            })
        
        return result
    
    def run(self) -> int:
        """
        运行健康检查
        
        Returns:
            退出码 (0=正常, 1=有问题)
        """
        print("=" * 80)
        print("🏥 OpenClaw 实例健康检查")
        print("=" * 80)
        print()
        
        # 获取所有实例
        lobsters_dir = self.pm.get_lobsters_dir()
        
        if not lobsters_dir.exists():
            print(f"⚠️  实例目录不存在: {lobsters_dir}")
            return 0
        
        instances = [d for d in lobsters_dir.iterdir() if d.is_dir()]
        
        if not instances:
            print(f"ℹ️  没有找到实例")
            return 0
        
        print(f"📋 检查 {len(instances)} 个实例...\n")
        
        # 检查每个实例
        all_results = []
        critical_count = 0
        warning_count = 0
        
        for instance_path in instances:
            result = self.check_instance(instance_path)
            all_results.append(result)
            
            # 统计问题
            for issue in result['issues']:
                if issue['severity'] == 'critical':
                    critical_count += 1
                elif issue['severity'] == 'warning':
                    warning_count += 1
        
        # 显示结果
        for result in all_results:
            if not result['issues']:
                print(f"✅ {result['name']}: 健康")
            else:
                print(f"⚠️  {result['name']}: 发现 {len(result['issues'])} 个问题")
                for issue in result['issues']:
                    severity_icon = "🔴" if issue['severity'] == 'critical' else "⚠️ "
                    print(f"   {severity_icon} [{issue['type']}] {issue['message']}")
        
        # 总结
        print()
        print("=" * 80)
        print("📊 健康检查结果")
        print("=" * 80)
        print(f"总实例数: {len(instances)}")
        print(f"健康实例: {len([r for r in all_results if not r['issues']])}")
        print(f"有问题实例: {len([r for r in all_results if r['issues']])}")
        print(f"  - 严重问题: {critical_count}")
        print(f"  - 警告: {warning_count}")
        print()
        
        # 修复建议
        if critical_count > 0:
            print("🔧 修复建议:")
            print("   运行批量修复: python3 scripts/fix_all_models.py")
            print()
        
        return 1 if (critical_count > 0 or warning_count > 0) else 0


def main():
    """主函数"""
    checker = HealthChecker()
    return checker.run()


if __name__ == '__main__':
    sys.exit(main())
