#!/usr/bin/env python3
"""
Agent-Handoff 安装和配置验证脚本
帮助用户正确安装和配置MCP服务器
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def check_installation():
    """检查安装状态"""
    print("🔍 检查Agent-Handoff安装状态...")
    
    try:
        result = subprocess.run([sys.executable, "-c", "import agent_handoff; print(agent_handoff.__version__)"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            version = result.stdout.strip()
            print(f"✅ Agent-Handoff已安装，版本: {version}")
            return True
        else:
            print("❌ Agent-Handoff未正确安装")
            return False
    except Exception as e:
        print(f"❌ 安装检查失败: {e}")
        return False

def install_agent_handoff():
    """安装Agent-Handoff"""
    print("📦 正在安装Agent-Handoff...")
    
    try:
        subprocess.run([
            sys.executable, "-m", "pip", "install", 
            "git+https://github.com/Sithcighce/AgentHandOff.git#egg=agent-handoff"
        ], check=True)
        print("✅ 安装完成")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 安装失败: {e}")
        return False

def test_mcp_server():
    """测试MCP服务器"""
    print("🚀 测试MCP服务器...")
    
    try:
        # 尝试启动服务器并立即终止
        process = subprocess.Popen([
            sys.executable, "-m", "agent_handoff.server"
        ], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        # 发送空输入并等待短时间
        try:
            stdout, stderr = process.communicate(input="", timeout=3)
        except subprocess.TimeoutExpired:
            process.terminate()
            stdout, stderr = process.communicate()
        
        if "No module named" in stderr:
            print("❌ MCP服务器启动失败: 模块未找到")
            return False
        else:
            print("✅ MCP服务器可以启动")
            return True
            
    except Exception as e:
        print(f"❌ MCP服务器测试失败: {e}")
        return False

def generate_vscode_config():
    """生成VSCode MCP配置"""
    python_path = sys.executable.replace("\\", "\\\\")  # 转义反斜杠
    cwd = os.getcwd().replace("\\", "\\\\")
    
    config = {
        "mcp": {
            "servers": {
                "agent-handoff": {
                    "command": python_path,
                    "args": ["-m", "agent_handoff.server"],
                    "cwd": cwd
                }
            }
        }
    }
    
    print("\n⚙️ VSCode MCP配置 (复制到settings.json):")
    print(json.dumps(config, indent=2))
    
    # 尝试找到VSCode配置文件
    vscode_settings_paths = [
        Path.home() / "AppData" / "Roaming" / "Code" / "User" / "settings.json",  # Windows
        Path.home() / ".config" / "Code" / "User" / "settings.json",  # Linux
        Path.home() / "Library" / "Application Support" / "Code" / "User" / "settings.json"  # macOS
    ]
    
    for settings_path in vscode_settings_paths:
        if settings_path.exists():
            print(f"\n📁 VSCode配置文件位置: {settings_path}")
            break

def main():
    """主函数"""
    print("🎯 Agent-Handoff 安装配置助手")
    print("=" * 50)
    
    # 检查安装
    if not check_installation():
        print("\n需要安装Agent-Handoff")
        if input("是否现在安装? (y/n): ").lower() == 'y':
            if not install_agent_handoff():
                print("安装失败，请手动运行:")
                print("pip install git+https://github.com/Sithcighce/AgentHandOff.git#egg=agent-handoff")
                return
        else:
            print("请先安装Agent-Handoff")
            return
    
    # 测试MCP服务器
    if not test_mcp_server():
        print("\nMCP服务器测试失败，可能需要:")
        print("1. 重新安装: pip uninstall agent-handoff && pip install git+https://github.com/Sithcighce/AgentHandOff.git#egg=agent-handoff")
        print("2. 检查Python环境")
        return
    
    # 生成配置
    generate_vscode_config()
    
    print("\n✅ 设置完成！")
    print("\n📋 下一步:")
    print("1. 复制上面的JSON配置到VSCode settings.json")
    print("2. 重启VSCode")
    print("3. 在项目中运行: agent-handoff init")
    print("4. 在Copilot中说: '调用 start_work，我要开始开发'")
    
    # 提供诊断命令
    print(f"\n🔧 如果有问题，运行诊断: {sys.executable} -m agent_handoff.cli diagnose")

if __name__ == "__main__":
    main()