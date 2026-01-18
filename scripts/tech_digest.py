#!/usr/bin/env python3
"""
每日科技简报生成器
整合 V2EX、Hacker News、RSS 源，使用 Claude 生成简报
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

import anthropic
import feedparser
import pytz
import requests
from bs4 import BeautifulSoup


# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent
CONFIG_PATH = Path(__file__).parent / "config.json"


def load_config() -> dict:
    """加载配置文件"""
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def fetch_v2ex_hot(config: dict) -> list[dict]:
    """获取 V2EX 热门话题"""
    try:
        url = config["v2ex"]["hot_url"]
        headers = {"User-Agent": "TechDigest/1.0"}
        resp = requests.get(url, headers=headers, timeout=15)
        resp.raise_for_status()
        topics = resp.json()

        result = []
        for topic in topics[:config["v2ex"]["max_topics"]]:
            result.append({
                "title": topic.get("title", ""),
                "url": f"https://www.v2ex.com/t/{topic.get('id', '')}",
                "node": topic.get("node", {}).get("title", ""),
                "replies": topic.get("replies", 0),
                "source": "V2EX"
            })
        return result
    except Exception as e:
        print(f"[警告] V2EX 抓取失败: {e}")
        return []


def fetch_hn_top(config: dict) -> list[dict]:
    """获取 Hacker News 热门"""
    try:
        top_url = config["hackernews"]["top_url"]
        item_url_template = config["hackernews"]["item_url"]
        max_items = config["hackernews"]["max_items"]

        resp = requests.get(top_url, timeout=15)
        resp.raise_for_status()
        story_ids = resp.json()[:max_items]

        result = []

        def fetch_item(story_id):
            try:
                item_resp = requests.get(
                    item_url_template.format(story_id),
                    timeout=10
                )
                item_resp.raise_for_status()
                return item_resp.json()
            except Exception:
                return None

        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = {executor.submit(fetch_item, sid): sid for sid in story_ids}
            for future in as_completed(futures):
                item = future.result()
                if item and item.get("title"):
                    result.append({
                        "title": item.get("title", ""),
                        "url": item.get("url", f"https://news.ycombinator.com/item?id={item.get('id')}"),
                        "score": item.get("score", 0),
                        "comments": item.get("descendants", 0),
                        "source": "Hacker News"
                    })

        # 按分数排序
        result.sort(key=lambda x: x.get("score", 0), reverse=True)
        return result
    except Exception as e:
        print(f"[警告] Hacker News 抓取失败: {e}")
        return []


def fetch_rss_feeds(config: dict) -> list[dict]:
    """获取 RSS 源内容"""
    feeds_config = config["rss_feeds"]
    result = []

    def fetch_single_feed(name, feed_info):
        try:
            feed = feedparser.parse(feed_info["url"])
            items = []
            for entry in feed.entries[:10]:
                items.append({
                    "title": entry.get("title", ""),
                    "url": entry.get("link", ""),
                    "published": entry.get("published", ""),
                    "summary": BeautifulSoup(
                        entry.get("summary", "")[:300], "html.parser"
                    ).get_text()[:200],
                    "source": feed_info["name"],
                    "category": feed_info["category"]
                })
            return items
        except Exception as e:
            print(f"[警告] RSS {name} 抓取失败: {e}")
            return []

    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {
            executor.submit(fetch_single_feed, name, info): name
            for name, info in feeds_config.items()
        }
        for future in as_completed(futures):
            items = future.result()
            result.extend(items)

    return result


def prepare_content_for_claude(v2ex: list, hn: list, rss: list) -> str:
    """准备发送给 Claude 的内容"""
    sections = []

    # V2EX 部分
    if v2ex:
        v2ex_items = []
        for item in v2ex:
            v2ex_items.append(f"- [{item['title']}]({item['url']}) [节点: {item['node']}, 回复: {item['replies']}]")
        sections.append("## V2EX 热门话题\n" + "\n".join(v2ex_items))

    # Hacker News 部分
    if hn:
        hn_items = []
        for item in hn:
            hn_items.append(f"- [{item['title']}]({item['url']}) [得分: {item['score']}, 评论: {item['comments']}]")
        sections.append("## Hacker News 热门\n" + "\n".join(hn_items))

    # RSS 部分 - 按分类分组
    if rss:
        by_category = {}
        for item in rss:
            cat = item.get("category", "其他")
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append(item)

        for cat, items in by_category.items():
            cat_items = []
            for item in items[:8]:  # 每分类最多8条
                cat_items.append(f"- [{item['title']}]({item['url']}) [{item['source']}]")
            sections.append(f"## {cat}\n" + "\n".join(cat_items))

    return "\n\n".join(sections)


def generate_digest_with_claude(content: str, config: dict, today: str) -> str:
    """使用 Claude/GLM 生成简报"""
    # API 配置
    # 注意：请通过环境变量设置 API Key，不要硬编码
    # 示例：export ANTHROPIC_API_KEY="your-api-key-here"
    # 智谱 BigModel 兼容 API 示例：
    #   export ANTHROPIC_API_KEY="your-key"
    #   export ANTHROPIC_BASE_URL="https://open.bigmodel.cn/api/anthropic"

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("请设置 ANTHROPIC_API_KEY 环境变量")

    base_url = os.environ.get("ANTHROPIC_BASE_URL")

    # 如果设置了 base_url，则使用兼容 API（如智谱 BigModel）
    if base_url:
        client = anthropic.Anthropic(api_key=api_key, base_url=base_url)
    else:
        client = anthropic.Anthropic(api_key=api_key)

    prompt = f"""你是一位资深科技编辑，需要根据以下原始内容生成一份精炼的中文科技简报。

今天日期: {today}

原始内容:
{content}

请生成一份结构清晰的科技简报，包含以下板块:

1. **今日热点** (3-5条): 从 V2EX 和 Hacker News 中筛选最值得关注的话题，简要说明为什么重要
2. **技术趋势** (2-3条): 识别技术领域的趋势动态（AI、云计算、编程语言、开发工具等）
3. **产品观察** (2-3条): 有趣的新产品、产品设计洞察
4. **推荐阅读** (3-5条): 精选值得深入阅读的文章，保留原始链接

格式要求:
- 使用 Markdown 格式
- 开头添加日期和简短导语
- 每条内容保留原始链接
- 语言简洁有力，避免冗长
- 总长度控制在 1500 字以内

直接输出简报内容，不需要额外说明。"""

    message = client.messages.create(
        model=config["claude"]["model"],
        max_tokens=config["claude"]["max_tokens"],
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    return message.content[0].text


def save_digest(content: str, config: dict, today: str):
    """保存简报文件"""
    digests_dir = PROJECT_ROOT / config["output"]["digests_dir"]
    digests_dir.mkdir(exist_ok=True)

    # 保存日期文件
    date_file = digests_dir / f"{today}.md"
    with open(date_file, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"[完成] 已保存: {date_file}")

    # 更新 latest.md
    latest_file = digests_dir / "latest.md"
    with open(latest_file, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"[完成] 已更新: {latest_file}")


def main():
    """主函数"""
    print("=" * 50)
    print("每日科技简报生成器")
    print("=" * 50)

    # 加载配置
    config = load_config()

    # 获取北京时间日期
    tz = pytz.timezone("Asia/Shanghai")
    today = datetime.now(tz).strftime(config["output"]["date_format"])
    print(f"\n日期: {today}")

    # 抓取数据
    print("\n[1/4] 正在抓取 V2EX 热门...")
    v2ex = fetch_v2ex_hot(config)
    print(f"      获取 {len(v2ex)} 条")

    print("[2/4] 正在抓取 Hacker News...")
    hn = fetch_hn_top(config)
    print(f"      获取 {len(hn)} 条")

    print("[3/4] 正在抓取 RSS 源...")
    rss = fetch_rss_feeds(config)
    print(f"      获取 {len(rss)} 条")

    # 检查是否有内容
    if not v2ex and not hn and not rss:
        print("\n[错误] 未获取到任何内容，退出")
        sys.exit(1)

    # 准备内容
    raw_content = prepare_content_for_claude(v2ex, hn, rss)

    # 生成简报
    print("[4/4] 正在使用 Claude 生成简报...")
    digest = generate_digest_with_claude(raw_content, config, today)

    # 保存
    save_digest(digest, config, today)

    print("\n" + "=" * 50)
    print("生成完成!")
    print("=" * 50)


if __name__ == "__main__":
    main()
