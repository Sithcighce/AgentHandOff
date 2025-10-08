#!/usr/bin/env python3
"""
调试server.py文件的导入问题
"""

import sys
import traceback
import os

# 添加当前路径
sys.path.insert(0, os.path.join(os.getcwd(), 'src'))

print("=== Agent-Handoff 导入调试 ===")

# 1. 检查基础模块导入
print("\n1. 检查基础依赖...")
try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import Tool, TextContent
    print("✅ MCP 依赖导入成功")
except ImportError as e:
    print(f"❌ MCP 依赖导入失败: {e}")
    sys.exit(1)

# 2. 尝试导入模块
print("\n2. 导入agent_handoff模块...")
try:
    import agent_handoff.server as server_module
    print("✅ 模块导入成功")
    print(f"模块属性: {dir(server_module)}")
except Exception as e:
    print(f"❌ 模块导入失败: {e}")
    traceback.print_exc()

# 3. 尝试直接执行文件内容
print("\n3. 尝试直接执行文件...")
server_path = os.path.join("src", "agent_handoff", "server.py")

try:
    # 读取文件内容并执行
    with open(server_path, 'r', encoding='utf-8') as f:
        source_code = f.read()
    
    # 创建命名空间并执行
    namespace = {}
    exec(source_code, namespace)
    
    print("✅ 文件执行成功")
    print(f"命名空间包含: {[k for k in namespace.keys() if not k.startswith('__')]}")
    
    # 检查是否有AgentHandoffServer
    if 'AgentHandoffServer' in namespace:
        print("✅ 找到 AgentHandoffServer 类")
        cls = namespace['AgentHandoffServer']
        print(f"类信息: {cls}")
    else:
        print("❌ 未找到 AgentHandoffServer 类")

except Exception as e:
    print(f"❌ 文件执行失败: {e}")
    traceback.print_exc()

print("\n=== 调试完成 ===")