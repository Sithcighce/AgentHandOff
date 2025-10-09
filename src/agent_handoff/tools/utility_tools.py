#!/usr/bin/env python3
"""
Utility Tools Handler
Manages utility tools: read_file, write_file, list_files, search_files
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List

from mcp.types import Tool, TextContent

logger = logging.getLogger("agent-handoff")

class UtilityToolsHandler:
    """Handler for utility MCP tools"""
    
    def __init__(self, project_root: Path, docs_dir: Path):
        self.project_root = project_root
        self.docs_dir = docs_dir
    
    def get_utility_tools(self) -> List[Tool]:
        """Return utility tool definitions"""
        return [
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
            ),
            Tool(
                name="append_file",
                description="Append content to an existing file in the docs directory",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "Path to file relative to docs directory"
                        },
                        "content": {
                            "type": "string",
                            "description": "Content to append to the file"
                        }
                    },
                    "required": ["path", "content"]
                }
            )
        ]
    
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
    
    async def handle_read_file(self, arguments: Dict) -> List[TextContent]:
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
    
    async def handle_write_file(self, arguments: Dict) -> List[TextContent]:
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
            
            # Check file extension - docs should primarily contain documentation files
            file_extension = file_path.suffix.lower()
            non_doc_extensions = ['.py', '.js', '.ts', '.java', '.cpp', '.c', '.h', '.go', '.rs', '.exe', '.bin', '.so', '.dll']
            
            warnings = []
            if file_extension in non_doc_extensions:
                warnings.append(f"⚠️ WARNING: You are writing a {file_extension} file to the docs/ directory. The docs/ folder is meant for DOCUMENTATION files (.md, .txt, etc.), not code or executables. Consider if this file should be elsewhere in the project structure.")
            
            # Create parent directories if needed
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write file
            file_path.write_text(content, encoding='utf-8')
            
            # Get file statistics for health check
            line_count = len(content.splitlines())
            
            response = {
                "path": path,
                "status": "written",
                "size": len(content),
                "lines": line_count
            }
            
            # Add health warnings if needed
            if line_count > 300:
                warnings.append(f"⚠️ File is too long ({line_count} lines). Consider splitting into multiple files (recommended <300 lines).")
            
            if warnings:
                response["warnings"] = warnings
            
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
    
    async def handle_list_files(self, arguments: Dict) -> List[TextContent]:
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
                "files": files,
                "file_count": len(files),
                "directory_count": len(directories)
            }
            
            # Add health warnings if needed
            warnings = []
            if len(files) > 8:
                warnings.append(f"⚠️ Directory has too many files ({len(files)} files). Consider splitting into subdirectories (recommended ≤8 files per directory).")
            
            if warnings:
                response["warnings"] = warnings
            
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
    
    async def handle_search_files(self, arguments: Dict) -> List[TextContent]:
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
    
    async def handle_append_file(self, arguments: Dict) -> List[TextContent]:
        """Handle append_file tool call"""
        try:
            path = arguments.get("path", "")
            content = arguments.get("content", "")
            
            # Special handling for agentreadme.md in project root
            if path == "../agentreadme.md" or path == "agentreadme.md":
                agentreadme_path = self.project_root / "agentreadme.md"
                
                if agentreadme_path.exists():
                    existing = agentreadme_path.read_text(encoding='utf-8')
                    agentreadme_path.write_text(existing + "\n" + content, encoding='utf-8')
                else:
                    agentreadme_path.write_text(content, encoding='utf-8')
                
                response = {
                    "path": path,
                    "status": "appended",
                    "appended_size": len(content)
                }
                return [TextContent(type="text", text=json.dumps(response, indent=2, ensure_ascii=False))]
            
            file_path = self._ensure_docs_path(path)
            
            # Check file extension - docs should primarily contain documentation files
            file_extension = file_path.suffix.lower()
            non_doc_extensions = ['.py', '.js', '.ts', '.java', '.cpp', '.c', '.h', '.go', '.rs', '.exe', '.bin', '.so', '.dll']
            
            warnings = []
            if file_extension in non_doc_extensions:
                warnings.append(f"⚠️ WARNING: You are appending to a {file_extension} file in the docs/ directory. The docs/ folder is meant for DOCUMENTATION files (.md, .txt, etc.), not code or executables. Consider if this file should be elsewhere in the project structure.")
            
            # Check if file exists
            if not file_path.exists():
                error = self._create_error_response(
                    "FILE_NOT_FOUND",
                    f"Cannot append to non-existent file: {path}",
                    "Use write_file to create a new file"
                )
                return [TextContent(type="text", text=json.dumps(error, indent=2))]
            
            # Read existing content and append
            existing_content = file_path.read_text(encoding='utf-8')
            file_path.write_text(existing_content + "\n" + content, encoding='utf-8')
            
            # Check file health after append
            final_size = file_path.stat().st_size
            line_count = len(file_path.read_text(encoding='utf-8').splitlines())
            
            response = {
                "path": path,
                "status": "appended",
                "appended_size": len(content),
                "total_size": final_size,
                "total_lines": line_count
            }
            
            # Add health warnings if needed
            if line_count > 300:
                warnings.append(f"⚠️ File is too long ({line_count} lines). Consider splitting into multiple files (recommended <300 lines).")
            
            if warnings:
                response["warnings"] = warnings
            
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
                f"Error appending to file: {str(e)}"
            )
            return [TextContent(type="text", text=json.dumps(error, indent=2))]