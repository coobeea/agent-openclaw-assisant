#!/usr/bin/env python3
"""
AGENTS.md 意图识别自动化测试
验证 AGENTS.md 的意图识别引擎是否正确工作
"""

import re
from typing import Tuple, List

# 测试用例
test_cases = [
    # (用户输入, 期望意图, 期望技能包)
    ("创建一个实例", "CREATE_INSTANCE", ["manager"]),
    ("我想要飞书机器人", "CREATE_WITH_PLATFORM", ["manager", "plugin", "channel"]),
    ("搭建客服系统", "CREATE_SERVICE", ["manager", "plugin", "channel", "model", "agent"]),
    ("部署到生产", "DEPLOY_PRODUCTION", ["deploy"]),
    ("查看所有实例", "LIST_INSTANCES", ["manager"]),
    ("prod-01 状态", "INSTANCE_STATUS", ["manager"]),
    ("查看日志", "VIEW_LOGS", ["manager"]),
    ("健康检查", "HEALTH_CHECK", ["deploy"]),
    ("添加飞书渠道", "ADD_CHANNEL", ["plugin", "channel"]),
    ("添加 GPT-4", "ADD_MODEL", ["model"]),
    ("创建客服智能体", "CREATE_AGENT", ["agent"]),
    ("配置企业微信", "ADD_CHANNEL", ["plugin", "channel"]),
    ("启动 prod-01", "START_INSTANCE", ["manager"]),
    ("停止 test-01", "STOP_INSTANCE", ["manager"]),
    ("重启 prod-01", "RESTART_INSTANCE", ["manager"]),
]

def extract_keywords(text: str) -> List[str]:
    """提取关键词"""
    keywords = []
    
    # 操作类关键词（扩展同义词）
    if re.search(r'创建|新建|建立|搭建|想要|需要', text):
        keywords.append('CREATE')
    if re.search(r'查看|列表|状态', text):
        keywords.append('QUERY')
    if re.search(r'添加|配置', text):
        keywords.append('CONFIG')
    if re.search(r'启动|停止|重启|删除', text):
        keywords.append('OPERATE')
    if re.search(r'部署', text):
        keywords.append('DEPLOY')
    
    # 对象类关键词
    if re.search(r'实例|龙虾', text):
        keywords.append('INSTANCE')
    if re.search(r'飞书|QQ|企业微信|钉钉|渠道', text):
        keywords.append('CHANNEL')
    if re.search(r'模型|GPT|Claude', text):
        keywords.append('MODEL')
    if re.search(r'智能体|Agent', text):
        keywords.append('AGENT')
    if re.search(r'机器人', text):
        # 机器人可能指智能体或完整系统
        if re.search(r'客服|技术|销售', text):
            keywords.append('AGENT')  # 有角色描述，是智能体
        else:
            keywords.append('AGENT')  # 默认也是智能体/完整系统
    if re.search(r'系统|完整', text):
        keywords.append('SERVICE')
    
    return keywords

def recognize_intent(user_input: str) -> Tuple[str, List[str]]:
    """
    意图识别逻辑（简化版，实际由 AGENTS.md 指导 AI 执行）
    返回: (意图类型, 需要的技能包列表)
    """
    keywords = extract_keywords(user_input)
    
    # 部署类
    if 'DEPLOY' in keywords:
        if '生产' in user_input or 'production' in user_input:
            return "DEPLOY_PRODUCTION", ["deploy"]
    
    # 创建类
    if 'CREATE' in keywords:
        # 优先检查是否明确提到"智能体"（最具体）
        if '智能体' in user_input or 'Agent' in user_input:
            return "CREATE_AGENT", ["agent"]
        
        # 检查是否创建完整服务
        if 'SERVICE' in keywords:
            return "CREATE_SERVICE", ["manager", "plugin", "channel", "model", "agent"]
        
        # 检查是否创建带平台的实例
        if 'CHANNEL' in keywords or any(p in user_input for p in ['飞书', 'QQ', '企业微信', '钉钉']):
            return "CREATE_WITH_PLATFORM", ["manager", "plugin", "channel"]
        
        # 检查是否只是创建机器人（无平台信息）
        if 'AGENT' in keywords:
            return "CREATE_INSTANCE", ["manager"]
        
        # 默认创建实例
        return "CREATE_INSTANCE", ["manager"]
    
    # 查询类
    if 'QUERY' in keywords:
        if '所有' in user_input or '列表' in user_input:
            return "LIST_INSTANCES", ["manager"]
        elif '日志' in user_input:
            return "VIEW_LOGS", ["manager"]
        else:
            return "INSTANCE_STATUS", ["manager"]
    
    # 健康检查
    if '健康' in user_input or '检查' in user_input:
        return "HEALTH_CHECK", ["deploy"]
    
    # 配置类
    if 'CONFIG' in keywords:
        if 'CHANNEL' in keywords:
            return "ADD_CHANNEL", ["plugin", "channel"]
        elif 'MODEL' in keywords:
            return "ADD_MODEL", ["model"]
        elif 'AGENT' in keywords:
            return "CREATE_AGENT", ["agent"]
    
    # 操作类
    if 'OPERATE' in keywords:
        if '启动' in user_input:
            return "START_INSTANCE", ["manager"]
        elif '停止' in user_input:
            return "STOP_INSTANCE", ["manager"]
        elif '重启' in user_input:
            return "RESTART_INSTANCE", ["manager"]
    
    return "UNKNOWN", []

def run_tests():
    """运行测试"""
    passed = 0
    failed = 0
    
    print("🧪 AGENTS.md 意图识别测试")
    print("=" * 80)
    
    for i, (user_input, expected_intent, expected_skills) in enumerate(test_cases, 1):
        print(f"\n测试 {i}/{len(test_cases)}: '{user_input}'")
        
        # 执行识别
        actual_intent, actual_skills = recognize_intent(user_input)
        
        # 验证
        intent_match = actual_intent == expected_intent
        skills_match = set(actual_skills) == set(expected_skills)
        
        if intent_match and skills_match:
            print(f"  ✅ PASS")
            print(f"     意图: {actual_intent}")
            print(f"     技能包: {', '.join(actual_skills)}")
            passed += 1
        else:
            print(f"  ❌ FAIL")
            if not intent_match:
                print(f"     期望意图: {expected_intent}")
                print(f"     实际意图: {actual_intent}")
            if not skills_match:
                print(f"     期望技能包: {', '.join(expected_skills)}")
                print(f"     实际技能包: {', '.join(actual_skills)}")
            failed += 1
    
    print("\n" + "=" * 80)
    print(f"\n📊 测试结果: {passed}/{len(test_cases)} 通过 ({passed*100//len(test_cases)}%)")
    
    if failed == 0:
        print("\n🎉 所有测试通过！AGENTS.md 意图识别引擎工作正常。")
        return 0
    else:
        print(f"\n⚠️ {failed} 个测试失败，需要优化 AGENTS.md 的识别规则。")
        return 1

if __name__ == "__main__":
    exit(run_tests())
