#!/usr/bin/env python3
"""
测试agent_handoff导入问题
"""

import sys
import os

# 添加src路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

print("测试agent_handoff模块导入...")

try:
    import agent_handoff
    print(f"✅ agent_handoff包导入成功，版本: {agent_handoff.__version__}")
except ImportError as e:
    print(f"❌ agent_handoff包导入失败: {e}")
    sys.exit(1)

try:
    from agent_handoff import server as server_module
    print("✅ server模块导入成功")
    print(f"server模块内容: {dir(server_module)}")
except ImportError as e:
    print(f"❌ server模块导入失败: {e}")
    sys.exit(1)

try:
    # 直接执行server.py文件
    server_py_path = os.path.join(os.path.dirname(__file__), 'src', 'agent_handoff', 'server.py')
    with open(server_py_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    # 检查类定义
    if 'class AgentHandoffServer:' in content:
        print("✅ server.py中找到AgentHandoffServer类定义")
    else:
        print("❌ server.py中未找到AgentHandoffServer类定义")
        
    # 尝试执行模块
    exec_globals = {}
    exec(content, exec_globals)
    
    if 'AgentHandoffServer' in exec_globals:
        print("✅ 通过exec成功加载AgentHandoffServer类")
        cls = exec_globals['AgentHandoffServer']
        print(f"类信息: {cls}")
    else:
        print("❌ exec执行后未找到AgentHandoffServer类")
        print("执行后的全局变量:", list(exec_globals.keys()))
        
except Exception as e:
    print(f"❌ 执行测试时出错: {e}")
    import traceback
    traceback.print_exc()