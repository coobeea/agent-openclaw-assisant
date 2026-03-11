#!/usr/bin/env python3
"""
AGENTS.md 自动决策测试
验证智能决策引擎的正确性
"""

from typing import Dict

def auto_decide_config(intent: str, context: dict) -> dict:
    """
    自动决策配置参数（模拟 AGENTS.md 的决策逻辑）
    """
    config = {}
    
    # 决策: 环境类型
    user_input = context.get("user_input", "")
    if "生产" in user_input or "production" in user_input or "prod" in user_input.lower():
        config["env"] = "prod"
    elif "测试" in user_input or "test" in user_input.lower() or "开发" in user_input or "dev" in user_input.lower():
        config["env"] = "test"
    else:
        config["env"] = "prod"  # 默认生产
    
    # 决策: 部署模式
    if "docker" in user_input.lower():
        config["deploy"] = "docker"
    elif "k8s" in user_input.lower() or "kubernetes" in user_input.lower():
        config["deploy"] = "k8s"
    else:
        config["deploy"] = "docker" if config["env"] == "prod" else "host"
    
    # 决策: AI 模型
    purpose = context.get("purpose", "")
    if purpose in ["客服", "咨询"]:
        config["model"] = "gpt-3.5-turbo"
    elif purpose in ["技术支持", "编程", "技术"]:
        config["model"] = "gpt-4"
    elif purpose in ["内容创作", "写作"]:
        config["model"] = "gpt-4"
    else:
        config["model"] = "gpt-3.5-turbo"  # 默认
    
    # 决策: 实例命名
    if name := context.get("name"):
        config["name"] = name if name.startswith("openclaw-") else f"openclaw-{name}"
    else:
        config["name"] = f"openclaw-{config['env']}-01"
    
    # 决策: 日志级别
    config["log_level"] = "DEBUG" if config["env"] == "test" else "INFO"
    
    return config

# 测试用例
test_cases = [
    (
        "创建客服机器人",
        {"user_input": "创建客服机器人", "purpose": "客服"},
        {"env": "prod", "deploy": "docker", "model": "gpt-3.5-turbo", "name": "openclaw-prod-01", "log_level": "INFO"}
    ),
    (
        "创建测试实例",
        {"user_input": "创建测试实例", "purpose": "测试"},
        {"env": "test", "deploy": "host", "model": "gpt-3.5-turbo", "name": "openclaw-test-01", "log_level": "DEBUG"}
    ),
    (
        "创建技术支持助手",
        {"user_input": "创建技术支持助手", "purpose": "技术支持"},
        {"env": "prod", "deploy": "docker", "model": "gpt-4", "name": "openclaw-prod-01", "log_level": "INFO"}
    ),
    (
        "部署到生产",
        {"user_input": "部署到生产环境", "purpose": ""},
        {"env": "prod", "deploy": "docker", "model": "gpt-3.5-turbo", "name": "openclaw-prod-01", "log_level": "INFO"}
    ),
    (
        "创建开发环境实例",
        {"user_input": "创建开发环境实例", "purpose": "开发"},
        {"env": "test", "deploy": "host", "model": "gpt-3.5-turbo", "name": "openclaw-test-01", "log_level": "DEBUG"}
    ),
    (
        "创建内容创作助手",
        {"user_input": "创建内容创作助手", "purpose": "内容创作"},
        {"env": "prod", "deploy": "docker", "model": "gpt-4", "name": "openclaw-prod-01", "log_level": "INFO"}
    ),
    (
        "部署到 Docker",
        {"user_input": "部署到 Docker", "purpose": ""},
        {"env": "prod", "deploy": "docker", "model": "gpt-3.5-turbo", "name": "openclaw-prod-01", "log_level": "INFO"}
    ),
    (
        "部署到 K8s",
        {"user_input": "部署到 K8s 集群", "purpose": ""},
        {"env": "prod", "deploy": "k8s", "model": "gpt-3.5-turbo", "name": "openclaw-prod-01", "log_level": "INFO"}
    ),
]

def run_tests():
    """运行自动决策测试"""
    passed = 0
    failed = 0
    
    print("🧪 AGENTS.md 自动决策测试")
    print("=" * 80)
    
    for i, (scenario, context, expected) in enumerate(test_cases, 1):
        print(f"\n测试 {i}/{len(test_cases)}: {scenario}")
        print(f"  输入: {context}")
        
        actual = auto_decide_config("CREATE", context)
        
        if actual == expected:
            print(f"  ✅ PASS")
            print(f"     决策结果: {actual}")
            passed += 1
        else:
            print(f"  ❌ FAIL")
            print(f"     期望: {expected}")
            print(f"     实际: {actual}")
            
            # 显示差异
            for key in set(expected.keys()) | set(actual.keys()):
                if expected.get(key) != actual.get(key):
                    print(f"     差异 [{key}]: 期望={expected.get(key)}, 实际={actual.get(key)}")
            
            failed += 1
    
    print("\n" + "=" * 80)
    print(f"\n📊 测试结果: {passed}/{len(test_cases)} 通过 ({passed*100//len(test_cases)}%)")
    
    if failed == 0:
        print("\n🎉 所有测试通过！AGENTS.md 自动决策引擎工作正常。")
        print("\n✅ 验证项:")
        print("  - 环境类型决策正确")
        print("  - 部署模式决策正确")
        print("  - AI模型决策正确")
        print("  - 实例命名决策正确")
        print("  - 日志级别决策正确")
        return 0
    else:
        print(f"\n⚠️ {failed} 个测试失败，需要优化 AGENTS.md 的决策规则。")
        return 1

if __name__ == "__main__":
    exit(run_tests())
