# src/agent_handoff/cli.py
# CLI 工具 - init 命令

import click
import os


@click.group()
@click.version_option(version="0.1.0")
def cli():
    """
    Agent-Handoff - 项目级 AI 协作系统
    
    使用方法：
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
    
    click.echo("📦 开始初始化 Agent-Handoff...\n")
    
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
        click.echo(f"✓ 创建 {d}/")
    
    # 2. 创建 agentreadme.md
    agentreadme_path = ".agent-handoff/agentreadme.md"
    if not os.path.exists(agentreadme_path):
        with open(agentreadme_path, 'w', encoding='utf-8') as f:
            f.write("""# Agent README

**状态**: 未开始  
**最后更新**: 项目初始化  

## 项目概况

这是一个新项目。第一个 Agent 完成任务后，这里会自动生成项目交接文档。

## 当前状态

- 项目已初始化 Agent-Handoff
- 等待第一个开发任务

## 下一步

请：
1. 在 `docs/01_Goals_and_Status/` 中填写项目目标和需求
2. 在 `docs/02_Architecture_and_Usage/` 中说明技术架构
3. 调用 `start_work` 工具开始第一个任务

---

💡 这个文档会在每次任务结束时由 Agent 自动更新。
""")
        click.echo(f"✓ 创建 {agentreadme_path}")
    
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
            click.echo(f"✓ 创建 {path}")
    
    # 4. 创建配置文件
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
        click.echo(f"✓ 创建 {config_path}")
    
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
    click.echo("🎉 初始化完成！")
    click.echo("="*60)
    
    click.echo("\n📝 下一步：配置你的 IDE\n")
    
    click.echo("如果你使用 VSCode 或 Cursor (支持GitHub Copilot)：")
    click.echo("方法1 - 使用界面配置（推荐）：")
    click.echo("1. 点击右下角的工具选项 🔧")
    click.echo("2. 选择 '配置MCP服务器'")
    click.echo("3. 点击上方栏右侧 '添加MCP服务器'")
    click.echo("4. 选择 '命令类型'")
    click.echo("5. 输入命令：python -m agent_handoff.server")
    click.echo("6. 设置工作目录为当前项目根目录\n")
    
    click.echo("方法2 - 手动配置settings.json：")
    click.echo("1. 打开 settings.json（命令面板: Preferences: Open User Settings (JSON)）")
    click.echo("2. 添加以下配置：\n")
    
    click.secho("""
{
  "mcp": {
    "servers": {
      "agent-handoff": {
        "command": "python",
        "args": ["-m", "agent_handoff.server"],
        "cwd": "${workspaceFolder}",
        "env": {
          "PYTHONPATH": "${workspaceFolder}"
        }
      }
    }
  }
}
""", fg="cyan")
    
    click.echo("\n3. 重启 IDE")
    click.echo("4. 在 Copilot/Claude 中输入: '调用 start_work，我要开始开发'\n")
    
    click.echo("📚 更多文档: https://github.com/Sithcighce/AgentHandOff\n")
    
    click.echo("⚠️  重要提示：")
    click.echo("- 确保使用正确的Python环境（虚拟环境或全局环境）")
    click.echo("- 如果使用虚拟环境，请在MCP配置中指定完整的Python路径")
    click.echo("- 重启VSCode后MCP服务器才会生效")


@cli.command()
def status():
    """查看当前项目状态"""
    
    if not os.path.exists(".agent-handoff"):
        click.echo("❌ 项目未初始化。请先运行: agent-handoff init")
        return
    
    click.echo("📊 Agent-Handoff 状态\n")
    
    # 检查 agentreadme
    agentreadme_path = ".agent-handoff/agentreadme.md"
    if os.path.exists(agentreadme_path):
        with open(agentreadme_path, 'r', encoding='utf-8') as f:
            content = f.read()
        click.echo(f"✓ agentreadme.md: {len(content)} 字符")
    else:
        click.echo("⚠️  agentreadme.md 不存在")
    
    # 检查文档数量
    docs_count = 0
    for root, dirs, files in os.walk("docs"):
        docs_count += len([f for f in files if f.endswith('.md')])
    click.echo(f"✓ 文档数量: {docs_count} 个")
    
    # 检查会话历史
    history_dir = ".agent-handoff/history"
    if os.path.exists(history_dir):
        sessions = [f for f in os.listdir(history_dir) if f.endswith('.json')]
        click.echo(f"✓ 历史会话: {len(sessions)} 个")
        
        if sessions:
            click.echo("\n最近的会话:")
            for session_file in sorted(sessions)[-3:]:
                click.echo(f"  - {session_file}")
    
    click.echo()


@cli.command()
def diagnose():
    """诊断MCP服务器环境和配置"""
    click.echo("🔧 运行MCP环境诊断...")
    
    try:
        # 运行诊断脚本
        import subprocess
        import sys
        
        # 获取诊断脚本路径
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