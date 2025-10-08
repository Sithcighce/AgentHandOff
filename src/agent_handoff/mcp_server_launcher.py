#!/usr/bin/env python3
"""
Agent-Handoff MCP服务器启动脚本
解决模块路径和环境问题
"""

import sys
import os
import asyncio
from pathlib import Path

def setup_python_path():
    """设置Python路径，确保能找到agent_handoff模块"""
    # 获取当前脚本所在目录
    current_dir = Path(__file__).parent.absolute()
    
    # 添加可能的路径
    possible_paths = [
        current_dir,  # 当前目录
        current_dir / "src",  # src目录
        current_dir.parent / "src",  # 上级目录的src
    ]
    
    for path in possible_paths:
        if path.exists():
            sys.path.insert(0, str(path))
    
    # 如果在工作目录中，也添加工作目录
    cwd = Path.cwd()
    if (cwd / "src" / "agent_handoff").exists():
        sys.path.insert(0, str(cwd / "src"))

def main():
    """主函数"""
    # 设置Python路径
    setup_python_path()
    
    try:
        # 尝试导入并运行服务器
        from agent_handoff.server import main as server_main
        asyncio.run(server_main())
    except ImportError as e:
        print(f"错误: 无法导入agent_handoff模块: {e}", file=sys.stderr)
        print("可能的解决方案:", file=sys.stderr)
        print("1. 确保已正确安装: pip install git+https://github.com/Sithcighce/AgentHandOff.git#egg=agent-handoff", file=sys.stderr)
        print("2. 检查Python环境是否正确", file=sys.stderr)
        print("3. 确保在正确的工作目录中运行", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"服务器启动失败: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()