# src/agent_handoff/cli.py
# CLI 工具 - init 命令

import click
import json
import os


@click.group()
@click.version_option(version="0.1.0")
def cli():
    """
    Agent-Handoff - 项目级 AI 协作系统
    
        click.echo(f"✓ Created {config_path}")
       cl    click.echo("3. Restart VSCode/Cursor")
    click.echo("4. Check MCP connection status in bottom-right corner")
    click.echo("5. In Copilot, type: 'Call start_work to begin development'\n")
    
    click.echo("💡 Tips:")
    click.echo("- If connection fails, check that Python path is correct")
    click.echo("- Ensure agent-handoff is installed in current Python environment")
    click.echo("- Check VSCode Output panel MCP logs for error details\n")("3. Restart VSCode/Cursor")
    click.echo("4. Check MCP connection status in bottom-right corner")
    click.echo("5. In Copilot, type: 'Call start_work to begin development'\n")
    
    click.echo("💡 Tips:")
    click.echo("- If connection fails, check that Python path is correct")
    click.echo("- Ensure agent-handoff is installed in current Python environment")
    click.echo("- Check VSCode Output panel MCP logs for error details\n") 6. Print next steps
    click.echo("\n" + "="*60)
    click.echo("🎉 Initialization Complete!")
    click.echo("="*60)
    
    click.echo("\n📝 Next Step: Configure your IDE\n")：
        agent-handoff init     # 初始化项目
    """
    pass


@cli.command()
def init():
    """
    初始化项目的 docs/ 目录和配置文件
    
    这会创建推荐的目录结构：
    - docs/01_Goals_and_Status/       # 目标、现状、规范
    - docs/02_Architecture_and_Usage/ # 架构、API 用法
    - docs/03_History_and_Lessons/    # 历史和教训
    - docs/04_User_Facing/            # 面向用户的文档
    - .agent-handoff/                 # 配置和状态
    """
    
    # 检查是否已经初始化
    if os.path.exists(".agent-handoff"):
        if not click.confirm("⚠️  项目已初始化过。是否重新初始化？", default=False):
            click.echo("❌ 取消初始化")
            return
    
    click.echo("📦 Initializing Agent-Handoff...\n")
    
    # 1. 创建目录结构
    dirs = [
        "docs/01_Goals_and_Status",
        "docs/02_Architecture_and_Usage",
        "docs/03_History_and_Lessons",
        "docs/04_User_Facing",
        ".agent-handoff/history",
    ]
    
    for d in dirs:
        os.makedirs(d, exist_ok=True)
        click.echo(f"✓ Created {d}/")
    
    # 2. Create agentreadme.md
    agentreadme_path = ".agent-handoff/agentreadme.md"
    if not os.path.exists(agentreadme_path):
        with open(agentreadme_path, 'w', encoding='utf-8') as f:
            f.write("""# Agent README

**Status**: Not Started  
**Last Updated**: Project Initialization  

## Project Overview

This is a new project. After the first Agent completes a task, handoff documentation will be automatically generated here.

## Current Status

- Agent-Handoff has been initialized
- Waiting for first development task

## Next Steps

Please:
1. Fill in project goals and requirements in `docs/01_Goals_and_Status/`
2. Describe technical architecture in `docs/02_Architecture_and_Usage/`
3. Call `start_work` tool to begin first task

---

💡 This document will be automatically updated by the Agent at the end of each task.
""")
        click.echo(f"✓ Created {agentreadme_path}")
    
    # 3. 创建示例文档
    example_docs = {
        "docs/01_Goals_and_Status/README.md": """# 目标与状态

本目录存放：
- 项目整体目标和愿景
- 当前开发进度
- 开发规范和准则

## 建议的文档

- `vision.md` - 项目愿景和目标
- `current_progress.md` - 当前进度
- `development_guide.md` - 开发规范
""",
        "docs/02_Architecture_and_Usage/README.md": """# 架构与用法

本目录存放：
- 技术架构设计
- API 文档
- 组件使用说明

## 建议的文档

- `architecture.md` - 系统架构
- `api.md` - API 接口文档
- `components.md` - 组件说明
""",
        "docs/03_History_and_Lessons/README.md": """# 历史与教训

本目录存放：
- 开发历史记录
- 决策记录
- Bug 追踪
- 经验教训

## 建议的文档

- `timeline.md` - 开发时间线
- `decisions.md` - 重要决策记录
- `bug_tracker.md` - Bug 追踪
- `lessons_learned.md` - 经验教训
""",
        "docs/04_User_Facing/README.md": """# 面向用户的文档

本目录存放：
- 最终用户文档
- 使用指南
- FAQ

## 建议的文档

- `README.md` - 项目介绍（可复制到项目根目录）
- `user_guide.md` - 使用指南
- `faq.md` - 常见问题
"""
    }
    
    for path, content in example_docs.items():
        if not os.path.exists(path):
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            click.echo(f"✓ Created {path}")
    
    # 4. Create .vscode/mcp.json configuration file
    vscode_dir = ".vscode"
    if not os.path.exists(vscode_dir):
        os.makedirs(vscode_dir)
    
    # 检测当前Python环境
    import sys
    python_exe = sys.executable
    current_dir = os.path.abspath(".")
    
    # 生成VSCode MCP配置
    vscode_mcp_config = {
        "servers": {
            "agent-handoff": {
                "type": "stdio",
                "command": python_exe,
                "args": ["-m", "agent_handoff.server"],
                "cwd": current_dir
            }
        },
        "inputs": []
    }
    
    vscode_mcp_path = os.path.join(vscode_dir, "mcp.json")
    if not os.path.exists(vscode_mcp_path):
        with open(vscode_mcp_path, 'w', encoding='utf-8') as f:
            json.dump(vscode_mcp_config, f, indent=2)
        click.echo(f"✓ Created {vscode_mcp_path}")
    
    # 5. Create configuration files
    config_path = ".agent-handoff/config.yaml"
    if not os.path.exists(config_path):
        with open(config_path, 'w', encoding='utf-8') as f:
            f.write("""# Agent-Handoff 配置文件

project:
  name: "未命名项目"
  description: ""
  
# 未来版本的配置项...
# docs:
#   structure:
#     custom_mapping: false
""")
        click.echo(f"✓ Created {config_path}")
    
    # 5. 创建 .gitignore（如果项目有 Git）
    if os.path.exists(".git"):
        gitignore_path = ".agent-handoff/.gitignore"
        if not os.path.exists(gitignore_path):
            with open(gitignore_path, 'w', encoding='utf-8') as f:
                f.write("""# Agent-Handoff 临时文件
*.pyc
__pycache__/
.DS_Store

# 可选：不提交会话历史（如果包含敏感信息）
# history/
""")
            click.echo(f"✓ 创建 {gitignore_path}")
    
    # 6. 打印下一步指引
    click.echo("\n" + "="*60)
    click.echo("🎉 Initialization Complete!")
    click.echo("="*60)
    
    click.echo("\n📝 Next Step: Configure your IDE\n")
    
    click.echo("📋 VSCode/Cursor Configuration:")
    click.echo("✅ Auto-created .vscode/mcp.json configuration file")
    click.echo("   If using virtual environment, config automatically uses correct Python path\n")
    
    click.echo("🔧 Manual Configuration (if auto-config doesn't work):")
    click.echo("Method 1 - Use UI Configuration:")
    click.echo("1. VSCode: Open Command Palette (Ctrl+Shift+P) → 'MCP: Configure'")
    click.echo("2. Or click MCP status in bottom-right → 'Configure MCP Servers'")
    click.echo("3. Add server with following parameters:")
    
    # 获取当前Python路径
    import sys
    python_path = sys.executable
    current_dir = os.path.abspath(".")
    
    click.echo(f"   - Command: {python_path}")
    click.echo("   - Args: -m agent_handoff.server")
    click.echo(f"   - Working Directory: {current_dir}\n")
    
    click.echo("Method 2 - Manual settings.json editing:")
    click.echo("1. Open settings.json (Ctrl+Shift+P → 'Preferences: Open User Settings (JSON)')")
    click.echo("2. Add the following configuration:\n")
    
    click.secho(f'''{{
  "mcp": {{
    "servers": {{
      "agent-handoff": {{
        "command": "{python_path}",
        "args": ["-m", "agent_handoff.server"],
        "cwd": "{current_dir}"
      }}
    }}
  }}
}}''', fg="cyan")
    
    click.echo("\n3. 重启 VSCode/Cursor")
    click.echo("4. 检查右下角MCP连接状态")
    click.echo("5. 在 Copilot 中输入: 'Call start_work to begin development'\n")
    
    click.echo("� 提示:")
    click.echo("- 如果连接失败，检查Python路径是否正确")
    click.echo("- 确保 agent-handoff 已安装到当前Python环境")
    click.echo("- 查看VSCode输出面板的MCP日志获取错误信息\n")
    
    click.echo("📚 More docs: https://github.com/Sithcighce/AgentHandOff")


@cli.command()
def status():
    """Check current project status"""
    
    if not os.path.exists(".agent-handoff"):
        click.echo("❌ Project not initialized. Please run: agent-handoff init")
        return
    
    click.echo("📊 Agent-Handoff Status\n")
    
    # Check agentreadme
    agentreadme_path = ".agent-handoff/agentreadme.md"
    if os.path.exists(agentreadme_path):
        with open(agentreadme_path, 'r', encoding='utf-8') as f:
            content = f.read()
        click.echo(f"✓ agentreadme.md: {len(content)} characters")
    else:
        click.echo("⚠️  agentreadme.md does not exist")
    
    # Check document count
    docs_count = 0
    for root, dirs, files in os.walk("docs"):
        docs_count += len([f for f in files if f.endswith('.md')])
    click.echo(f"✓ Document count: {docs_count} files")
    
    # Check session history
    history_dir = ".agent-handoff/history"
    if os.path.exists(history_dir):
        sessions = [f for f in os.listdir(history_dir) if f.endswith('.json')]
        click.echo(f"✓ Session history: {len(sessions)} sessions")
        
        if sessions:
            click.echo("\nRecent sessions:")
            for session_file in sorted(sessions)[-3:]:
                click.echo(f"  - {session_file}")
    
    click.echo()


@cli.command()
def diagnose():
    """Diagnose MCP server environment and configuration"""
    click.echo("🔧 Running MCP environment diagnostics...")
    
    try:
        # 运行诊断脚本
        import subprocess
        import sys
        
        # Get diagnostic script path
        current_dir = os.path.dirname(__file__)
        tools_dir = os.path.join(os.path.dirname(current_dir), "..", "tools")
        diagnose_script = os.path.join(tools_dir, "mcp_diagnostics.py")
        
        if os.path.exists(diagnose_script):
            subprocess.run([sys.executable, diagnose_script])
        else:
            # 如果找不到外部脚本，运行内置诊断
            click.echo("运行内置诊断...")
            _run_builtin_diagnostics()
            
    except Exception as e:
        click.echo(f"诊断失败: {e}")
        _run_builtin_diagnostics()


def _run_builtin_diagnostics():
    """内置诊断功能"""
    import sys
    
    click.echo("\n🔍 环境检查:")
    click.echo(f"Python版本: {sys.version}")
    click.echo(f"Python路径: {sys.executable}")
    
    # 检查agent_handoff是否可导入
    try:
        import agent_handoff
        click.echo(f"✅ agent-handoff已安装: {agent_handoff.__version__}")
    except ImportError:
        click.echo("❌ agent-handoff未安装")
        click.echo("请运行: pip install git+https://github.com/Sithcighce/AgentHandOff.git#egg=agent-handoff")
        return
    
    # 检查MCP服务器
    try:
        from agent_handoff.server import AgentHandoffServer
        click.echo("✅ MCP服务器模块可用")
    except ImportError as e:
        click.echo(f"❌ MCP服务器导入失败: {e}")
        return
    
    # 生成配置建议
    click.echo(f"\n⚙️ 推荐MCP配置:")
    click.echo(f'''{{
  "mcp": {{
    "servers": {{
      "agent-handoff": {{
        "command": "{sys.executable}",
        "args": ["-m", "agent_handoff.server"],
        "cwd": "{os.getcwd()}"
      }}
    }}
  }}
}}''')


if __name__ == "__main__":
    cli()