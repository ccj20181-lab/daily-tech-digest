#!/usr/bin/env python3
"""
使用 Claude Agent SDK 加载 daily-tech-digest Skill 生成科技简报

这是完全通过 Agent Skills 方式运行的版本。
Claude 会自动发现并调用 .claude/skills/daily-tech-digest/ 中的 Skill。

注意：claude-agent-sdk 底层调用 Claude Code CLI，需要：
- 原生 Anthropic API Key（设置 ANTHROPIC_API_KEY）
- 或者通过 ANTHROPIC_BASE_URL 使用兼容 API（如智谱 BigModel）
"""

import asyncio
import os
from pathlib import Path

from claude_agent_sdk import query, ClaudeAgentOptions


# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent


async def run_with_skill():
    """使用 Agent SDK 加载 Skill 并生成简报"""

    print("=" * 60)
    print("Claude Agent SDK - Skills 方式生成科技简报")
    print("=" * 60)

    # 检查 API Key
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("\n[错误] 请设置 ANTHROPIC_API_KEY 环境变量")
        return

    # 检查 Skill 文件是否存在
    skill_path = PROJECT_ROOT / ".claude" / "skills" / "daily-tech-digest" / "SKILL.md"
    if not skill_path.exists():
        print(f"\n[错误] Skill 文件不存在: {skill_path}")
        return

    print(f"\n[配置]")
    print(f"  项目目录: {PROJECT_ROOT}")
    print(f"  Skill 路径: {skill_path}")

    # 检查是否使用智谱 BigModel 兼容 API
    base_url = os.environ.get("ANTHROPIC_BASE_URL", "")
    if base_url:
        print(f"  API 端点: {base_url}")

    # 配置 SDK 选项
    # - cwd: 项目目录（包含 .claude/skills/）
    # - setting_sources: 从项目目录加载 Skills
    # - allowed_tools: 启用 Skill 工具和其他必要工具
    # - env: 传递环境变量（包括可能的 ANTHROPIC_BASE_URL）
    env_vars = {
        "ANTHROPIC_API_KEY": api_key,
    }
    if base_url:
        env_vars["ANTHROPIC_BASE_URL"] = base_url

    options = ClaudeAgentOptions(
        cwd=str(PROJECT_ROOT),
        setting_sources=["project"],  # 从项目目录加载 Skills
        allowed_tools=["Skill", "Read", "Write", "Bash", "Glob", "Grep"],
        env=env_vars,
        permission_mode="bypassPermissions",  # 自动批准工具使用
    )

    print(f"\n[1/2] 查询可用的 Skills...")

    # 先列出可用的 Skills
    try:
        async for message in query(
            prompt="What Skills are available? Please list them briefly.",
            options=options
        ):
            if hasattr(message, 'content'):
                for block in message.content:
                    if hasattr(block, 'text'):
                        print(f"  {block.text}")
            elif isinstance(message, str):
                print(f"  {message}")
    except Exception as e:
        print(f"  [错误] {e}")
        return

    print(f"\n[2/2] 使用 Skill 生成科技简报...")

    # 使用 Skill 生成简报
    prompt = """请使用 daily-tech-digest Skill 生成今日科技简报。

具体要求：
1. 运行项目中的 scripts/tech_digest.py 脚本来抓取数据并生成简报
2. 脚本会自动从 V2EX、Hacker News 和 RSS 源抓取内容
3. 使用 AI 生成精炼的中文简报
4. 简报会保存到 digests/ 目录

请开始执行。"""

    try:
        async for message in query(
            prompt=prompt,
            options=options
        ):
            if hasattr(message, 'content'):
                for block in message.content:
                    if hasattr(block, 'text'):
                        print(block.text)
            elif hasattr(message, 'type'):
                if message.type == 'text':
                    print(message.text if hasattr(message, 'text') else str(message))
                elif message.type == 'tool_use':
                    print(f"[工具调用] {message.name if hasattr(message, 'name') else 'unknown'}")
            elif isinstance(message, str):
                print(message)
    except Exception as e:
        print(f"[错误] {e}")

    print("\n" + "=" * 60)
    print("完成!")
    print("=" * 60)


async def main():
    """主函数"""
    await run_with_skill()


if __name__ == "__main__":
    asyncio.run(main())
