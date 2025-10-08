#!/usr/bin/env python3
"""
逐行调试server.py执行问题
"""

import sys
import os
import ast

sys.path.insert(0, os.path.join(os.getcwd(), 'src'))

print("=== 逐行分析 server.py ===")

server_path = os.path.join("src", "agent_handoff", "server.py")

# 读取并解析文件
with open(server_path, 'r', encoding='utf-8') as f:
    source_code = f.read()

print(f"文件大小: {len(source_code)} 字符")
print(f"行数: {len(source_code.splitlines())}")

# 尝试AST解析
try:
    tree = ast.parse(source_code)
    print("✅ AST解析成功")
    
    # 查找类定义
    classes = [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
    print(f"找到 {len(classes)} 个类定义:")
    
    for cls in classes:
        print(f"  - {cls.name} (行 {cls.lineno})")
    
    # 查找函数定义
    functions = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
    print(f"找到 {len(functions)} 个函数定义")
    
except SyntaxError as e:
    print(f"❌ AST解析失败: {e}")
    print(f"错误位置: 行 {e.lineno}, 列 {e.offset}")

# 尝试逐步执行前面部分
print("\n=== 逐步执行测试 ===")

lines = source_code.splitlines()
accumulated_code = ""

for i, line in enumerate(lines[:50], 1):  # 只检查前50行
    accumulated_code += line + "\n"
    
    if line.strip().startswith("class AgentHandoffServer"):
        print(f"✅ 找到类定义在第 {i} 行")
        
        # 尝试执行到类定义为止
        try:
            namespace = {}
            exec(accumulated_code, namespace)
            if 'AgentHandoffServer' in namespace:
                print("✅ 类定义执行成功")
            else:
                print("❌ 类定义执行但未生效")
        except Exception as e:
            print(f"❌ 执行失败: {e}")
        break

print("=== 分析完成 ===")