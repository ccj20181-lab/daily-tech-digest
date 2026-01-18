#!/usr/bin/env python3
"""
每日财经简报生成器
整合全球财经媒体 RSS 源，使用 Claude AI 生成简报
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


def fetch_rss_feeds(config: dict) -> list[dict]:
    """获取 RSS 源内容"""
    feeds_config = config["rss_feeds"]
    result = []

    def fetch_single_feed(name, feed_info):
        try:
            feed = feedparser.parse(feed_info["url"])
            items = []
            for entry in feed.entries[:15]:  # 每个源最多15条
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


def prepare_content_for_claude(rss: list) -> str:
    """准备发送给 Claude 的内容"""
    sections = []

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
            for item in items[:10]:  # 每分类最多10条
                cat_items.append(f"- [{item['title']}]({item['url']}) [{item['source']}]")
            sections.append(f"## {cat}\n" + "\n".join(cat_items))

    return "\n\n".join(sections)


def generate_digest_with_claude(content: str, config: dict, today: str) -> str:
    """使用 Claude/GLM 生成财经简报"""
    # API 配置
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("请设置 ANTHROPIC_API_KEY 环境变量")

    base_url = os.environ.get("ANTHROPIC_BASE_URL")

    # 如果设置了 base_url，则使用兼容 API（如智谱 BigModel）
    if base_url:
        client = anthropic.Anthropic(api_key=api_key, base_url=base_url)
    else:
        client = anthropic.Anthropic(api_key=api_key)

    # 财经简报专属 Prompt
    prompt = f"""你是一位资深财经编辑，需要根据以下原始内容生成一份精炼的中文财经简报。

今天日期: {today}

原始内容:
{content}

## 生成要求:

### 1. 热点筛选标准
优先选择符合以下特征的内容:
- **高影响力**: 影响股市、债市、商品市场或政策方向
- **大众关切**: 普通投资者和公众关心的话题
- **传播性强**: 具有话题性、争议性或突破性
- **时效性强**: 24小时内的最新动态

### 2. 板块结构（严格按以下顺序）

**🔥 今日热点（5条）**
- 从所有来源中筛选最重要、最受关注的5条
- 每条包含: 标题 + 链接 + **看点**（为什么重要 + 影响）
- 看点控制在50字内

**📈 市场动态（3-5条）**
- A股、港股、美股当日表现
- 重要指数、热门板块、大宗商品
- 每条包含: 数据 + **点评**

**💰 宏观与政策（3条）**
- 央行政策、财政政策、金融监管
- 每条包含: 政策内容 + **影响**

**🏢 行业观察（3条）**
- 特定行业动态、龙头企业、行业数据

**🌍 国际视野（2-3条）**
- 美联储、欧央行政策
- 国际大宗商品价格
- 全球经济数据

**💡 投资洞察（2条）**
- 知名机构或投资者观点
- 券商研报核心观点

**🎯 选题灵感（3-5条）**
为财经博主推荐选题方向:
- **选题类型**: "选题标题"
  - 理由: 为什么适合做内容
  - 切入点: 从哪个角度写更容易火

选题类型: 深度选题、热点解读、数据解读、投资教育、行业分析

**📚 延伸阅读（5条）**
- 深度分析文章
- 保留原始链接

### 3. 风险提示（必须包含）
```
⚠️ **风险提示**: 本简报仅供参考，不构成投资建议。市场有风险，投资需谨慎。
```

### 4. 语言风格
- 专业性与可读性平衡
- 简洁有力，每条控制在100字内
- 数据导向
- 中立客观

### 5. 格式要求
- 使用Markdown格式
- 导语50字以内
- 保留所有原始链接
- 总长度控制在2000字以内

直接输出简报内容，不需要额外说明。"""

    message = client.messages.create(
        model=config["claude"]["model"],
        max_tokens=config["claude"]["max_tokens"],
        temperature=config.get("claude", {}).get("temperature", 0.3),
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
    print("每日财经简报生成器")
    print("=" * 50)

    # 加载配置
    config = load_config()

    # 获取北京时间日期
    tz = pytz.timezone("Asia/Shanghai")
    today = datetime.now(tz).strftime(config["output"]["date_format"])
    print(f"\n日期: {today}")

    # 抓取数据
    print("\n[1/3] 正在抓取财经媒体 RSS 源...")
    rss = fetch_rss_feeds(config)
    print(f"      获取 {len(rss)} 条")

    # 检查是否有内容
    if not rss:
        print("\n[错误] 未获取到任何内容，退出")
        sys.exit(1)

    # 准备内容
    raw_content = prepare_content_for_claude(rss)

    # 生成简报
    print("[2/3] 正在使用 AI 生成财经简报...")
    digest = generate_digest_with_claude(raw_content, config, today)

    # 保存
    print("[3/3] 正在保存简报...")
    save_digest(digest, config, today)

    print("\n" + "=" * 50)
    print("生成完成!")
    print("=" * 50)


if __name__ == "__main__":
    main()
