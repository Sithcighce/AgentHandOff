#!/usr/bin/env python3
"""
Agent-Handoff 独立MCP服务器
这个脚本可以在任何项目目录中运行，无需安装agent_handoff包
"""

import asyncio
import json
import logging
import os
import sys
from pathlib import Path
from typing import Any

try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import Tool, TextContent
except ImportError:
    print("错误: 请先安装 MCP 依赖: pip install mcp", file=sys.stderr)
    sys.exit(1)

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("agent-handoff-standalone")


class StandaloneAgentHandoffServer:
    """独立的 Agent-Handoff MCP 服务器"""
    
    def __init__(self):
        self.server = Server("agent-handoff")
        self.project_root = os.getcwd()
        self.docs_dir = os.path.join(self.project_root, "docs")
        self.config_dir = os.path.join(self.project_root, ".agent-handoff")
        
        # 确保必要的目录存在
        os.makedirs(self.docs_dir, exist_ok=True)
        os.makedirs(self.config_dir, exist_ok=True)
        
        # 工作流状态（内存存储）
        self.active_sessions = {}
        
        # 注册工具处理器
        self._register_handlers()
        
        logger.info(f"MCP服务器初始化完成，项目目录: {self.project_root}")
    
    def _register_handlers(self):
        """注册所有 MCP 工具处理器"""
        
        @self.server.list_tools()
        async def list_tools() -> list[Tool]:
            """返回所有可用工具的列表"""
            return [
                Tool(
                    name="read_file",
                    description="读取 docs/ 目录下的文件内容",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "path": {
                                "type": "string",
                                "description": "相对于 docs/ 的文件路径，例如：01_Goals/vision.md"
                            }
                        },
                        "required": ["path"]
                    }
                ),
                Tool(
                    name="write_file",
                    description="写入内容到 docs/ 目录下的文件（会覆盖原内容）",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "path": {
                                "type": "string",
                                "description": "相对于 docs/ 的文件路径"
                            },
                            "content": {
                                "type": "string",
                                "description": "要写入的内容"
                            }
                        },
                        "required": ["path", "content"]
                    }
                ),
                Tool(
                    name="list_files",
                    description="列出 docs/ 目录下的所有文件和子目录",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "path": {
                                "type": "string",
                                "description": "相对于 docs/ 的目录路径，默认为根目录",
                                "default": ""
                            }
                        }
                    }
                ),
                Tool(
                    name="search_files",
                    description="在 docs/ 目录下搜索包含关键词的文件",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "搜索关键词"
                            }
                        },
                        "required": ["query"]
                    }
                ),
                Tool(
                    name="start_work",
                    description="开始一个新的工作会话",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "user_goal": {
                                "type": "string",
                                "description": "用户的目标和需求描述"
                            }
                        },
                        "required": ["user_goal"]
                    }
                ),
                Tool(
                    name="plan_setup",
                    description="设置工作计划和流程",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "session_id": {
                                "type": "string",
                                "description": "会话 ID"
                            },
                            "plan": {
                                "type": "string",
                                "description": "详细的工作计划"
                            }
                        },
                        "required": ["session_id", "plan"]
                    }
                ),
                Tool(
                    name="proceed",
                    description="继续执行下一步工作",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "session_id": {
                                "type": "string",
                                "description": "会话 ID"
                            },
                            "last_step_result": {
                                "type": "string",
                                "description": "上一步的完成情况总结"
                            }
                        },
                        "required": ["session_id", "last_step_result"]
                    }
                ),
                Tool(
                    name="report_issue",
                    description="报告执行过程中遇到的问题或错误",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "session_id": {
                                "type": "string",
                                "description": "会话 ID"
                            },
                            "error_details": {
                                "type": "string",
                                "description": "详细的错误信息"
                            }
                        },
                        "required": ["session_id", "error_details"]
                    }
                ),
                Tool(
                    name="end_job",
                    description="结束任务并提交交接文档",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "session_id": {
                                "type": "string",
                                "description": "会话 ID"
                            },
                            "new_agent_readme": {
                                "type": "string",
                                "description": "更新后的 agentreadme.md 内容"
                            }
                        },
                        "required": ["session_id", "new_agent_readme"]
                    }
                ),
            ]
        
        @self.server.call_tool()
        async def call_tool(name: str, arguments: Any) -> list[TextContent]:
            """处理工具调用"""
            
            try:
                if name == "read_file":
                    result = await self._read_file(arguments["path"])
                elif name == "write_file":
                    result = await self._write_file(arguments["path"], arguments["content"])
                elif name == "list_files":
                    result = await self._list_files(arguments.get("path", ""))
                elif name == "search_files":
                    result = await self._search_files(arguments["query"])
                elif name == "start_work":
                    result = await self._start_work(arguments["user_goal"])
                elif name == "plan_setup":
                    result = await self._plan_setup(arguments["session_id"], arguments["plan"])
                elif name == "proceed":
                    result = await self._proceed(arguments["session_id"], arguments["last_step_result"])
                elif name == "report_issue":
                    result = await self._report_issue(arguments["session_id"], arguments["error_details"])
                elif name == "end_job":
                    result = await self._end_job(arguments["session_id"], arguments["new_agent_readme"])
                else:
                    result = {"error": f"未知工具: {name}"}
                
                return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]
            
            except Exception as e:
                logger.error(f"工具 {name} 执行失败: {e}")
                error_result = {
                    "error": {
                        "code": "TOOL_EXECUTION_ERROR",
                        "message": str(e)
                    }
                }
                return [TextContent(type="text", text=json.dumps(error_result, ensure_ascii=False, indent=2))]
    
    # ============================================================
    # 文件操作工具实现
    # ============================================================
    
    async def _read_file(self, path: str) -> dict:
        """读取文件"""
        full_path = self._safe_path(path)
        if not full_path:
            return {
                "error": {
                    "code": "INVALID_PATH",
                    "message": f"路径必须在 docs/ 目录内: {path}"
                }
            }
        
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return {
                "path": path,
                "content": content,
                "size": len(content),
                "lines": len(content.splitlines())
            }
        
        except FileNotFoundError:
            return {
                "error": {
                    "code": "FILE_NOT_FOUND", 
                    "message": f"文件不存在: {path}"
                }
            }
        except Exception as e:
            return {
                "error": {
                    "code": "READ_ERROR",
                    "message": f"读取文件失败: {str(e)}"
                }
            }
    
    async def _write_file(self, path: str, content: str) -> dict:
        """写入文件"""
        full_path = self._safe_path(path)
        if not full_path:
            return {
                "error": {
                    "code": "INVALID_PATH",
                    "message": f"路径必须在 docs/ 目录内: {path}"
                }
            }
        
        try:
            # 创建目录结构
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            
            # 写入文件
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return {
                "path": path,
                "size": len(content),
                "lines": len(content.splitlines()),
                "status": "success",
                "message": f"文件已保存到 {path}"
            }
        
        except Exception as e:
            return {
                "error": {
                    "code": "WRITE_ERROR",
                    "message": f"写入文件失败: {str(e)}"
                }
            }
    
    async def _list_files(self, path: str = "") -> dict:
        """列出目录内容"""
        full_path = self._safe_path(path)
        if not full_path:
            return {
                "error": {
                    "code": "INVALID_PATH",
                    "message": f"路径必须在 docs/ 目录内: {path}"
                }
            }
        
        try:
            if not os.path.exists(full_path):
                return {
                    "path": path,
                    "files": [],
                    "directories": []
                }
            
            files = []
            directories = []
            
            for item in sorted(os.listdir(full_path)):
                item_path = os.path.join(full_path, item)
                relative_path = os.path.relpath(item_path, self.docs_dir).replace("\\", "/")
                
                if os.path.isfile(item_path):
                    files.append({
                        "name": item,
                        "path": relative_path,
                        "size": os.path.getsize(item_path)
                    })
                elif os.path.isdir(item_path):
                    directories.append({
                        "name": item,
                        "path": relative_path
                    })
            
            return {
                "path": path,
                "files": files,
                "directories": directories,
                "total": len(files) + len(directories)
            }
        
        except Exception as e:
            return {
                "error": {
                    "code": "LIST_ERROR",
                    "message": f"列出目录失败: {str(e)}"
                }
            }
    
    async def _search_files(self, query: str) -> dict:
        """搜索文件内容"""
        try:
            matches = []
            
            for root, dirs, files in os.walk(self.docs_dir):
                for file in files:
                    if not file.endswith(('.md', '.txt')):
                        continue
                    
                    file_path = os.path.join(root, file)
                    relative_path = os.path.relpath(file_path, self.docs_dir).replace("\\", "/")
                    
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        if query.lower() in content.lower():
                            # 查找匹配行
                            lines = content.splitlines()
                            matching_lines = []
                            
                            for i, line in enumerate(lines, 1):
                                if query.lower() in line.lower():
                                    matching_lines.append({
                                        "line_number": i,
                                        "content": line.strip()
                                    })
                            
                            matches.append({
                                "file": relative_path,
                                "matches": len(matching_lines),
                                "lines": matching_lines[:5]  # 限制显示前5个匹配
                            })
                    
                    except Exception:
                        continue  # 跳过无法读取的文件
            
            return {
                "query": query,
                "total_files": len(matches),
                "matches": matches
            }
        
        except Exception as e:
            return {
                "error": {
                    "code": "SEARCH_ERROR",
                    "message": f"搜索失败: {str(e)}"
                }
            }
    
    # ============================================================
    # 工作流管理工具实现
    # ============================================================
    
    async def _start_work(self, user_goal: str) -> dict:
        """开始新的工作会话"""
        try:
            import uuid
            import time
            session_id = str(uuid.uuid4())[:8]
            
            # 读取当前的 agentreadme.md
            agentreadme_path = os.path.join(self.config_dir, "agentreadme.md")
            current_context = ""
            if os.path.exists(agentreadme_path):
                try:
                    with open(agentreadme_path, 'r', encoding='utf-8') as f:
                        current_context = f.read()
                except Exception:
                    current_context = "（无法读取当前项目上下文）"
            else:
                current_context = "（项目暂无历史上下文）"
            
            # 创建会话状态
            self.active_sessions[session_id] = {
                "id": session_id,
                "goal": user_goal,
                "status": "initialized",
                "plan": None,
                "steps": [],
                "created_at": time.time(),
                "project_context": current_context
            }
            
            # 保存会话信息
            session_file = os.path.join(self.config_dir, f"session_{session_id}.json")
            with open(session_file, 'w', encoding='utf-8') as f:
                json.dump(self.active_sessions[session_id], f, ensure_ascii=False, indent=2)
            
            return {
                "session_id": session_id,
                "status": "success",
                "message": "新的工作会话已创建",
                "user_goal": user_goal,
                "project_context": current_context,
                "next_step": "请使用 plan_setup 工具制定详细计划"
            }
        
        except Exception as e:
            return {
                "error": {
                    "code": "SESSION_CREATE_ERROR",
                    "message": f"创建会话失败: {str(e)}"
                }
            }
    
    async def _plan_setup(self, session_id: str, plan: str) -> dict:
        """设置工作计划"""
        try:
            if session_id not in self.active_sessions:
                return {
                    "error": {
                        "code": "SESSION_NOT_FOUND",
                        "message": f"会话 {session_id} 不存在"
                    }
                }
            
            # 更新会话状态
            self.active_sessions[session_id]["plan"] = plan
            self.active_sessions[session_id]["status"] = "planned"
            
            # 保存更新
            session_file = os.path.join(self.config_dir, f"session_{session_id}.json")
            with open(session_file, 'w', encoding='utf-8') as f:
                json.dump(self.active_sessions[session_id], f, ensure_ascii=False, indent=2)
            
            return {
                "session_id": session_id,
                "status": "success",
                "message": "工作计划已设置",
                "plan": plan,
                "next_step": "使用 proceed 工具开始执行第一步"
            }
        
        except Exception as e:
            return {
                "error": {
                    "code": "PLAN_SETUP_ERROR", 
                    "message": f"设置计划失败: {str(e)}"
                }
            }
    
    async def _proceed(self, session_id: str, last_step_result: str) -> dict:
        """继续下一步工作"""
        try:
            if session_id not in self.active_sessions:
                return {
                    "error": {
                        "code": "SESSION_NOT_FOUND",
                        "message": f"会话 {session_id} 不存在"
                    }
                }
            
            import time
            # 记录步骤结果
            step_info = {
                "step": len(self.active_sessions[session_id]["steps"]) + 1,
                "result": last_step_result,
                "timestamp": time.time()
            }
            
            self.active_sessions[session_id]["steps"].append(step_info)
            self.active_sessions[session_id]["status"] = "in_progress"
            
            # 保存更新
            session_file = os.path.join(self.config_dir, f"session_{session_id}.json")
            with open(session_file, 'w', encoding='utf-8') as f:
                json.dump(self.active_sessions[session_id], f, ensure_ascii=False, indent=2)
            
            return {
                "session_id": session_id,
                "step_number": step_info["step"],
                "status": "success",
                "message": f"第 {step_info['step']} 步已完成",
                "next_step": "继续执行下一步，或使用 end_job 结束任务"
            }
        
        except Exception as e:
            return {
                "error": {
                    "code": "PROCEED_ERROR",
                    "message": f"继续执行失败: {str(e)}"
                }
            }
    
    async def _report_issue(self, session_id: str, error_details: str) -> dict:
        """报告问题"""
        try:
            if session_id not in self.active_sessions:
                return {
                    "error": {
                        "code": "SESSION_NOT_FOUND",
                        "message": f"会话 {session_id} 不存在"
                    }
                }
            
            import time
            # 记录问题
            issue_info = {
                "type": "issue",
                "details": error_details,
                "timestamp": time.time()
            }
            
            if "issues" not in self.active_sessions[session_id]:
                self.active_sessions[session_id]["issues"] = []
            
            self.active_sessions[session_id]["issues"].append(issue_info)
            self.active_sessions[session_id]["status"] = "has_issues"
            
            # 保存更新
            session_file = os.path.join(self.config_dir, f"session_{session_id}.json")
            with open(session_file, 'w', encoding='utf-8') as f:
                json.dump(self.active_sessions[session_id], f, ensure_ascii=False, indent=2)
            
            return {
                "session_id": session_id,
                "status": "success",
                "message": "问题已记录",
                "issue_count": len(self.active_sessions[session_id]["issues"]),
                "recommendation": "请分析问题原因并调整计划，然后使用 proceed 继续"
            }
        
        except Exception as e:
            return {
                "error": {
                    "code": "ISSUE_REPORT_ERROR",
                    "message": f"报告问题失败: {str(e)}"
                }
            }
    
    async def _end_job(self, session_id: str, new_agent_readme: str) -> dict:
        """结束任务"""
        try:
            if session_id not in self.active_sessions:
                return {
                    "error": {
                        "code": "SESSION_NOT_FOUND",
                        "message": f"会话 {session_id} 不存在"
                    }
                }
            
            import time
            # 更新会话状态
            self.active_sessions[session_id]["status"] = "completed"
            self.active_sessions[session_id]["completed_at"] = time.time()
            
            # 保存 agentreadme.md
            readme_path = os.path.join(self.config_dir, "agentreadme.md")
            
            with open(readme_path, 'w', encoding='utf-8') as f:
                f.write(new_agent_readme)
            
            # 保存最终会话状态
            session_file = os.path.join(self.config_dir, f"session_{session_id}.json")
            with open(session_file, 'w', encoding='utf-8') as f:
                json.dump(self.active_sessions[session_id], f, ensure_ascii=False, indent=2)
            
            # 从活跃会话中移除
            completed_session = self.active_sessions.pop(session_id)
            
            return {
                "session_id": session_id,
                "status": "success",
                "message": "任务已完成",
                "steps_completed": len(completed_session["steps"]),
                "agentreadme_path": ".agent-handoff/agentreadme.md",
                "session_saved": f".agent-handoff/session_{session_id}.json"
            }
        
        except Exception as e:
            return {
                "error": {
                    "code": "END_JOB_ERROR",
                    "message": f"结束任务失败: {str(e)}"
                }
            }
    
    def _safe_path(self, path: str) -> str:
        """验证路径安全性"""
        if not path:
            path = ""
        
        # 规范化路径
        path = path.replace("\\", "/").strip("/")
        
        # 构造完整路径
        full_path = os.path.join(self.docs_dir, path)
        full_path = os.path.abspath(full_path)
        
        # 验证路径在 docs/ 目录内
        docs_abs = os.path.abspath(self.docs_dir)
        if not full_path.startswith(docs_abs):
            return None
        
        return full_path


async def main():
    """启动 MCP 服务器"""
    logger.info("Agent-Handoff 独立MCP服务器启动中...")
    server_instance = StandaloneAgentHandoffServer()
    
    async with stdio_server() as (read_stream, write_stream):
        await server_instance.server.run(
            read_stream,
            write_stream,
            server_instance.server.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())