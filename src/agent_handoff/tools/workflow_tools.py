#!/usr/bin/env python3
"""
Workflow Tools Handler
Manages workflow-specific tools: start_work, plan_setup, proceed, report_issue, end_job
"""

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from mcp.types import Tool, TextContent

class WorkflowState:
    """Workflow state enumeration"""
    IDLE = "idle"
    WORK_STARTED = "work_started"
    PLAN_SUBMITTED = "plan_submitted"
    IN_PROGRESS = "in_progress"

class WorkflowToolsHandler:
    """Handler for workflow-related MCP tools"""
    
    def __init__(self, project_root: Path, config_dir: Path):
        self.project_root = project_root
        self.config_dir = config_dir
        self.history_dir = config_dir / "history"
        
        # Workflow state management (in-memory)
        self.active_sessions: Dict[str, Dict] = {}
        self.current_session_id: str = None
    
    def get_workflow_tools(self) -> List[Tool]:
        """Return workflow tool definitions"""
        return [
            Tool(
                name="start_work",
                description="🚨 MANDATORY FIRST STEP 🚨 Start a new work session. You MUST call this tool FIRST before doing ANY development work. This initializes the workflow tracking system and retrieves project context. Calling this is NOT optional - it is REQUIRED.",
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
                description="📋 REQUIRED STEP 2: Submit your development plan. Must be called after start_work and before proceeding with implementation.",
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
                description="✅ STEP 3: Report your completed work progress. You MUST call this at least once with actual work completed before you can end the job. This is not optional.",
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
                description="🐛 OPTIONAL: Report an issue or problem during development",
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
                description="🏁 FINAL STEP: Complete the work session. Can only be called AFTER you have called 'proceed' at least once with completed work. The workflow enforces this strictly.",
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
            )
        ]
    
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
    
    async def handle_start_work(self, arguments: Dict) -> List[TextContent]:
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
            "instruction": "✅ Work session started successfully! You are now in a TRACKED workflow.\n\n🚨 MANDATORY NEXT STEP: You MUST now call 'plan_setup' tool to submit your development plan.\n\n⚠️ WORKFLOW ENFORCEMENT: All your work in this session is being tracked. You cannot skip steps. The workflow is: start_work → plan_setup → proceed (at least once) → end_job.\n\nDo NOT proceed with code changes until you have called plan_setup!"
        }
        
        return [TextContent(type="text", text=json.dumps(response, indent=2, ensure_ascii=False))]
    
    async def handle_plan_setup(self, arguments: Dict) -> List[TextContent]:
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
    
    async def handle_proceed(self, arguments: Dict) -> List[TextContent]:
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
    
    async def handle_report_issue(self, arguments: Dict) -> List[TextContent]:
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
    
    async def handle_end_job(self, arguments: Dict) -> List[TextContent]:
        """Handle end_job tool call"""
        if not self.current_session_id or self.current_session_id not in self.active_sessions:
            error = self._create_error_response(
                "WORKFLOW_VIOLATION",
                "No active work session. Call start_work first."
            )
            return [TextContent(type="text", text=json.dumps(error, indent=2))]
        
        session = self.active_sessions[self.current_session_id]
        
        # STRICT CHECK: Must have completed at least one proceed before ending
        if session["state"] not in [WorkflowState.IN_PROGRESS]:
            error = self._create_error_response(
                "WORKFLOW_VIOLATION",
                f"Cannot end job without completing work. Current state: {session['state']}",
                "You must call 'proceed' at least once to report completed work before calling 'end_job'. The work is not done yet!"
            )
            return [TextContent(type="text", text=json.dumps(error, indent=2))]
        
        # Additional check: Must have at least one progress entry
        if not session.get("progress") or len(session["progress"]) == 0:
            error = self._create_error_response(
                "WORKFLOW_VIOLATION",
                "Cannot end job without any completed work reported.",
                "Call 'proceed' to report your completed work before ending the job. You haven't done anything yet!"
            )
            return [TextContent(type="text", text=json.dumps(error, indent=2))]
        
        summary = arguments.get("summary", "")
        agentreadme_content = arguments.get("agentreadme_content", "")
        
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