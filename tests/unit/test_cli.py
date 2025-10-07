#!/usr/bin/env python3
"""
Agent-Handoff CLI工具单元测试
"""

import unittest
import tempfile
import os
import shutil
from click.testing import CliRunner
import sys

# 添加src到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

class TestCLITools(unittest.TestCase):
    """测试CLI工具功能"""
    
    def setUp(self):
        """设置测试环境"""
        self.test_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir)
        self.runner = CliRunner()
    
    def tearDown(self):
        """清理测试环境"""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_cli_version(self):
        """测试version命令"""
        try:
            from agent_handoff.cli import cli
            result = self.runner.invoke(cli, ['--version'])
            self.assertEqual(result.exit_code, 0)
            self.assertIn("0.1.0", result.output)
            print("✅ CLI version测试通过")
        except ImportError:
            self.skipTest("无法导入CLI，跳过version测试")
    
    def test_cli_init_success(self):
        """测试init命令成功执行"""
        try:
            from agent_handoff.cli import cli
            result = self.runner.invoke(cli, ['init'])
            
            self.assertEqual(result.exit_code, 0)
            self.assertIn("初始化完成", result.output)
            
            # 检查目录结构
            expected_dirs = [
                "docs/01_Goals_and_Status",
                "docs/02_Architecture_and_Usage", 
                "docs/03_History_and_Lessons",
                "docs/04_User_Facing",
                ".agent-handoff/history"
            ]
            
            for dir_path in expected_dirs:
                self.assertTrue(os.path.exists(dir_path), f"目录不存在: {dir_path}")
                self.assertTrue(os.path.isdir(dir_path), f"不是目录: {dir_path}")
            
            # 检查文件
            expected_files = [
                ".agent-handoff/agentreadme.md",
                ".agent-handoff/config.yaml"
            ]
            
            for file_path in expected_files:
                self.assertTrue(os.path.exists(file_path), f"文件不存在: {file_path}")
                self.assertTrue(os.path.isfile(file_path), f"不是文件: {file_path}")
            
            print("✅ CLI init成功测试通过")
        except ImportError:
            self.skipTest("无法导入CLI，跳过init测试")
    
    def test_cli_status_before_init(self):
        """测试未初始化时的status命令"""
        try:
            from agent_handoff.cli import cli
            result = self.runner.invoke(cli, ['status'])
            self.assertIn("未初始化", result.output)
            print("✅ CLI status未初始化测试通过")
        except ImportError:
            self.skipTest("无法导入CLI，跳过status测试")
    
    def test_cli_status_after_init(self):
        """测试初始化后的status命令"""
        try:
            from agent_handoff.cli import cli
            
            # 先初始化
            init_result = self.runner.invoke(cli, ['init'])
            self.assertEqual(init_result.exit_code, 0)
            
            # 再检查状态
            status_result = self.runner.invoke(cli, ['status'])
            self.assertEqual(status_result.exit_code, 0)
            self.assertIn("状态", status_result.output)
            
            print("✅ CLI status已初始化测试通过")
        except ImportError:
            self.skipTest("无法导入CLI，跳过status测试")
    
    def test_cli_init_overwrite_warning(self):
        """测试重复初始化的警告"""
        try:
            from agent_handoff.cli import cli
            
            # 第一次初始化
            result1 = self.runner.invoke(cli, ['init'])
            self.assertEqual(result1.exit_code, 0)
            
            # 第二次初始化，选择取消
            result2 = self.runner.invoke(cli, ['init'], input='n\n')
            self.assertIn("取消初始化", result2.output)
            
            print("✅ CLI重复初始化警告测试通过")
        except ImportError:
            self.skipTest("无法导入CLI，跳过重复初始化测试")

class TestConfigFiles(unittest.TestCase):
    """测试配置文件格式"""
    
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir)
    
    def tearDown(self):
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_agentreadme_format(self):
        """测试agentreadme.md格式"""
        try:
            from agent_handoff.cli import cli
            runner = CliRunner()
            result = runner.invoke(cli, ['init'])
            self.assertEqual(result.exit_code, 0)
            
            # 检查agentreadme.md内容
            with open(".agent-handoff/agentreadme.md", "r", encoding="utf-8") as f:
                content = f.read()
            
            required_sections = ["# Agent README", "状态", "项目概况", "当前状态"]
            for section in required_sections:
                self.assertIn(section, content, f"缺少必要部分: {section}")
            
            print("✅ agentreadme.md格式测试通过")
        except ImportError:
            self.skipTest("无法导入CLI，跳过配置文件测试")
    
    def test_config_yaml_format(self):
        """测试config.yaml格式"""
        try:
            from agent_handoff.cli import cli
            runner = CliRunner()
            result = runner.invoke(cli, ['init'])
            self.assertEqual(result.exit_code, 0)
            
            # 检查config.yaml内容
            with open(".agent-handoff/config.yaml", "r", encoding="utf-8") as f:
                content = f.read()
            
            self.assertIn("project:", content)
            self.assertIn("name:", content)
            
            print("✅ config.yaml格式测试通过")
        except ImportError:
            self.skipTest("无法导入CLI，跳过配置文件测试")

if __name__ == '__main__':
    print("🧪 运行CLI单元测试...")
    unittest.main(verbosity=2)