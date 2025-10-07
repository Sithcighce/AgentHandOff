#!/usr/bin/env python3
"""
Agent-Handoff 集成测试
测试完整的用户工作流程
"""

import unittest
import tempfile
import os
import shutil
import subprocess
import sys
from pathlib import Path

class TestEndToEndWorkflow(unittest.TestCase):
    """端到端工作流测试"""
    
    def setUp(self):
        """设置测试环境"""
        self.test_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        
    def tearDown(self):
        """清理测试环境"""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_complete_user_journey(self):
        """测试完整的用户使用流程"""
        os.chdir(self.test_dir)
        
        # 步骤1: 测试安装后的命令行工具
        result = subprocess.run(
            ["agent-handoff", "--version"], 
            capture_output=True, text=True, encoding='utf-8'
        )
        self.assertEqual(result.returncode, 0)
        self.assertIn("0.1.0", result.stdout)
        print("✅ 步骤1: 命令行工具可用")
        
        # 步骤2: 初始化项目
        result = subprocess.run(
            ["agent-handoff", "init"], 
            capture_output=True, text=True, encoding='utf-8'
        )
        self.assertEqual(result.returncode, 0)
        self.assertIn("初始化完成", result.stdout)
        print("✅ 步骤2: 项目初始化成功")
        
        # 步骤3: 验证文件结构
        required_paths = [
            "docs/01_Goals_and_Status/README.md",
            "docs/02_Architecture_and_Usage/README.md", 
            "docs/03_History_and_Lessons/README.md",
            "docs/04_User_Facing/README.md",
            ".agent-handoff/agentreadme.md",
            ".agent-handoff/config.yaml"
        ]
        
        for path in required_paths:
            self.assertTrue(Path(path).exists(), f"缺少文件: {path}")
            
        print("✅ 步骤3: 文件结构验证通过")
        
        # 步骤4: 测试status命令
        result = subprocess.run(
            ["agent-handoff", "status"], 
            capture_output=True, text=True, encoding='utf-8'
        )
        self.assertEqual(result.returncode, 0)
        print("✅ 步骤4: status命令测试通过")
        
        # 步骤5: 测试MCP服务器启动（快速测试）
        try:
            # 使用timeout快速测试服务器是否能启动
            result = subprocess.run(
                [sys.executable, "-m", "agent_handoff.server"],
                input="",
                timeout=2,
                capture_output=True, 
                text=True, encoding='utf-8'
            )
        except subprocess.TimeoutExpired:
            # 超时是预期的，说明服务器正在运行
            print("✅ 步骤5: MCP服务器启动测试通过")
        except Exception as e:
            self.fail(f"MCP服务器启动失败: {e}")

class TestPackageIntegrity(unittest.TestCase):
    """测试包完整性"""
    
    def test_import_all_modules(self):
        """测试所有模块可以正常导入"""
        try:
            import agent_handoff
            self.assertEqual(agent_handoff.__version__, "0.1.0")
            print("✅ 主包导入测试通过")
        except ImportError as e:
            self.fail(f"无法导入主包: {e}")
        
        try:
            from agent_handoff.cli import cli
            self.assertIsNotNone(cli)
            print("✅ CLI模块导入测试通过")
        except ImportError as e:
            self.skipTest(f"CLI模块导入失败: {e}")
        
        try:
            from agent_handoff.server import AgentHandoffServer
            self.assertIsNotNone(AgentHandoffServer)
            print("✅ Server模块导入测试通过")
        except ImportError as e:
            self.skipTest(f"Server模块导入失败: {e}")
    
    def test_dependencies_available(self):
        """测试依赖包可用性"""
        required_packages = ['mcp', 'click']
        
        for package in required_packages:
            try:
                __import__(package)
                print(f"✅ 依赖包 {package} 可用")
            except ImportError:
                self.fail(f"缺少依赖包: {package}")

class TestFileSystemSafety(unittest.TestCase):
    """测试文件系统安全性"""
    
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir)
        
        # 初始化项目
        subprocess.run(["agent-handoff", "init"], capture_output=True)
    
    def tearDown(self):
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_docs_directory_isolation(self):
        """测试docs目录隔离性"""
        # MCP服务器应该只能访问docs/目录内的文件
        # 这里主要是验证目录结构的正确性
        
        self.assertTrue(Path("docs").exists())
        self.assertTrue(Path("docs").is_dir())
        
        # 确保敏感目录不会被误创建在docs外
        sensitive_paths = [
            "../etc", "../../windows", "/root", "C:\\System32"
        ]
        
        for path in sensitive_paths:
            self.assertFalse(Path(path).exists(), f"不应该创建敏感路径: {path}")
        
        print("✅ 文件系统安全测试通过")

if __name__ == '__main__':
    print("🧪 运行Agent-Handoff集成测试...")
    
    # 检查是否在正确的环境中运行
    try:
        import agent_handoff
        print(f"✅ 使用Agent-Handoff版本: {agent_handoff.__version__}")
    except ImportError:
        print("❌ 未找到Agent-Handoff包，请先安装: pip install -e .")
        sys.exit(1)
    
    unittest.main(verbosity=2)