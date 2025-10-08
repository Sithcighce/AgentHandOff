#!/usr/bin/env python3
"""
Agent-Handoff MCP Server Full Functionality Test
Tests all workflow and utility tools according to design specifications
"""

import asyncio
import json
import tempfile
from pathlib import Path

from agent_handoff.server import AgentHandoffServer

class MCPServerTester:
    """Test suite for Agent-Handoff MCP Server"""
    
    def __init__(self):
        self.server = None
        self.test_results = []
    
    def log_result(self, test_name: str, success: bool, message: str = ""):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        self.test_results.append({
            "test": test_name,
            "success": success,
            "message": message
        })
        print(f"{status}: {test_name} - {message}")
    
    async def setup(self):
        """Setup test environment"""
        print("🚀 Setting up Agent-Handoff MCP Server test environment...")
        try:
            self.server = AgentHandoffServer()
            self.log_result("Server Initialization", True, "Server created successfully")
            
            # Create test docs structure
            docs_dir = Path("docs")
            docs_dir.mkdir(exist_ok=True)
            
            test_files = {
                "docs/test_file.md": "# Test File\nThis is a test file for MCP server testing.",
                "docs/subdirectory/nested_file.md": "# Nested File\nThis file tests nested directory operations.",
                "docs/search_test.md": "This file contains searchable content for testing search functionality."
            }
            
            for file_path, content in test_files.items():
                file_obj = Path(file_path)
                file_obj.parent.mkdir(parents=True, exist_ok=True)
                file_obj.write_text(content, encoding='utf-8')
            
            self.log_result("Test Environment Setup", True, "Created test files and directories")
            return True
            
        except Exception as e:
            self.log_result("Server Initialization", False, f"Error: {str(e)}")
            return False
    
    async def test_workflow_tools(self):
        """Test workflow tools in correct sequence"""
        print("\n📋 Testing Workflow Tools...")
        
        # Test 1: start_work
        try:
            result = await self.server._handle_start_work({
                "user_goal": "Test the complete Agent-Handoff workflow"
            })
            
            response_text = result[0].text
            response_data = json.loads(response_text)
            
            if "session_id" in response_data and response_data.get("status") == "work_started":
                session_id = response_data["session_id"]
                self.log_result("start_work", True, f"Session created: {session_id[:8]}...")
            else:
                self.log_result("start_work", False, "Invalid response format")
                return False
                
        except Exception as e:
            self.log_result("start_work", False, f"Error: {str(e)}")
            return False
        
        # Test 2: plan_setup
        try:
            result = await self.server._handle_plan_setup({
                "plan": "1. Test all MCP tools\n2. Verify workflow state management\n3. Complete testing session"
            })
            
            response_text = result[0].text
            response_data = json.loads(response_text)
            
            if response_data.get("status") == "plan_accepted":
                self.log_result("plan_setup", True, "Plan submitted successfully")
            else:
                self.log_result("plan_setup", False, "Plan submission failed")
                return False
                
        except Exception as e:
            self.log_result("plan_setup", False, f"Error: {str(e)}")
            return False
        
        # Test 3: proceed
        try:
            result = await self.server._handle_proceed({
                "completed_work": "Successfully tested start_work and plan_setup tools"
            })
            
            response_text = result[0].text
            response_data = json.loads(response_text)
            
            if response_data.get("status") == "progress_recorded":
                self.log_result("proceed", True, "Progress recorded successfully")
            else:
                self.log_result("proceed", False, "Progress recording failed")
                
        except Exception as e:
            self.log_result("proceed", False, f"Error: {str(e)}")
        
        # Test 4: report_issue
        try:
            result = await self.server._handle_report_issue({
                "issue_description": "Test issue reporting functionality",
                "attempted_solutions": "This is a test, no real issue exists"
            })
            
            response_text = result[0].text
            response_data = json.loads(response_text)
            
            if response_data.get("status") == "issue_recorded":
                self.log_result("report_issue", True, "Issue recorded successfully")
            else:
                self.log_result("report_issue", False, "Issue recording failed")
                
        except Exception as e:
            self.log_result("report_issue", False, f"Error: {str(e)}")
        
        # Test 5: end_job
        try:
            result = await self.server._handle_end_job({
                "summary": "Completed comprehensive testing of Agent-Handoff MCP server",
                "agentreadme_content": "# Agent Handoff Test\n\nAll tests completed successfully."
            })
            
            response_text = result[0].text
            response_data = json.loads(response_text)
            
            if response_data.get("status") == "job_completed":
                self.log_result("end_job", True, "Job completed successfully")
            else:
                self.log_result("end_job", False, "Job completion failed")
                
        except Exception as e:
            self.log_result("end_job", False, f"Error: {str(e)}")
        
        return True
    
    async def test_utility_tools(self):
        """Test utility tools"""
        print("\n📁 Testing Utility Tools...")
        
        # Test 1: read_file
        try:
            result = await self.server._handle_read_file({
                "path": "test_file.md"
            })
            
            response_text = result[0].text
            response_data = json.loads(response_text)
            
            if "content" in response_data and "# Test File" in response_data["content"]:
                self.log_result("read_file", True, "File read successfully")
            else:
                self.log_result("read_file", False, "File content not found")
                
        except Exception as e:
            self.log_result("read_file", False, f"Error: {str(e)}")
        
        # Test 2: write_file
        try:
            test_content = "# New Test File\n\nThis file was created by the MCP server test."
            
            result = await self.server._handle_write_file({
                "path": "new_test_file.md",
                "content": test_content
            })
            
            response_text = result[0].text
            response_data = json.loads(response_text)
            
            if response_data.get("status") == "written":
                # Verify file was actually written
                test_file = Path("docs/new_test_file.md")
                if test_file.exists() and test_content in test_file.read_text():
                    self.log_result("write_file", True, "File written and verified")
                else:
                    self.log_result("write_file", False, "File not found after writing")
            else:
                self.log_result("write_file", False, "Write operation failed")
                
        except Exception as e:
            self.log_result("write_file", False, f"Error: {str(e)}")
        
        # Test 3: list_files
        try:
            result = await self.server._handle_list_files({
                "path": ""
            })
            
            response_text = result[0].text
            response_data = json.loads(response_text)
            
            if "files" in response_data and "directories" in response_data:
                file_count = len(response_data["files"])
                dir_count = len(response_data["directories"])
                self.log_result("list_files", True, f"Listed {file_count} files, {dir_count} directories")
            else:
                self.log_result("list_files", False, "Invalid response format")
                
        except Exception as e:
            self.log_result("list_files", False, f"Error: {str(e)}")
        
        # Test 4: search_files
        try:
            result = await self.server._handle_search_files({
                "query": "searchable",
                "path": ""
            })
            
            response_text = result[0].text
            response_data = json.loads(response_text)
            
            if "results" in response_data and response_data.get("total_matches", 0) > 0:
                match_count = response_data["total_matches"]
                self.log_result("search_files", True, f"Found {match_count} matches for 'searchable'")
            else:
                self.log_result("search_files", False, "No search results found")
                
        except Exception as e:
            self.log_result("search_files", False, f"Error: {str(e)}")
        
        return True
    
    async def test_error_handling(self):
        """Test error handling and security"""
        print("\n🛡️ Testing Error Handling & Security...")
        
        # Test 1: Invalid workflow state
        try:
            # Reset server state
            self.server.current_session_id = None
            self.server.active_sessions = {}
            
            result = await self.server._handle_plan_setup({
                "plan": "This should fail - no active session"
            })
            
            response_text = result[0].text
            response_data = json.loads(response_text)
            
            if "error" in response_data and response_data["error"]["code"] == "WORKFLOW_VIOLATION":
                self.log_result("Workflow Violation Detection", True, "Correctly rejected invalid workflow state")
            else:
                self.log_result("Workflow Violation Detection", False, "Did not detect workflow violation")
                
        except Exception as e:
            self.log_result("Workflow Violation Detection", False, f"Error: {str(e)}")
        
        # Test 2: Path traversal protection
        try:
            result = await self.server._handle_read_file({
                "path": "../../../etc/passwd"
            })
            
            response_text = result[0].text
            response_data = json.loads(response_text)
            
            if "error" in response_data and response_data["error"]["code"] == "INVALID_PATH":
                self.log_result("Path Traversal Protection", True, "Successfully blocked path traversal attempt")
            else:
                self.log_result("Path Traversal Protection", False, "Path traversal not blocked")
                
        except Exception as e:
            self.log_result("Path Traversal Protection", True, f"Exception caught: {str(e)}")
        
        # Test 3: Non-existent file handling
        try:
            result = await self.server._handle_read_file({
                "path": "non_existent_file.md"
            })
            
            response_text = result[0].text
            response_data = json.loads(response_text)
            
            if "error" in response_data and response_data["error"]["code"] == "FILE_NOT_FOUND":
                self.log_result("File Not Found Handling", True, "Correctly handled non-existent file")
            else:
                self.log_result("File Not Found Handling", False, "Did not handle non-existent file correctly")
                
        except Exception as e:
            self.log_result("File Not Found Handling", False, f"Error: {str(e)}")
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*50)
        print("📊 TEST SUMMARY")
        print("="*50)
        
        passed = sum(1 for r in self.test_results if r["success"])
        total = len(self.test_results)
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        if total - passed > 0:
            print("\n❌ Failed Tests:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  - {result['test']}: {result['message']}")
        
        print("\n" + ("🎉 ALL TESTS PASSED!" if passed == total else "⚠️  SOME TESTS FAILED"))
        return passed == total

async def main():
    """Run comprehensive MCP server tests"""
    print("🧪 Agent-Handoff MCP Server Comprehensive Test Suite")
    print("="*60)
    
    tester = MCPServerTester()
    
    # Setup
    if not await tester.setup():
        print("❌ Setup failed, aborting tests")
        return False
    
    # Run all tests
    await tester.test_workflow_tools()
    await tester.test_utility_tools() 
    await tester.test_error_handling()
    
    # Print summary
    success = tester.print_summary()
    
    # Cleanup
    print("\n🧹 Cleaning up test files...")
    try:
        import shutil
        if Path("docs").exists():
            shutil.rmtree("docs")
        if Path(".agent-handoff").exists():
            shutil.rmtree(".agent-handoff")
        print("✅ Cleanup completed")
    except Exception as e:
        print(f"⚠️ Cleanup warning: {e}")
    
    return success

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)