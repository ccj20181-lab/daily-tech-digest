#!/usr/bin/env python3
"""
增强版科技简报生成器
添加趋势分析、历史对比等高级功能
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path

import anthropic
import pytz

from tech_digest import (
    PROJECT_ROOT,
    load_config,
    fetch_v2ex_hot,
    fetch_hn_top,
    fetch_rss_feeds,
    prepare_content_for_claude,
    save_digest,
)


def load_recent_digests(config: dict, days: int = 7) -> list[str]:
    """加载最近几天的简报内容"""
    digests_dir = PROJECT_ROOT / config["output"]["digests_dir"]
    tz = pytz.timezone("Asia/Shanghai")
    today = datetime.now(tz)

    contents = []
    for i in range(1, days + 1):
        date = today - timedelta(days=i)
        date_str = date.strftime(config["output"]["date_format"])
        file_path = digests_dir / f"{date_str}.md"
        if file_path.exists():
            with open(file_path, "r", encoding="utf-8") as f:
                contents.append(f"### {date_str}\n{f.read()}")

    return contents


def analyze_trends_with_claude(
    current_content: str,
    historical_content: list[str],
    config: dict,
    today: str
) -> str:
    """使用 Claude 进行趋势分析"""
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("请设置 ANTHROPIC_API_KEY 环境变量")

    client = anthropic.Anthropic(api_key=api_key)

    historical_text = "\n\n---\n\n".join(historical_content) if historical_content else "无历史数据"

    prompt = f"""你是一位资深科技分析师，需要根据今日内容和历史简报进行深度分析。

今天日期: {today}

## 今日原始内容:
{current_content}

## 过去一周的简报摘要:
{historical_text}

请生成一份增强版科技简报，包含以下板块:

1. **今日热点** (3-5条): 最值得关注的话题
2. **技术趋势** (2-3条): 技术领域动态
3. **产品观察** (2-3条): 新产品、设计洞察
4. **推荐阅读** (3-5条): 精选深度文章

5. **本周趋势洞察** (如果有历史数据):
   - 识别本周反复出现的热点话题
   - 分析技术趋势的演变
   - 预测未来可能的发展方向

格式要求:
- 使用 Markdown 格式
- 开头添加日期和简短导语
- 保留原始链接
- 语言简洁有力
- 趋势分析部分要有洞察深度

直接输出简报内容。"""

    message = client.messages.create(
        model=config["claude"]["model"],
        max_tokens=config["claude"]["max_tokens"] + 1024,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    return message.content[0].text


def main():
    """主函数 - 增强版"""
    print("=" * 50)
    print("每日科技简报生成器 (增强版)")
    print("=" * 50)

    # 加载配置
    config = load_config()

    # 获取北京时间日期
    tz = pytz.timezone("Asia/Shanghai")
    today = datetime.now(tz).strftime(config["output"]["date_format"])
    print(f"\n日期: {today}")

    # 抓取数据
    print("\n[1/5] 正在抓取 V2EX 热门...")
    v2ex = fetch_v2ex_hot(config)
    print(f"      获取 {len(v2ex)} 条")

    print("[2/5] 正在抓取 Hacker News...")
    hn = fetch_hn_top(config)
    print(f"      获取 {len(hn)} 条")

    print("[3/5] 正在抓取 RSS 源...")
    rss = fetch_rss_feeds(config)
    print(f"      获取 {len(rss)} 条")

    # 加载历史数据
    print("[4/5] 正在加载历史简报...")
    historical = load_recent_digests(config, days=7)
    print(f"      找到 {len(historical)} 份历史简报")

    # 准备内容
    raw_content = prepare_content_for_claude(v2ex, hn, rss)

    # 生成增强版简报
    print("[5/5] 正在使用 Claude 生成增强版简报...")
    digest = analyze_trends_with_claude(raw_content, historical, config, today)

    # 保存
    save_digest(digest, config, today)

    print("\n" + "=" * 50)
    print("增强版生成完成!")
    print("=" * 50)


if __name__ == "__main__":
    main()
