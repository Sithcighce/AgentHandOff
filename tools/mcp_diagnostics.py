#!/usr/bin/env python3
"""
MCP服务器环境诊断工具
"""

import sys
import os
import subprocess
from pathlib import Path

def check_python_environment():
    """检查Python环境"""
    print("🔍 Python环境检查:")
    print(f"Python版本: {sys.version}")
    print(f"Python路径: {sys.executable}")
    print(f"工作目录: {os.getcwd()}")
    print()

def check_agent_handoff_installation():
    """检查agent-handoff安装状态"""
    print("📦 Agent-Handoff安装检查:")
    
    try:
        import agent_handoff
        print(f"✅ agent_handoff模块已安装，版本: {agent_handoff.__version__}")
    except ImportError:
        print("❌ agent_handoff模块未安装")
        print("请运行: pip install git+https://github.com/Sithcighce/AgentHandOff.git#egg=agent-handoff")
        return False
    
    try:
        from agent_handoff.server import AgentHandoffServer
        print("✅ MCP服务器模块可用")
    except ImportError as e:
        print(f"❌ MCP服务器模块导入失败: {e}")
        return False
    
    return True

def check_dependencies():
    """检查依赖包"""
    print("🔗 依赖包检查:")
    
    required_packages = ['mcp', 'click']
    all_ok = True
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package} 已安装")
        except ImportError:
            print(f"❌ {package} 未安装")
            all_ok = False
    
    return all_ok

def test_mcp_server():
    """测试MCP服务器启动"""
    print("🚀 MCP服务器启动测试:")
    
    try:
        # 尝试导入服务器
        from agent_handoff.server import AgentHandoffServer
        server = AgentHandoffServer()
        print("✅ MCP服务器可以正常创建")
        return True
    except Exception as e:
        print(f"❌ MCP服务器创建失败: {e}")
        return False

def generate_mcp_config():
    """生成MCP配置"""
    python_path = sys.executable
    cwd = os.getcwd()
    
    print("⚙️ 推荐的MCP配置:")
    print()
    
    config = f'''{{
  "mcp": {{
    "servers": {{
      "agent-handoff": {{
        "command": "{python_path}",
        "args": ["-m", "agent_handoff.server"],
        "cwd": "{cwd}"
      }}
    }}
  }}
}}'''
    
    print(config)
    print()
    
    print("📋 配置步骤:")
    print("1. 复制上面的JSON配置")
    print("2. 打开VSCode设置 (Ctrl+,)")
    print("3. 搜索 'mcp' 或直接编辑settings.json")
    print("4. 粘贴配置并保存")
    print("5. 重启VSCode")

def main():
    """主函数"""
    print("🔧 Agent-Handoff MCP 环境诊断")
    print("=" * 50)
    
    # 检查环境
    check_python_environment()
    
    if not check_agent_handoff_installation():
        print("请先安装agent-handoff后再运行此诊断工具")
        return
    
    if not check_dependencies():
        print("请安装缺失的依赖包")
        return
    
    if not test_mcp_server():
        print("MCP服务器测试失败，请检查安装")
        return
    
    print("✅ 环境检查完成，所有组件正常！")
    print()
    
    generate_mcp_config()

if __name__ == "__main__":
    main()