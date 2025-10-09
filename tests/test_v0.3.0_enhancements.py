#!/usr/bin/env python3
"""
Test script for v0.3.0 enhancements
Tests:
1. end_job requires agentreadme content
2. plan_setup requires list of steps
3. proceed tracks step progress
4. start_work description emphasizes universal requirement
5. write_file warns about non-doc files in docs/
"""

import asyncio
import json
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from agent_handoff.tools.workflow_tools import WorkflowToolsHandler
from agent_handoff.tools.utility_tools import UtilityToolsHandler


async def test_enhancement_1_agentreadme_required():
    """Test that end_job requires agentreadme content"""
    print("\n" + "="*70)
    print("TEST 1: end_job requires agentreadme content")
    print("="*70)
    
    project_root = Path.cwd()
    config_dir = project_root / ".agent_handoff"
    
    handler = WorkflowToolsHandler(project_root, config_dir)
    
    # Start work
    result = await handler.handle_start_work({"user_goal": "Test enhancement 1"})
    print("✓ Started work session")
    
    # Submit plan with steps
    result = await handler.handle_plan_setup({
        "plan_steps": ["Step 1: Test", "Step 2: Verify"]
    })
    print("✓ Submitted plan with steps")
    
    # Complete work
    result = await handler.handle_proceed({"completed_work": "Step 1 done"})
    result = await handler.handle_proceed({"completed_work": "Step 2 done"})
    print("✓ Completed all steps")
    
    # Try to end without agentreadme - should FAIL
    print("\n→ Testing end_job WITHOUT agentreadme content...")
    result = await handler.handle_end_job({
        "summary": "Work complete",
        "agentreadme_content": ""
    })
    
    response = json.loads(result[0].text)
    if "error" in response and "MISSING_AGENTREADME" in response["error"]["code"]:
        print("✅ PASS: Correctly rejected end_job without agentreadme content")
        print(f"   Error message: {response['error']['message']}")
    else:
        print("❌ FAIL: Should have rejected end_job without agentreadme")
        return False
    
    # Try again with agentreadme - should SUCCEED
    print("\n→ Testing end_job WITH agentreadme content...")
    result = await handler.handle_end_job({
        "summary": "Work complete",
        "agentreadme_content": "# Agent Readme\n\nThis is a complete agentreadme file with sufficient content to pass validation."
    })
    
    response = json.loads(result[0].text)
    if "status" in response and response["status"] == "job_completed":
        print("✅ PASS: Correctly accepted end_job with agentreadme content")
        print(f"   Agentreadme saved to: {response.get('agentreadme_updated', 'N/A')}")
    else:
        print("❌ FAIL: Should have accepted end_job with agentreadme")
        return False
    
    return True


async def test_enhancement_2_plan_steps_list():
    """Test that plan_setup requires list of steps"""
    print("\n" + "="*70)
    print("TEST 2: plan_setup requires list of steps")
    print("="*70)
    
    project_root = Path.cwd()
    config_dir = project_root / ".agent_handoff"
    
    handler = WorkflowToolsHandler(project_root, config_dir)
    
    # Start work
    result = await handler.handle_start_work({"user_goal": "Test enhancement 2"})
    print("✓ Started work session")
    
    # Try to submit plan as string - should FAIL
    print("\n→ Testing plan_setup with string (wrong format)...")
    result = await handler.handle_plan_setup({
        "plan_steps": "This is a string, not a list"
    })
    
    response = json.loads(result[0].text)
    if "error" in response:
        print("✅ PASS: Correctly rejected plan as string")
        print(f"   Error message: {response['error']['message']}")
    else:
        print("❌ FAIL: Should have rejected plan as string")
        return False
    
    # Submit proper list - should SUCCEED
    print("\n→ Testing plan_setup with list of steps...")
    result = await handler.handle_plan_setup({
        "plan_steps": [
            "Step 1: Confirm environment",
            "Step 2: Read docs",
            "Step 3: Implement feature",
            "Step 4: Test and debug",
            "Step 5: Clean up"
        ]
    })
    
    response = json.loads(result[0].text)
    if "status" in response and response["status"] == "plan_accepted":
        print("✅ PASS: Correctly accepted plan as list")
        print(f"   Total steps: {response.get('total_steps', 0)}")
        print(f"   Current step: {response.get('current_step', 'N/A')}")
    else:
        print("❌ FAIL: Should have accepted plan as list")
        return False
    
    return True


async def test_enhancement_3_step_tracking():
    """Test that proceed tracks step progress"""
    print("\n" + "="*70)
    print("TEST 3: proceed tracks step progress")
    print("="*70)
    
    project_root = Path.cwd()
    config_dir = project_root / ".agent_handoff"
    
    handler = WorkflowToolsHandler(project_root, config_dir)
    
    # Start work
    result = await handler.handle_start_work({"user_goal": "Test enhancement 3"})
    print("✓ Started work session")
    
    # Submit plan with 3 steps
    steps = ["Step 1: First task", "Step 2: Second task", "Step 3: Third task"]
    result = await handler.handle_plan_setup({"plan_steps": steps})
    print(f"✓ Submitted plan with {len(steps)} steps")
    
    # Complete first step
    print("\n→ Completing step 1...")
    result = await handler.handle_proceed({"completed_work": "Finished first task"})
    response = json.loads(result[0].text)
    
    if response.get("steps_completed") == 1 and response.get("next_step") == steps[1]:
        print("✅ PASS: Step 1 tracked correctly")
        print(f"   Progress: {response['steps_completed']}/{response['total_steps']}")
        print(f"   Next step: {response['next_step']}")
    else:
        print("❌ FAIL: Step 1 not tracked correctly")
        return False
    
    # Complete second step
    print("\n→ Completing step 2...")
    result = await handler.handle_proceed({"completed_work": "Finished second task"})
    response = json.loads(result[0].text)
    
    if response.get("steps_completed") == 2 and response.get("next_step") == steps[2]:
        print("✅ PASS: Step 2 tracked correctly")
        print(f"   Progress: {response['steps_completed']}/{response['total_steps']}")
    else:
        print("❌ FAIL: Step 2 not tracked correctly")
        return False
    
    # Complete third step
    print("\n→ Completing step 3...")
    result = await handler.handle_proceed({"completed_work": "Finished third task"})
    response = json.loads(result[0].text)
    
    if response.get("steps_completed") == 3 and response.get("next_step") is None:
        print("✅ PASS: Step 3 tracked correctly (all done)")
        print(f"   Progress: {response['steps_completed']}/{response['total_steps']}")
        print("   ✓ All steps completed!")
    else:
        print("❌ FAIL: Step 3 not tracked correctly")
        return False
    
    # Try to end without completing all steps - should FAIL
    print("\n→ Testing end_job enforcement of step completion...")
    
    # Start new session with incomplete steps
    handler2 = WorkflowToolsHandler(project_root, config_dir)
    await handler2.handle_start_work({"user_goal": "Test incomplete"})
    await handler2.handle_plan_setup({"plan_steps": ["Step 1", "Step 2", "Step 3"]})
    await handler2.handle_proceed({"completed_work": "Only step 1"})
    
    result = await handler2.handle_end_job({
        "summary": "Trying to end early",
        "agentreadme_content": "# Test\nSome content here"
    })
    
    response = json.loads(result[0].text)
    if "error" in response and "incomplete plan" in response["error"]["message"].lower():
        print("✅ PASS: Correctly blocked end_job with incomplete steps")
        print(f"   Error: {response['error']['message']}")
    else:
        print("❌ FAIL: Should have blocked end_job with incomplete steps")
        return False
    
    return True


async def test_enhancement_4_start_work_description():
    """Test that start_work tool description emphasizes universal requirement"""
    print("\n" + "="*70)
    print("TEST 4: start_work description emphasizes universal requirement")
    print("="*70)
    
    project_root = Path.cwd()
    config_dir = project_root / ".agent_handoff"
    
    handler = WorkflowToolsHandler(project_root, config_dir)
    tools = handler.get_workflow_tools()
    
    start_work_tool = next(t for t in tools if t.name == "start_work")
    description = start_work_tool.description
    
    print(f"\nstart_work description:\n{description}\n")
    
    # Check for key phrases
    checks = [
        ("ANY project", "emphasizes it's not just for agent-handoff"),
        ("ALL complex features", "emphasizes universal requirement"),
        ("bad code", "warns about consequences of skipping"),
        ("project context", "mentions context retrieval"),
        ("NOT optional", "emphasizes mandatory nature")
    ]
    
    passed = True
    for phrase, reason in checks:
        if phrase.lower() in description.lower():
            print(f"✅ Contains '{phrase}' - {reason}")
        else:
            print(f"❌ Missing '{phrase}' - {reason}")
            passed = False
    
    if passed:
        print("\n✅ PASS: start_work description properly emphasizes universal requirement")
    else:
        print("\n❌ FAIL: start_work description missing key messaging")
    
    return passed


async def test_enhancement_5_docs_file_warning():
    """Test that write_file warns about non-doc files"""
    print("\n" + "="*70)
    print("TEST 5: write_file warns about non-doc files in docs/")
    print("="*70)
    
    project_root = Path.cwd()
    docs_dir = project_root / "docs"
    
    handler = UtilityToolsHandler(project_root, docs_dir)
    
    # Test writing .md file - should NOT warn
    print("\n→ Testing write .md file (should NOT warn)...")
    result = await handler.handle_write_file({
        "path": "test_enhancement_5.md",
        "content": "# Test File\nThis is a markdown file."
    })
    
    response = json.loads(result[0].text)
    if "warnings" not in response or not any("WARNING" in w for w in response.get("warnings", [])):
        print("✅ PASS: .md file does NOT trigger warning")
    else:
        print("❌ FAIL: .md file should NOT trigger warning")
        print(f"   Warnings: {response.get('warnings')}")
        return False
    
    # Test writing .py file - should WARN
    print("\n→ Testing write .py file (should WARN)...")
    result = await handler.handle_write_file({
        "path": "test_code.py",
        "content": "# Python code\nprint('hello')"
    })
    
    response = json.loads(result[0].text)
    if "warnings" in response and any(".py file" in w for w in response["warnings"]):
        print("✅ PASS: .py file triggers warning")
        print(f"   Warning message: {response['warnings'][0]}")
    else:
        print("❌ FAIL: .py file should trigger warning")
        return False
    
    # Test writing .cpp file - should WARN
    print("\n→ Testing write .cpp file (should WARN)...")
    result = await handler.handle_write_file({
        "path": "test_code.cpp",
        "content": "// C++ code\nint main() { return 0; }"
    })
    
    response = json.loads(result[0].text)
    if "warnings" in response and any(".cpp file" in w for w in response["warnings"]):
        print("✅ PASS: .cpp file triggers warning")
        print(f"   Warning message: {response['warnings'][0]}")
    else:
        print("❌ FAIL: .cpp file should trigger warning")
        return False
    
    # Cleanup test files
    (docs_dir / "test_enhancement_5.md").unlink(missing_ok=True)
    (docs_dir / "test_code.py").unlink(missing_ok=True)
    (docs_dir / "test_code.cpp").unlink(missing_ok=True)
    print("\n✓ Cleaned up test files")
    
    return True


async def test_enhancement_bonus_plan_recommendations():
    """Test that start_work includes plan recommendations"""
    print("\n" + "="*70)
    print("BONUS TEST: start_work includes plan recommendations")
    print("="*70)
    
    project_root = Path.cwd()
    config_dir = project_root / ".agent_handoff"
    
    handler = WorkflowToolsHandler(project_root, config_dir)
    
    result = await handler.handle_start_work({"user_goal": "Test plan recommendations"})
    response = json.loads(result[0].text)
    
    print("\nstart_work response:")
    print(json.dumps(response, indent=2, ensure_ascii=False))
    
    if "recommended_plan_steps" in response:
        steps = response["recommended_plan_steps"]
        print(f"\n✅ PASS: Found {len(steps)} recommended plan steps:")
        for step in steps:
            print(f"   • {step}")
        return True
    else:
        print("\n❌ FAIL: No recommended_plan_steps in response")
        return False


async def main():
    """Run all tests"""
    print("\n" + "="*70)
    print("AGENT-HANDOFF v0.3.0 ENHANCEMENT TESTS")
    print("="*70)
    
    tests = [
        ("Enhancement 1: end_job requires agentreadme", test_enhancement_1_agentreadme_required),
        ("Enhancement 2: plan_setup requires list", test_enhancement_2_plan_steps_list),
        ("Enhancement 3: proceed tracks steps", test_enhancement_3_step_tracking),
        ("Enhancement 4: start_work description", test_enhancement_4_start_work_description),
        ("Enhancement 5: docs file warnings", test_enhancement_5_docs_file_warning),
        ("Bonus: plan recommendations", test_enhancement_bonus_plan_recommendations),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            passed = await test_func()
            results.append((test_name, passed))
        except Exception as e:
            print(f"\n❌ EXCEPTION in {test_name}: {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    total = len(results)
    passed_count = sum(1 for _, p in results if p)
    
    print(f"\nTotal: {passed_count}/{total} tests passed")
    
    if passed_count == total:
        print("\n🎉 ALL TESTS PASSED! v0.3.0 enhancements are working correctly.")
        return 0
    else:
        print(f"\n⚠️ {total - passed_count} test(s) failed. Please review the output above.")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
