#!/usr/bin/env python3
"""
Agent-Handoff MCP Server
Refactored version with separated tool handlers
"""

import asyncio
import logging
from pathlib import Path
from typing import Any, List

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from .tools import WorkflowToolsHandler, UtilityToolsHandler

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("agent-handoff")

class AgentHandoffServer:
    """
    🚨🚨🚨 CRITICAL: MANDATORY WORKFLOW ENFORCEMENT 🚨🚨🚨
    
    Agent-Handoff MCP Server - Structured Development Workflow System
    
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    BEFORE YOU DO ANYTHING ELSE:
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    This server enforces a STRICT MANDATORY WORKFLOW. You CANNOT skip steps.
    
    📋 REQUIRED WORKFLOW (IN ORDER):
    
    1. 🚨 start_work     → FIRST! Initialize session and get context
    2. 📋 plan_setup     → Submit your development plan  
    3. ✅ proceed        → Report completed work (REQUIRED at least once)
    4. 🏁 end_job        → Finalize and handoff (only after proceed)
    
    ⚠️  ENFORCEMENT RULES:
    - You MUST call start_work BEFORE any development work
    - You CANNOT call end_job without calling proceed first
    - Skipping steps will result in WORKFLOW_VIOLATION errors
    - All work is tracked and validated
    
    💡 WHY THIS MATTERS:
    - Maintains project continuity across AI sessions
    - Creates structured handoff documentation
    - Ensures accountability and progress tracking
    
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    START EVERY SESSION WITH: start_work(user_goal="...")
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    """
    
    def __init__(self):
        self.server = Server("agent-handoff")
        self.project_root = Path.cwd()
        self.docs_dir = self.project_root / "docs"
        self.config_dir = self.project_root / ".agent-handoff"
        
        # Initialize tool handlers
        self.workflow_handler = WorkflowToolsHandler(self.project_root, self.config_dir)
        self.utility_handler = UtilityToolsHandler(self.project_root, self.docs_dir)
        
        # Register all tool handlers
        self._register_handlers()
        logger.info("Agent-Handoff MCP server initialized")
        logger.info("🚨 WORKFLOW ENFORCEMENT ACTIVE: start_work → plan_setup → proceed → end_job")
    
    def _register_handlers(self):
        """Register all tool handlers"""
        
        @self.server.list_tools()
        async def list_tools() -> List[Tool]:
            """Return all available tools"""
            tools = []
            tools.extend(self.workflow_handler.get_workflow_tools())
            tools.extend(self.utility_handler.get_utility_tools())
            return tools
        
        @self.server.call_tool()
        async def call_tool(name: str, arguments: Any) -> List[TextContent]:
            """Route tool calls to appropriate handlers"""
            try:
                # Workflow tools
                if name == "start_work":
                    return await self.workflow_handler.handle_start_work(arguments)
                elif name == "plan_setup":
                    return await self.workflow_handler.handle_plan_setup(arguments)
                elif name == "proceed":
                    return await self.workflow_handler.handle_proceed(arguments)
                elif name == "report_issue":
                    return await self.workflow_handler.handle_report_issue(arguments)
                elif name == "end_job":
                    return await self.workflow_handler.handle_end_job(arguments)
                
                # Utility tools
                elif name == "read_file":
                    return await self.utility_handler.handle_read_file(arguments)
                elif name == "write_file":
                    return await self.utility_handler.handle_write_file(arguments)
                elif name == "append_file":
                    return await self.utility_handler.handle_append_file(arguments)
                elif name == "list_files":
                    return await self.utility_handler.handle_list_files(arguments)
                elif name == "search_files":
                    return await self.utility_handler.handle_search_files(arguments)
                
                else:
                    error = {
                        "error": {
                            "code": "UNKNOWN_TOOL",
                            "message": f"Unknown tool: {name}"
                        }
                    }
                    import json
                    return [TextContent(type="text", text=json.dumps(error, indent=2))]
                    
            except Exception as e:
                logger.error(f"Tool call error: {e}")
                error = {
                    "error": {
                        "code": "EXECUTION_ERROR",
                        "message": f"Error executing tool {name}: {str(e)}"
                    }
                }
                import json
                return [TextContent(type="text", text=json.dumps(error, indent=2))]

async def main():
    """Start MCP server"""
    logger.info("Starting Agent-Handoff MCP server...")
    
    try:
        server_instance = AgentHandoffServer()
        
        async with stdio_server() as (read_stream, write_stream):
            await server_instance.server.run(
                read_stream,
                write_stream,
                server_instance.server.create_initialization_options()
            )
    except Exception as e:
        logger.error(f"Server startup failed: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())