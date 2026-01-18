#!/usr/bin/env python3
"""
使用 Anthropic Skills API 加载和使用 daily-tech-digest Skill

此脚本演示如何通过 Anthropic API 的 Skills 功能来使用本项目作为一个 Skill。

使用前提：
1. 需要 Anthropic API Key
2. 需要启用 code-execution 和 skills beta 功能

参考文档: https://docs.anthropic.com/en/docs/agents-and-tools/agent-skills/api-integration
"""

import os
from pathlib import Path

import anthropic
from anthropic.lib import files_from_dir


def create_skill(client: anthropic.Anthropic, skill_dir: Path) -> dict:
    """
    创建或更新 Skill

    Args:
        client: Anthropic 客户端
        skill_dir: Skill 目录路径

    Returns:
        创建的 Skill 信息
    """
    skill = client.beta.skills.create(
        display_title="每日科技简报生成器",
        files=files_from_dir(str(skill_dir)),
        betas=["skills-2025-10-02"]
    )
    print(f"[完成] 创建 Skill: {skill.id}")
    print(f"       版本: {skill.latest_version}")
    return skill


def list_skills(client: anthropic.Anthropic) -> list:
    """列出所有可用的 Skills"""
    skills = client.beta.skills.list(
        source="custom",
        betas=["skills-2025-10-02"]
    )
    return skills.data


def use_skill_to_generate_digest(
    client: anthropic.Anthropic,
    skill_id: str,
    skill_version: str = "latest"
) -> str:
    """
    使用 Skill 生成科技简报

    Args:
        client: Anthropic 客户端
        skill_id: Skill ID
        skill_version: Skill 版本

    Returns:
        生成的简报内容
    """
    response = client.beta.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=4096,
        betas=["code-execution-2025-08-25", "skills-2025-10-02"],
        container={
            "skills": [
                {
                    "type": "custom",
                    "skill_id": skill_id,
                    "version": skill_version
                }
            ]
        },
        messages=[{
            "role": "user",
            "content": "请使用 daily-tech-digest Skill 生成今日科技简报。"
                       "请抓取 V2EX、Hacker News 和 RSS 源的内容，然后生成一份精炼的中文简报。"
        }],
        tools=[{
            "type": "code_execution_20250825",
            "name": "code_execution"
        }]
    )

    # 处理可能的 pause_turn
    max_retries = 10
    messages = [{"role": "user", "content": "请使用 daily-tech-digest Skill 生成今日科技简报。"}]

    for _ in range(max_retries):
        if response.stop_reason != "pause_turn":
            break

        messages.append({"role": "assistant", "content": response.content})
        response = client.beta.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=4096,
            betas=["code-execution-2025-08-25", "skills-2025-10-02"],
            container={
                "id": response.container.id,
                "skills": [
                    {
                        "type": "custom",
                        "skill_id": skill_id,
                        "version": skill_version
                    }
                ]
            },
            messages=messages,
            tools=[{
                "type": "code_execution_20250825",
                "name": "code_execution"
            }]
        )

    # 提取文本内容
    result = ""
    for item in response.content:
        if hasattr(item, "text"):
            result += item.text

    return result


def delete_skill(client: anthropic.Anthropic, skill_id: str):
    """删除 Skill 及其所有版本"""
    # 先删除所有版本
    versions = client.beta.skills.versions.list(
        skill_id=skill_id,
        betas=["skills-2025-10-02"]
    )

    for version in versions.data:
        client.beta.skills.versions.delete(
            skill_id=skill_id,
            version=version.version,
            betas=["skills-2025-10-02"]
        )
        print(f"[完成] 删除版本: {version.version}")

    # 再删除 Skill
    client.beta.skills.delete(
        skill_id=skill_id,
        betas=["skills-2025-10-02"]
    )
    print(f"[完成] 删除 Skill: {skill_id}")


def main():
    """演示 Skills API 使用"""
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("错误: 请设置 ANTHROPIC_API_KEY 环境变量")
        return

    client = anthropic.Anthropic(api_key=api_key)
    project_root = Path(__file__).parent.parent

    print("=" * 60)
    print("Anthropic Skills API 演示")
    print("=" * 60)

    # 1. 创建 Skill
    print("\n[1] 创建 Skill...")
    skill = create_skill(client, project_root)

    # 2. 列出 Skills
    print("\n[2] 列出所有自定义 Skills...")
    skills = list_skills(client)
    for s in skills:
        print(f"    - {s.id}: {s.display_title}")

    # 3. 使用 Skill 生成简报
    print("\n[3] 使用 Skill 生成简报...")
    digest = use_skill_to_generate_digest(client, skill.id)
    print("\n生成的简报:")
    print("-" * 40)
    print(digest[:1000] + "..." if len(digest) > 1000 else digest)

    # 4. 清理（可选）
    # print("\n[4] 清理 Skill...")
    # delete_skill(client, skill.id)

    print("\n" + "=" * 60)
    print("演示完成!")
    print("=" * 60)


if __name__ == "__main__":
    main()
