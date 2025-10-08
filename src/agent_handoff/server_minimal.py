#!/usr/bin/env python3
"""
最小化的Agent-Handoff MCP服务器
用于测试和调试导入问题
"""

import asyncio
import json
import logging
import os
from typing import Any

# 检查MCP导入
try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import Tool, TextContent
    print("✅ MCP依赖导入成功")
except ImportError as e:
    print(f"❌ MCP依赖导入失败: {e}")
    raise

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("agent-handoff")

class AgentHandoffServer:
    """Agent-Handoff MCP 服务器核心 - 简化版"""
    
    def __init__(self):
        print("🚀 初始化AgentHandoffServer...")
        self.server = Server("agent-handoff")
        self.project_root = os.getcwd()
        self.docs_dir = os.path.join(self.project_root, "docs")
        self.config_dir = os.path.join(self.project_root, ".agent-handoff")
        
        # 工作流状态（内存存储）
        self.active_sessions = {}
        
        # 注册工具处理器
        self._register_handlers()
        print("✅ AgentHandoffServer初始化完成")
    
    def _register_handlers(self):
        """注册基础工具处理器"""
        
        @self.server.list_tools()
        async def list_tools() -> list[Tool]:
            """返回工具列表"""
            return [
                Tool(
                    name="test_tool",
                    description="测试工具",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "message": {
                                "type": "string",
                                "description": "测试消息"
                            }
                        },
                        "required": ["message"]
                    }
                )
            ]
        
        @self.server.call_tool()
        async def call_tool(name: str, arguments: Any) -> list[TextContent]:
            """处理工具调用"""
            if name == "test_tool":
                message = arguments.get("message", "Hello World")
                result = {"status": "success", "message": f"收到消息: {message}"}
                return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]
            else:
                error_result = {"error": f"未知工具: {name}"}
                return [TextContent(type="text", text=json.dumps(error_result, ensure_ascii=False, indent=2))]

async def main():
    """启动MCP服务器"""
    logger.info("Agent-Handoff MCP 服务器启动中...")
    
    try:
        server_instance = AgentHandoffServer()
        
        async with stdio_server() as (read_stream, write_stream):
            await server_instance.server.run(
                read_stream,
                write_stream,
                server_instance.server.create_initialization_options()
            )
    except Exception as e:
        logger.error(f"服务器启动失败: {e}")
        raise

if __name__ == "__main__":
    print("🧪 测试版Agent-Handoff MCP服务器")
    asyncio.run(main())