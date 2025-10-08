#!/usr/bin/env python3
"""
Agent-Handoff MCP Server
Complete implementation based on design specifications
"""

import asyncio
import json
import logging
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("agent-handoff")

class WorkflowState:
    """Workflow state enumeration"""
    IDLE = "idle"
    WORK_STARTED = "work_started"
    PLAN_SUBMITTED = "plan_submitted"
    IN_PROGRESS = "in_progress"

class AgentHandoffServer:
    """Agent-Handoff MCP Server - Full Implementation"""
    
    def __init__(self):
        self.server = Server("agent-handoff")
        self.project_root = Path(os.getcwd())
        self.docs_dir = self.project_root / "docs"
        self.config_dir = self.project_root / ".agent-handoff"
        self.history_dir = self.config_dir / "history"
        
        # Workflow state management (in-memory)
        self.active_sessions: Dict[str, Dict] = {}
        self.current_session_id: Optional[str] = None
        
        # Register all tool handlers
        self._register_handlers()
        logger.info("Agent-Handoff MCP server initialized")
    
    def _ensure_docs_path(self, path: str) -> Path:
        """Ensure path is within docs directory, return safe path"""
        requested_path = Path(path)
        
        # Convert to absolute path relative to docs dir
        if requested_path.is_absolute():
            # Check if it's within docs directory
            try:
                docs_relative = requested_path.relative_to(self.docs_dir)
                full_path = self.docs_dir / docs_relative
            except ValueError:
                raise ValueError(f"Path {path} is outside docs directory")
        else:
            full_path = self.docs_dir / requested_path
        
        # Normalize and check for directory traversal
        normalized = full_path.resolve()
        if not str(normalized).startswith(str(self.docs_dir.resolve())):
            raise ValueError(f"Path {path} attempts to escape docs directory")
        
        return normalized
    
    def _create_error_response(self, code: str, message: str, suggestion: str = None) -> Dict:
        """Create standard error response"""
        error = {
            "error": {
                "code": code,
                "message": message
            }
        }
        if suggestion:
            error["error"]["suggestion"] = suggestion
        return error
    
    def _register_handlers(self):
        """Register all tool handlers"""
        
        @self.server.list_tools()
        async def list_tools() -> List[Tool]:
            """Return all available tools"""
            return [
                # Workflow tools
                Tool(
                    name="start_work",
                    description="Start a new work session and get initial context",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "user_goal": {
                                "type": "string",
                                "description": "The user's goal and requirements for this work session"
                            }
                        },
                        "required": ["user_goal"]
                    }
                ),
                Tool(
                    name="plan_setup",
                    description="Submit a development plan for the current session",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "plan": {
                                "type": "string",
                                "description": "Detailed development plan"
                            }
                        },
                        "required": ["plan"]
                    }
                ),
                Tool(
                    name="proceed",
                    description="Report progress and get next instructions",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "completed_work": {
                                "type": "string",
                                "description": "Description of completed work"
                            }
                        },
                        "required": ["completed_work"]
                    }
                ),
                Tool(
                    name="report_issue",
                    description="Report an issue or problem during development",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "issue_description": {
                                "type": "string",
                                "description": "Description of the issue encountered"
                            },
                            "attempted_solutions": {
                                "type": "string",
                                "description": "What solutions were already attempted"
                            }
                        },
                        "required": ["issue_description"]
                    }
                ),
                Tool(
                    name="end_job",
                    description="Complete the work session and provide handoff documentation",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "summary": {
                                "type": "string",
                                "description": "Summary of all work completed"
                            },
                            "agentreadme_content": {
                                "type": "string",
                                "description": "Updated agentreadme.md content for handoff"
                            }
                        },
                        "required": ["summary", "agentreadme_content"]
                    }
                ),
                
                # Utility tools
                Tool(
                    name="read_file",
                    description="Read a file from the docs directory",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "path": {
                                "type": "string",
                                "description": "Path to file relative to docs directory"
                            }
                        },
                        "required": ["path"]
                    }
                ),
                Tool(
                    name="write_file",
                    description="Write content to a file in the docs directory",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "path": {
                                "type": "string",
                                "description": "Path to file relative to docs directory"
                            },
                            "content": {
                                "type": "string",
                                "description": "Content to write to the file"
                            }
                        },
                        "required": ["path", "content"]
                    }
                ),
                Tool(
                    name="list_files",
                    description="List files and directories in the docs directory",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "path": {
                                "type": "string",
                                "description": "Path relative to docs directory (default: root)",
                                "default": ""
                            }
                        }
                    }
                ),
                Tool(
                    name="search_files",
                    description="Search for text within files in the docs directory",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Search query text"
                            },
                            "path": {
                                "type": "string",
                                "description": "Path to search in (default: entire docs directory)",
                                "default": ""
                            }
                        },
                        "required": ["query"]
                    }
                )
            ]
        
        @self.server.call_tool()
        async def call_tool(name: str, arguments: Any) -> List[TextContent]:
            """Handle tool calls"""
            try:
                # Workflow tools
                if name == "start_work":
                    return await self._handle_start_work(arguments)
                elif name == "plan_setup":
                    return await self._handle_plan_setup(arguments)
                elif name == "proceed":
                    return await self._handle_proceed(arguments)
                elif name == "report_issue":
                    return await self._handle_report_issue(arguments)
                elif name == "end_job":
                    return await self._handle_end_job(arguments)
                
                # Utility tools
                elif name == "read_file":
                    return await self._handle_read_file(arguments)
                elif name == "write_file":
                    return await self._handle_write_file(arguments)
                elif name == "list_files":
                    return await self._handle_list_files(arguments)
                elif name == "search_files":
                    return await self._handle_search_files(arguments)
                
                else:
                    error = self._create_error_response(
                        "UNKNOWN_TOOL",
                        f"Unknown tool: {name}"
                    )
                    return [TextContent(type="text", text=json.dumps(error, indent=2))]
                    
            except Exception as e:
                logger.error(f"Tool call error: {e}")
                error = self._create_error_response(
                    "EXECUTION_ERROR",
                    f"Error executing tool {name}: {str(e)}"
                )
                return [TextContent(type="text", text=json.dumps(error, indent=2))]
    
    async def _handle_start_work(self, arguments: Dict) -> List[TextContent]:
        """Handle start_work tool call"""
        user_goal = arguments.get("user_goal", "")
        
        # Create new session
        session_id = str(uuid.uuid4())
        self.current_session_id = session_id
        
        # Initialize session state
        self.active_sessions[session_id] = {
            "state": WorkflowState.WORK_STARTED,
            "user_goal": user_goal,
            "started_at": datetime.now().isoformat(),
            "plan": None,
            "progress": []
        }
        
        # Read current agentreadme.md if exists
        agentreadme_path = self.project_root / "agentreadme.md"
        agent_readme_content = ""
        if agentreadme_path.exists():
            agent_readme_content = agentreadme_path.read_text(encoding='utf-8')
        
        response = {
            "session_id": session_id,
            "status": "work_started",
            "user_goal": user_goal,
            "agent_readme_content": agent_readme_content,
            "instruction": "Next step: Call plan_setup tool with your development plan"
        }
        
        return [TextContent(type="text", text=json.dumps(response, indent=2, ensure_ascii=False))]
    
    async def _handle_plan_setup(self, arguments: Dict) -> List[TextContent]:
        """Handle plan_setup tool call"""
        if not self.current_session_id or self.current_session_id not in self.active_sessions:
            error = self._create_error_response(
                "WORKFLOW_VIOLATION",
                "No active work session. Call start_work first."
            )
            return [TextContent(type="text", text=json.dumps(error, indent=2))]
        
        session = self.active_sessions[self.current_session_id]
        if session["state"] != WorkflowState.WORK_STARTED:
            error = self._create_error_response(
                "WORKFLOW_VIOLATION",
                f"Invalid state for plan_setup. Current state: {session['state']}",
                "Call start_work first or check current workflow state"
            )
            return [TextContent(type="text", text=json.dumps(error, indent=2))]
        
        plan = arguments.get("plan", "")
        session["plan"] = plan
        session["state"] = WorkflowState.PLAN_SUBMITTED
        
        response = {
            "status": "plan_accepted",
            "session_id": self.current_session_id,
            "plan": plan,
            "instruction": "Plan recorded. Begin implementation and use proceed tool to report progress."
        }
        
        return [TextContent(type="text", text=json.dumps(response, indent=2, ensure_ascii=False))]
    
    async def _handle_proceed(self, arguments: Dict) -> List[TextContent]:
        """Handle proceed tool call"""
        if not self.current_session_id or self.current_session_id not in self.active_sessions:
            error = self._create_error_response(
                "WORKFLOW_VIOLATION",
                "No active work session. Call start_work first."
            )
            return [TextContent(type="text", text=json.dumps(error, indent=2))]
        
        session = self.active_sessions[self.current_session_id]
        if session["state"] not in [WorkflowState.PLAN_SUBMITTED, WorkflowState.IN_PROGRESS]:
            error = self._create_error_response(
                "WORKFLOW_VIOLATION",
                f"Invalid state for proceed. Current state: {session['state']}",
                "Submit a plan with plan_setup first"
            )
            return [TextContent(type="text", text=json.dumps(error, indent=2))]
        
        completed_work = arguments.get("completed_work", "")
        session["progress"].append({
            "timestamp": datetime.now().isoformat(),
            "work": completed_work
        })
        session["state"] = WorkflowState.IN_PROGRESS
        
        response = {
            "status": "progress_recorded",
            "session_id": self.current_session_id,
            "completed_work": completed_work,
            "instruction": "Continue implementation or call end_job when complete"
        }
        
        return [TextContent(type="text", text=json.dumps(response, indent=2, ensure_ascii=False))]
    
    async def _handle_report_issue(self, arguments: Dict) -> List[TextContent]:
        """Handle report_issue tool call"""
        if not self.current_session_id or self.current_session_id not in self.active_sessions:
            error = self._create_error_response(
                "WORKFLOW_VIOLATION",
                "No active work session. Call start_work first."
            )
            return [TextContent(type="text", text=json.dumps(error, indent=2))]
        
        issue_description = arguments.get("issue_description", "")
        attempted_solutions = arguments.get("attempted_solutions", "")
        
        session = self.active_sessions[self.current_session_id]
        if "issues" not in session:
            session["issues"] = []
        
        session["issues"].append({
            "timestamp": datetime.now().isoformat(),
            "description": issue_description,
            "attempted_solutions": attempted_solutions
        })
        
        response = {
            "status": "issue_recorded",
            "session_id": self.current_session_id,
            "issue_description": issue_description,
            "instruction": "Issue logged. Continue with debugging or call proceed when resolved."
        }
        
        return [TextContent(type="text", text=json.dumps(response, indent=2, ensure_ascii=False))]
    
    async def _handle_end_job(self, arguments: Dict) -> List[TextContent]:
        """Handle end_job tool call"""
        if not self.current_session_id or self.current_session_id not in self.active_sessions:
            error = self._create_error_response(
                "WORKFLOW_VIOLATION",
                "No active work session. Call start_work first."
            )
            return [TextContent(type="text", text=json.dumps(error, indent=2))]
        
        summary = arguments.get("summary", "")
        agentreadme_content = arguments.get("agentreadme_content", "")
        
        session = self.active_sessions[self.current_session_id]
        session["summary"] = summary
        session["completed_at"] = datetime.now().isoformat()
        
        # Create history entry (simple JSON format to avoid YAML dependency)
        self.history_dir.mkdir(parents=True, exist_ok=True)
        history_file = self.history_dir / f"session_{self.current_session_id}.json"
        
        with open(history_file, 'w', encoding='utf-8') as f:
            json.dump(session, f, indent=2, ensure_ascii=False)
        
        response = {
            "status": "job_completed",
            "session_id": self.current_session_id,
            "summary": summary,
            "history_saved": str(history_file),
            "instruction": f"Job completed successfully. Please write the updated agentreadme.md using write_file tool with path '../agentreadme.md' and the provided content."
        }
        
        # Clear current session
        self.current_session_id = None
        
        return [TextContent(type="text", text=json.dumps(response, indent=2, ensure_ascii=False))]
    
    async def _handle_read_file(self, arguments: Dict) -> List[TextContent]:
        """Handle read_file tool call"""
        try:
            path = arguments.get("path", "")
            
            # Special handling for agentreadme.md in project root
            if path == "../agentreadme.md" or path == "agentreadme.md":
                agentreadme_path = self.project_root / "agentreadme.md"
                if not agentreadme_path.exists():
                    error = self._create_error_response(
                        "FILE_NOT_FOUND",
                        f"File not found: {path}"
                    )
                    return [TextContent(type="text", text=json.dumps(error, indent=2))]
                
                content = agentreadme_path.read_text(encoding='utf-8')
                response = {
                    "path": path,
                    "content": content,
                    "size": len(content)
                }
                return [TextContent(type="text", text=json.dumps(response, indent=2, ensure_ascii=False))]
            
            file_path = self._ensure_docs_path(path)
            
            if not file_path.exists():
                error = self._create_error_response(
                    "FILE_NOT_FOUND",
                    f"File not found: {path}"
                )
                return [TextContent(type="text", text=json.dumps(error, indent=2))]
            
            if file_path.is_dir():
                error = self._create_error_response(
                    "INVALID_PATH",
                    f"Path is a directory, not a file: {path}",
                    "Use list_files to see directory contents"
                )
                return [TextContent(type="text", text=json.dumps(error, indent=2))]
            
            content = file_path.read_text(encoding='utf-8')
            
            response = {
                "path": path,
                "content": content,
                "size": len(content)
            }
            
            return [TextContent(type="text", text=json.dumps(response, indent=2, ensure_ascii=False))]
            
        except ValueError as e:
            error = self._create_error_response(
                "INVALID_PATH",
                str(e),
                "Use paths relative to docs directory only"
            )
            return [TextContent(type="text", text=json.dumps(error, indent=2))]
        except Exception as e:
            error = self._create_error_response(
                "EXECUTION_ERROR",
                f"Error reading file: {str(e)}"
            )
            return [TextContent(type="text", text=json.dumps(error, indent=2))]
    
    async def _handle_write_file(self, arguments: Dict) -> List[TextContent]:
        """Handle write_file tool call"""
        try:
            path = arguments.get("path", "")
            content = arguments.get("content", "")
            
            # Special handling for agentreadme.md in project root
            if path == "../agentreadme.md" or path == "agentreadme.md":
                agentreadme_path = self.project_root / "agentreadme.md"
                agentreadme_path.write_text(content, encoding='utf-8')
                
                response = {
                    "path": path,
                    "status": "written",
                    "size": len(content)
                }
                return [TextContent(type="text", text=json.dumps(response, indent=2, ensure_ascii=False))]
            
            file_path = self._ensure_docs_path(path)
            
            # Create parent directories if needed
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write file
            file_path.write_text(content, encoding='utf-8')
            
            response = {
                "path": path,
                "status": "written",
                "size": len(content)
            }
            
            return [TextContent(type="text", text=json.dumps(response, indent=2, ensure_ascii=False))]
            
        except ValueError as e:
            error = self._create_error_response(
                "INVALID_PATH",
                str(e),
                "Use paths relative to docs directory only"
            )
            return [TextContent(type="text", text=json.dumps(error, indent=2))]
        except Exception as e:
            error = self._create_error_response(
                "EXECUTION_ERROR",
                f"Error writing file: {str(e)}"
            )
            return [TextContent(type="text", text=json.dumps(error, indent=2))]
    
    async def _handle_list_files(self, arguments: Dict) -> List[TextContent]:
        """Handle list_files tool call"""
        try:
            path = arguments.get("path", "")
            dir_path = self._ensure_docs_path(path)
            
            if not dir_path.exists():
                error = self._create_error_response(
                    "FILE_NOT_FOUND",
                    f"Directory not found: {path}"
                )
                return [TextContent(type="text", text=json.dumps(error, indent=2))]
            
            if not dir_path.is_dir():
                error = self._create_error_response(
                    "INVALID_PATH",
                    f"Path is not a directory: {path}",
                    "Use read_file to read file contents"
                )
                return [TextContent(type="text", text=json.dumps(error, indent=2))]
            
            files = []
            directories = []
            
            for item in sorted(dir_path.iterdir()):
                relative_path = str(item.relative_to(self.docs_dir))
                if item.is_dir():
                    directories.append(relative_path)
                else:
                    files.append({
                        "path": relative_path,
                        "size": item.stat().st_size
                    })
            
            response = {
                "path": path,
                "directories": directories,
                "files": files
            }
            
            return [TextContent(type="text", text=json.dumps(response, indent=2, ensure_ascii=False))]
            
        except ValueError as e:
            error = self._create_error_response(
                "INVALID_PATH",
                str(e),
                "Use paths relative to docs directory only"
            )
            return [TextContent(type="text", text=json.dumps(error, indent=2))]
        except Exception as e:
            error = self._create_error_response(
                "EXECUTION_ERROR",
                f"Error listing files: {str(e)}"
            )
            return [TextContent(type="text", text=json.dumps(error, indent=2))]
    
    async def _handle_search_files(self, arguments: Dict) -> List[TextContent]:
        """Handle search_files tool call"""
        try:
            query = arguments.get("query", "")
            path = arguments.get("path", "")
            
            search_path = self._ensure_docs_path(path)
            
            if not search_path.exists():
                error = self._create_error_response(
                    "FILE_NOT_FOUND",
                    f"Search path not found: {path}"
                )
                return [TextContent(type="text", text=json.dumps(error, indent=2))]
            
            results = []
            
            def search_in_file(file_path: Path):
                try:
                    content = file_path.read_text(encoding='utf-8')
                    lines = content.splitlines()
                    
                    for line_num, line in enumerate(lines, 1):
                        if query.lower() in line.lower():
                            results.append({
                                "file": str(file_path.relative_to(self.docs_dir)),
                                "line": line_num,
                                "text": line.strip()
                            })
                except Exception as e:
                    logger.warning(f"Could not search in file {file_path}: {e}")
            
            if search_path.is_file():
                search_in_file(search_path)
            else:
                for file_path in search_path.rglob("*.md"):
                    search_in_file(file_path)
                for file_path in search_path.rglob("*.txt"):
                    search_in_file(file_path)
                for file_path in search_path.rglob("*.json"):
                    search_in_file(file_path)
            
            response = {
                "query": query,
                "search_path": path,
                "results": results,
                "total_matches": len(results)
            }
            
            return [TextContent(type="text", text=json.dumps(response, indent=2, ensure_ascii=False))]
            
        except ValueError as e:
            error = self._create_error_response(
                "INVALID_PATH",
                str(e),
                "Use paths relative to docs directory only"
            )
            return [TextContent(type="text", text=json.dumps(error, indent=2))]
        except Exception as e:
            error = self._create_error_response(
                "EXECUTION_ERROR",
                f"Error searching files: {str(e)}"
            )
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