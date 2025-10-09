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
                description="🚨 MANDATORY FIRST STEP 🚨 Start a new work session. You MUST call this tool FIRST before doing ANY development work, regardless of task complexity. This is NOT just for agent-handoff development - it applies to ALL complex features in ANY project. Why? Because this tool retrieves critical project context including development guidelines, architecture decisions, and project goals. Without reading these, you WILL write bad code that violates project standards. This initializes the workflow tracking system. Calling this is NOT optional - it is REQUIRED.",
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
                description="📋 REQUIRED STEP 2: Submit your development plan as a structured list of steps. Must be called after start_work and before proceeding with implementation. Format: Provide numbered steps (Step 1: xxx, Step 2: xxx, etc.). These steps will be tracked and you'll be reminded of progress.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "plan_steps": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of development steps in order (e.g., ['Confirm environment', 'Read relevant docs', 'Implement feature X', 'Test and debug', 'Clean up files'])"
                        }
                    },
                    "required": ["plan_steps"]
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
                description="🏁 FINAL STEP: Complete the work session. STRICT REQUIREMENTS: (1) Can only be called AFTER you have called 'proceed' at least once with completed work. (2) You MUST provide the complete agentreadme.md file content - do NOT write it yourself, you must READ the existing agentreadme.md file first, then provide the updated version here. If you don't have the file content, this call will be REJECTED.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "summary": {
                            "type": "string",
                            "description": "Summary of all work completed"
                        },
                        "agentreadme_content": {
                            "type": "string",
                            "description": "REQUIRED: The COMPLETE updated agentreadme.md file content. You must READ the existing file first, update it, and provide the full content here. Do NOT skip this or write it from scratch."
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
            "next_step": "plan_setup",
            "recommended_plan_steps": [
                "Step 1: Confirm environment and check dependencies",
                "Step 2: Read relevant docs/ files and understand project structure",
                "Step 3: Break down development task into sub-tasks",
                "Step 4: Implement feature/fix with testing",
                "Step 5: Debug and confirm functionality",
                "Step 6: If bugs found, call report_issue tool",
                "Step 7: Clean up temporary/garbage files",
                "Step 8: Use agent-handoff tools to organize documentation",
                "Step 9: Update agentreadme.md with changes"
            ],
            "instruction": "✅ Work session started successfully! You are now in a TRACKED workflow.\n\n🚨 MANDATORY NEXT STEP: You MUST now call 'plan_setup' tool with a list of development steps.\n\n💡 RECOMMENDED PLAN TEMPLATE:\n  1. Confirm environment\n  2. Read relevant docs and files\n  3. Break down development steps\n  4. Implement and test\n  5. Debug (call report_issue if needed)\n  6. Clean up garbage files\n  7. Organize documentation\n  8. Update agentreadme.md\n\n⚠️ WORKFLOW ENFORCEMENT: All your work in this session is being tracked. You cannot skip steps. The workflow is: start_work → plan_setup → proceed (at least once) → end_job.\n\nDo NOT proceed with code changes until you have called plan_setup!"
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
        
        plan_steps = arguments.get("plan_steps", [])
        
        # Validate that steps are provided as a list
        if not isinstance(plan_steps, list) or len(plan_steps) == 0:
            error = self._create_error_response(
                "INVALID_INPUT",
                "plan_steps must be a non-empty list of strings",
                "Provide your plan as a list: ['Step 1: ...', 'Step 2: ...', ...]"
            )
            return [TextContent(type="text", text=json.dumps(error, indent=2))]
        
        session["plan_steps"] = plan_steps
        session["completed_steps"] = []
        session["current_step_index"] = 0
        session["state"] = WorkflowState.PLAN_SUBMITTED
        
        response = {
            "status": "plan_accepted",
            "session_id": self.current_session_id,
            "total_steps": len(plan_steps),
            "plan_steps": plan_steps,
            "current_step": f"Step 1/{len(plan_steps)}: {plan_steps[0]}" if plan_steps else None,
            "instruction": f"✅ Plan recorded with {len(plan_steps)} steps.\n\n📋 Current objective: {plan_steps[0] if plan_steps else 'N/A'}\n\nBegin implementation and use 'proceed' tool to report progress on each step."
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
        
        # Track step completion
        plan_steps = session.get("plan_steps", [])
        completed_steps = session.get("completed_steps", [])
        current_step_index = session.get("current_step_index", 0)
        
        # Mark current step as completed and move to next
        if plan_steps and current_step_index < len(plan_steps):
            completed_steps.append(plan_steps[current_step_index])
            current_step_index += 1
            session["completed_steps"] = completed_steps
            session["current_step_index"] = current_step_index
        
        # Build progress message
        progress_msg = f"✅ Progress recorded ({len(completed_steps)}/{len(plan_steps)} steps completed)\n\n"
        
        if completed_steps:
            progress_msg += f"📝 Just completed: {completed_steps[-1]}\n\n"
        
        if current_step_index < len(plan_steps):
            next_step = plan_steps[current_step_index]
            progress_msg += f"🎯 Next objective: {next_step}\n\n"
            progress_msg += "Continue implementation or call end_job when all steps are complete."
        else:
            progress_msg += "🎉 All planned steps completed! You can now call end_job to finish.\n\n"
            progress_msg += "⚠️ REMINDER: You must provide the complete agentreadme.md content when calling end_job."
        
        response = {
            "status": "progress_recorded",
            "session_id": self.current_session_id,
            "completed_work": completed_work,
            "steps_completed": len(completed_steps),
            "total_steps": len(plan_steps),
            "completed_steps": completed_steps,
            "next_step": plan_steps[current_step_index] if current_step_index < len(plan_steps) else None,
            "instruction": progress_msg
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
        
        # STRICT CHECK 1: Must have completed at least one proceed before ending
        if session["state"] not in [WorkflowState.IN_PROGRESS]:
            error = self._create_error_response(
                "WORKFLOW_VIOLATION",
                f"Cannot end job without completing work. Current state: {session['state']}",
                "You must call 'proceed' at least once to report completed work before calling 'end_job'. The work is not done yet!"
            )
            return [TextContent(type="text", text=json.dumps(error, indent=2))]
        
        # STRICT CHECK 2: Must have at least one progress entry
        if not session.get("progress") or len(session["progress"]) == 0:
            error = self._create_error_response(
                "WORKFLOW_VIOLATION",
                "Cannot end job without any completed work reported.",
                "Call 'proceed' to report your completed work before ending the job. You haven't done anything yet!"
            )
            return [TextContent(type="text", text=json.dumps(error, indent=2))]
        
        # STRICT CHECK 3: All planned steps must be completed
        plan_steps = session.get("plan_steps", [])
        completed_steps = session.get("completed_steps", [])
        if plan_steps and len(completed_steps) < len(plan_steps):
            error = self._create_error_response(
                "WORKFLOW_VIOLATION",
                f"Cannot end job with incomplete plan. Completed {len(completed_steps)}/{len(plan_steps)} steps.",
                f"You still have {len(plan_steps) - len(completed_steps)} steps remaining. Complete them with 'proceed' or update your plan if needed."
            )
            return [TextContent(type="text", text=json.dumps(error, indent=2))]
        
        summary = arguments.get("summary", "")
        agentreadme_content = arguments.get("agentreadme_content", "")
        
        # STRICT CHECK 4: agentreadme_content must be provided and substantial
        if not agentreadme_content or len(agentreadme_content.strip()) < 50:
            error = self._create_error_response(
                "MISSING_AGENTREADME",
                "You must provide the complete agentreadme.md file content.",
                "REQUIRED: Read the existing agentreadme.md file using read_file tool, update it with your changes, and provide the COMPLETE updated content in the agentreadme_content parameter. This is NOT optional!"
            )
            return [TextContent(type="text", text=json.dumps(error, indent=2))]
        
        session["summary"] = summary
        session["agentreadme_content"] = agentreadme_content
        session["completed_at"] = datetime.now().isoformat()
        
        # Save agentreadme.md to project root
        agentreadme_path = self.project_root / "agentreadme.md"
        agentreadme_path.write_text(agentreadme_content, encoding='utf-8')
        
        # Create history entry (simple JSON format to avoid YAML dependency)
        self.history_dir.mkdir(parents=True, exist_ok=True)
        history_file = self.history_dir / f"session_{self.current_session_id}.json"
        
        with open(history_file, 'w', encoding='utf-8') as f:
            json.dump(session, f, indent=2, ensure_ascii=False)
        
        response = {
            "status": "job_completed",
            "session_id": self.current_session_id,
            "summary": summary,
            "steps_completed": len(completed_steps),
            "total_steps": len(plan_steps),
            "agentreadme_updated": str(agentreadme_path),
            "history_saved": str(history_file),
            "instruction": f"✅ Job completed successfully!\n\n📊 Completed {len(completed_steps)}/{len(plan_steps)} planned steps\n📝 Updated agentreadme.md saved to {agentreadme_path}\n💾 Session history saved to {history_file}\n\nThank you for following the workflow!"
        }
        
        # Clear current session
        self.current_session_id = None
        
        return [TextContent(type="text", text=json.dumps(response, indent=2, ensure_ascii=False))]