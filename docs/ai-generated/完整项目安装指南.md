# Agent-Handoff 完整项目结构

## 📁 仓库结构

```
agent-handoff/
├── src/
│   └── agent_handoff/
│       ├── __init__.py          # 包初始化
│       ├── __main__.py          # 让 python -m 能工作
│       ├── server.py            # MCP 服务器核心 ⭐
│       └── cli.py               # CLI 工具 (init/status)
│
├── tests/                       # 测试（未来）
│   ├── test_server.py
│   └── test_workflow.py
│
├── docs/                        # 项目文档
│   ├── design/                  # 设计文档
│   │   ├── 产品愿景与核心设计.md
│   │   ├── MVP功能与用户流程.md
│   │   ├── 技术架构与实现.md
│   │   ├── MCP服务器工具及规范.md
│   │   └── 开发路线图与成功指标.md
│   │
│   └── guides/                  # 使用指南
│       ├── quickstart.md
│       ├── ide-setup.md
│       └── troubleshooting.md
│
├── examples/                    # 示例项目
│   └── demo-app/
│       ├── docs/
│       ├── .agent-handoff/
│       └── README.md
│
├── .gitignore
├── pyproject.toml              # ⭐ Python 项目配置
├── README.md                   # ⭐ 项目介绍
├── LICENSE
└── CONTRIBUTING.md
```

## 📦 安装与开发

### 从源码安装（当前阶段）

```bash
# 1. 克隆仓库
git clone https://github.com/yourusername/agent-handoff.git
cd agent-handoff

# 2. 创建虚拟环境（推荐）
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 3. 安装为可编辑模式
pip install -e .

# 4. 验证安装
agent-handoff --version
python -m agent_handoff.server --help
```

### 发布到 PyPI 后（未来）

```bash
pip install agent-handoff
```

## 🔧 开发环境设置

### 1. 安装开发依赖

```bash
pip install -e ".[dev]"
```

### 2. 运行测试

```bash
pytest tests/
```

### 3. 代码格式化

```bash
# 如果未来添加这些工具
black src/
isort src/
mypy src/
```

## 🚀 使用流程（开发者视角）

### 场景：初始化一个新项目

```bash
# 1. 进入项目目录
cd ~/projects/my-awesome-app

# 2. 初始化 Agent-Handoff
agent-handoff init

# 输出：
# 📦 开始初始化 Agent-Handoff...
# 
# ✓ 创建 docs/01_Goals_and_Status/
# ✓ 创建 docs/02_Architecture_and_Usage/
# ✓ 创建 docs/03_History_and_Lessons/
# ✓ 创建 docs/04_User_Facing/
# ✓ 创建 .agent-handoff/history/
# ✓ 创建 .agent-handoff/agentreadme.md
# ✓ 创建 .agent-handoff/config.yaml
# 
# 🎉 初始化完成！
```

### 场景：配置 VSCode

```json
// ~/.config/Code/User/settings.json 或 .vscode/settings.json

{
  "mcp": {
    "servers": {
      "agent-handoff": {
        "command": "python",
        "args": ["-m", "agent_handoff.server"],
        "cwd": "${workspaceFolder}"
      }
    }
  },
  
  // 可选：添加系统提示
  "github.copilot.chat.welcomeMessage": [
    "本项目使用 Agent-Handoff 进行任务管理。",
    "开始工作前请调用 start_work 工具。",
    "工作流程：start_work → plan_setup → proceed → end_job"
  ]
}
```

### 场景：Agent 的第一次任务

```
开发者: @copilot 开始工作，我要实现用户注册功能

Copilot: 
(后台调用 start_work)

📋 任务已启动！会话 ID: sess_20251007_103045

我已阅读项目交接文档：
- 这是第一次任务
- 项目刚初始化

接下来我会制定详细计划...

(后台调用 plan_setup)

✅ 计划已提交：
1. 设计用户数据模型
2. 创建注册 API 端点
3. 实现前端注册表单
4. 添加表单验证
5. 编写单元测试

现在开始执行第 1 步...

[Agent 开始工作...]

(完成后调用 proceed)

✅ 步骤 1 完成：用户数据模型已设计
- 字段：username, email, password_hash, created_at
- 使用 SQLAlchemy ORM

继续执行第 2 步...

[继续工作...]

(所有步骤完成后)

(后台调用 write_file 更新文档)
(后台调用 end_job)

🎉 任务成功结束！

我已更新：
- .agent-handoff/agentreadme.md（交接文档）
- docs/01_Goals_and_Status/current_progress.md
- docs/02_Architecture_and_Usage/api.md

下一个 Agent 将能看到这些成果。
```

## 🔍 调试技巧

### 查看 MCP 服务器日志

```bash
# 服务器通过 stderr 输出日志
# 在 VSCode 中，查看 Output 面板 → MCP: agent-handoff
```

### 手动测试工具

```python
# 创建一个测试脚本 test_mcp.py
import asyncio
import json
from agent_handoff.server import AgentHandoffServer

async def test():
    server = AgentHandoffServer()
    
    # 测试 read_file
    result = await server._read_file("01_Goals_and_Status/README.md")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    # 测试 start_work
    result = await server._start_work("测试任务")
    print(json.dumps(result, indent=2, ensure_ascii=False))

asyncio.run(test())
```

### 检查项目状态

```bash
agent-handoff status

# 输出：
# 📊 Agent-Handoff 状态
# 
# ✓ agentreadme.md: 1234 字符
# ✓ 文档数量: 8 个
# ✓ 历史会话: 3 个
# 
# 最近的会话:
#   - sess_20251006_103045.json
#   - sess_20251007_142030.json
```

## 📝 关键文件说明

### pyproject.toml

```toml
[build-system]
requires = ["setuptools>=68.0"]
build-backend = "setuptools.build_meta"

[project]
name = "agent-handoff"
version = "0.1.0"
description = "项目级 AI 协作记忆与工作流系统"
readme = "README.md"
requires-python = ">=3.10"
dependencies = [
    "mcp>=0.9.0",      # MCP SDK
    "click>=8.0.0",    # CLI 工具
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "black>=23.0.0",
    "mypy>=1.0.0",
]

[project.scripts]
# 这让 `agent-handoff` 命令可用
agent-handoff = "agent_handoff.cli:cli"

[tool.setuptools.packages.find]
where = ["src"]
```

### src/agent_handoff/__init__.py

```python
"""Agent-Handoff - 项目级 AI 协作系统"""

__version__ = "0.1.0"
```

### src/agent_handoff/__main__.py

```python
"""
让 python -m agent_handoff.server 能工作
"""
if __name__ == "__main__":
    from agent_handoff.server import main
    import asyncio
    asyncio.run(main())
```

## 🎯 下一步开发任务

### 立即需要做的

- [ ] **测试基础功能**
  - 在真实项目中运行 `agent-handoff init`
  - 配置 VSCode，启动 MCP 服务器
  - 让 Copilot 调用 `start_work`

- [ ] **修复 bug**（如果有）
  - 路径处理在 Windows 上可能有问题
  - 编码问题（中文文件名）

- [ ] **改进错误提示**
  - 更友好的错误信息
  - 添加调试模式

### 短期计划（1-2 周）

- [ ] **完善 CLI**
  - `agent-handoff history` - 查看历史会话
  - `agent-handoff validate` - 检查文档结构

- [ ] **改进文档**
  - 录制演示视频
  - 编写故障排除指南
  - 多语言文档（中英文）

- [ ] **测试覆盖**
  - 单元测试
  - 集成测试
  - 端到端测试

### 中期计划（1-2 月）

- [ ] **语义搜索**
  - 集成 ChromaDB
  - 自动建立文档索引
  - 智能相关性搜索

- [ ] **交互式 init**
  - 问答式配置
  - 自动解析 PRD
  - 生成初始文档内容

- [ ] **VSCode 插件**
  - 可视化会话状态
  - 文档健康度面板
  - 一键启动/停止服务器

- [ ] **发布到 PyPI**
  - 完善打包配置
  - 编写发布流程
  - 设置 CI/CD

## 🐛 已知问题与限制

### MVP 阶段的限制

1. **单用户**
   - 同一时刻只有一个 Agent 可以工作
   - 多人协作需要手动协调（通过 Git）

2. **简单搜索**
   - 只支持关键词匹配
   - 无法理解同义词

3. **无状态恢复**
   - MCP 服务器重启 = 会话丢失
   - 需要 Agent 重新调用 start_work

4. **无可视化界面**
   - 所有操作通过 CLI 或 Agent 工具
   - 需要查看文件才能了解状态

### 潜在问题

1. **路径兼容性**
   ```python
   # 可能在 Windows 上有问题
   # 需要测试：
   # - 中文路径
   # - 包含空格的路径
   # - 符号链接
   ```

2. **编码问题**
   ```python
   # 所有文件假设 UTF-8 编码
   # 如果项目有其他编码的文件？
   ```

3. **大文件处理**
   ```python
   # 如果文档 > 1MB 怎么办？
   # 目前没有限制，可能导致性能问题
   ```

## 📚 参考资源

### MCP 协议

- [MCP 官方文档](https://modelcontextprotocol.io/)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [MCP 规范](https://spec.modelcontextprotocol.io/)

### 相关项目

- [Continue.dev](https://continue.dev/) - AI IDE 插件
- [Cursor Rules](https://cursor.directory/) - AI 指令模板
- [Mintlify](https://mintlify.com/) - 文档生成

### 社区

- [GitHub Discussions](https://github.com/yourusername/agent-handoff/discussions)
- [Discord Server](https://discord.gg/yourinvite)

## 🤝 贡献指南

### 报告 Bug

1. 检查是否已有相同问题
2. 创建 Issue，包含：
   - 环境信息（OS、Python 版本、IDE）
   - 重现步骤
   - 错误日志
   - 预期行为

### 提交功能建议

1. 先在 Discussions 讨论
2. 如果被认可，创建 Issue
3. 等待 maintainer 分配

### 提交代码

1. Fork 仓库
2. 创建功能分支：`git checkout -b feature/amazing-feature`
3. 提交代码：`git commit -m 'feat: add amazing feature'`
4. 推送分支：`git push origin feature/amazing-feature`
5. 创建 Pull Request

### 代码规范

```python
# 使用 Black 格式化
black src/

# 类型检查
mypy src/

# 测试
pytest tests/

# Commit 信息格式
# feat: 新功能
# fix: 修复 bug
# docs: 文档更新
# refactor: 重构
# test: 测试相关
# chore: 构建/工具相关
```

## 🎓 教程与示例

### 示例 1：为现有项目添加 Agent-Handoff

```bash
# 1. 进入项目
cd ~/projects/existing-app

# 2. 初始化
agent-handoff init

# 3. 填写关键文档
vim docs/01_Goals_and_Status/vision.md
vim docs/02_Architecture_and_Usage/architecture.md

# 4. 配置 IDE（见上文）

# 5. 开始使用
# 在 Copilot 中：调用 start_work，我要重构用户认证模块
```

### 示例 2：团队协作（通过 Git）

```bash
# 开发者 A
git pull
agent-handoff init  # 如果还没初始化

# Agent A 完成任务
# .agent-handoff/agentreadme.md 被更新

git add .agent-handoff/agentreadme.md docs/
git commit -m "docs: Agent A 完成用户认证功能"
git push

# 开发者 B
git pull  # 获取最新的 agentreadme.md

# Agent B 读取到 Agent A 的工作成果
# 继续下一个任务
```

### 示例 3：调试失败的任务

```
Agent: (执行任务时遇到错误)

Agent: (调用 report_issue)
{
  "session_id": "sess_xxx",
  "error_details": "API 调用失败：403 Forbidden"
}

MCP 返回:
{
  "instruction": "
    问题已记录。请按以下步骤调试：
    1. 将错误详情写入 docs/03_History_and_Lessons/bug_tracker.md
    2. 分析问题原因（可能是权限配置）
    3. 制定调试计划
    4. 调用 plan_setup 提交调试计划
  "
}

Agent: (调用 write_file 记录 bug)
Agent: (调用 plan_setup 提交新计划)
Agent: (继续调试...)
```

## ⚡ 性能优化建议

### 文档组织

```
✅ 好的实践：
docs/
├── 01_Goals/
│   ├── vision.md          (< 5KB)
│   ├── requirements.md    (< 10KB)
│   └── progress.md        (< 5KB)

❌ 避免：
docs/
└── everything.md          (> 100KB)
```

### 搜索优化

```python
# 如果文档很多（> 50 个），考虑：
# 1. 定期清理旧文档
# 2. 使用更精确的搜索关键词
# 3. 等待 v1.1 的语义搜索
```

## 🔐 安全考虑

### 敏感信息

```yaml
# .agent-handoff/config.yaml
# 不要在这里存储：
# ❌ API keys
# ❌ 密码
# ❌ 私有令牌

# 使用环境变量或其他安全方式
```

### 路径安全

```python
# MCP 服务器已实现路径检查
# Agent 只能访问 docs/ 目录
# 无法访问：
# - ../../../etc/passwd
# - /absolute/path
# - ~/user/home
```

### Git 安全

```bash
# 建议在 .gitignore 中添加：
.agent-handoff/history/*.json  # 如果包含敏感调试信息
```

## 📊 项目统计

```bash
# 代码行数
find src -name "*.py" | xargs wc -l

# 文档字数
find docs -name "*.md" | xargs wc -w

# 测试覆盖率
pytest --cov=agent_handoff tests/
```

## 🎉 致谢

感谢所有贡献者和早期用户！

特别感谢：
- Anthropic - MCP 协议
- Vibecoding 社区 - 灵感来源
- 早期测试者 - 宝贵反馈

---

## 快速链接

- 📖 [完整文档](https://agent-handoff.readthedocs.io/)
- 🐛 [报告问题](https://github.com/yourusername/agent-handoff/issues)
- 💬 [讨论](https://github.com/yourusername/agent-handoff/discussions)
- 🎓 [教程](https://agent-handoff.dev/tutorials)

---

**准备好了吗？**

```bash
pip install git+https://github.com/yourusername/agent-handoff.git
cd your-project
agent-handoff init
# 让 AI 协作变得规范、可追溯、高效！
```