#!/usr/bin/env python3
"""
使用 Claude Agent SDK 加载和使用 daily-tech-digest Skill

此脚本演示如何通过 Claude Agent SDK 来使用本地 Skills。

使用前提：
1. 需要安装 claude-agent-sdk
2. 需要将 Skill 文件放置在正确位置
3. 需要设置 ANTHROPIC_API_KEY

参考文档: https://docs.anthropic.com/en/docs/agent-sdk/skills
"""

import asyncio
import os
import shutil
from pathlib import Path

# 注意：claude_agent_sdk 可能需要单独安装
# pip install claude-agent-sdk
try:
    from claude_agent_sdk import query, ClaudeAgentOptions
except ImportError:
    print("错误: 请先安装 claude-agent-sdk")
    print("运行: pip install claude-agent-sdk")
    exit(1)


# 项目路径
PROJECT_ROOT = Path(__file__).parent.parent


def setup_skill_in_project():
    """
    将 Skill 设置到项目的 .claude/skills/ 目录
    这样 SDK 可以通过 setting_sources=["project"] 加载
    """
    skills_dir = PROJECT_ROOT / ".claude" / "skills" / "daily-tech-digest"
    skills_dir.mkdir(parents=True, exist_ok=True)

    # 复制 SKILL.md
    skill_md_src = PROJECT_ROOT / "SKILL.md"
    skill_md_dst = skills_dir / "SKILL.md"

    if skill_md_src.exists():
        shutil.copy(skill_md_src, skill_md_dst)
        print(f"[完成] Skill 已设置到: {skills_dir}")
    else:
        print(f"[错误] 找不到 SKILL.md: {skill_md_src}")
        return False

    # 复制 scripts 目录作为支持文件
    scripts_src = PROJECT_ROOT / "scripts"
    scripts_dst = skills_dir / "scripts"
    if scripts_src.exists():
        if scripts_dst.exists():
            shutil.rmtree(scripts_dst)
        shutil.copytree(scripts_src, scripts_dst)
        print(f"[完成] 脚本已复制到: {scripts_dst}")

    return True


def setup_skill_for_user():
    """
    将 Skill 设置到用户的 ~/.config/claude/skills/ 目录
    这样 SDK 可以通过 setting_sources=["user"] 加载
    """
    user_skills_dir = Path.home() / ".config" / "claude" / "skills" / "daily-tech-digest"
    user_skills_dir.mkdir(parents=True, exist_ok=True)

    # 复制 SKILL.md
    skill_md_src = PROJECT_ROOT / "SKILL.md"
    skill_md_dst = user_skills_dir / "SKILL.md"

    if skill_md_src.exists():
        shutil.copy(skill_md_src, skill_md_dst)
        print(f"[完成] Skill 已设置到用户目录: {user_skills_dir}")
    else:
        print(f"[错误] 找不到 SKILL.md: {skill_md_src}")
        return False

    return True


async def list_available_skills():
    """列出所有可用的 Skills"""
    print("\n[查询] 正在获取可用 Skills...")

    options = ClaudeAgentOptions(
        cwd=str(PROJECT_ROOT),
        setting_sources=["user", "project"],
        allowed_tools=["Skill"]
    )

    async for message in query(
        prompt="What skills are available? Please list them.",
        options=options
    ):
        if hasattr(message, 'content'):
            print(message.content)
        elif isinstance(message, str):
            print(message)


async def generate_digest_with_skill():
    """使用 Skill 生成科技简报"""
    print("\n[生成] 正在使用 Skill 生成科技简报...")

    options = ClaudeAgentOptions(
        cwd=str(PROJECT_ROOT),
        setting_sources=["user", "project"],
        allowed_tools=["Skill", "Read", "Write", "Bash", "Glob", "Grep"]
    )

    async for message in query(
        prompt="""请使用 daily-tech-digest Skill 生成今日科技简报。

具体步骤：
1. 运行 scripts/tech_digest.py 脚本
2. 检查生成的 digests/ 目录下的文件
3. 返回生成的简报内容摘要""",
        options=options
    ):
        if hasattr(message, 'content'):
            print(message.content)
        elif isinstance(message, str):
            print(message)


async def main():
    """主函数"""
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("错误: 请设置 ANTHROPIC_API_KEY 环境变量")
        return

    print("=" * 60)
    print("Claude Agent SDK - Skills 使用演示")
    print("=" * 60)

    # 1. 设置 Skill
    print("\n[1] 设置 Skill 到项目目录...")
    if not setup_skill_in_project():
        return

    # 2. 列出可用 Skills
    print("\n[2] 列出可用 Skills...")
    await list_available_skills()

    # 3. 使用 Skill 生成简报
    print("\n[3] 使用 Skill 生成简报...")
    await generate_digest_with_skill()

    print("\n" + "=" * 60)
    print("演示完成!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
