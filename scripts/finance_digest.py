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
            for entry in feed.entries[:8]:  # 每个源最多8条（降低国际源权重，提升国内内容占比）
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


def get_api_key() -> str:
    """获取API Key,兼容多种环境变量名称"""
    # 优先使用新的 AUTH_TOKEN,其次使用旧的 API_KEY
    api_key = os.environ.get("ANTHROPIC_AUTH_TOKEN") or os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("请设置 ANTHROPIC_AUTH_TOKEN 或 ANTHROPIC_API_KEY 环境变量")
    return api_key


def generate_digest_with_claude(content: str, config: dict, today: str) -> str:
    """使用 Claude/GLM 生成财经简报"""
    # API 配置
    api_key = get_api_key()

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

### 0. 内容比例要求（强制执行）
- **国内财经内容必须占比60%以上**
- 今日热点: 至少3条国内热点
- 市场动态: 必须包含A股,且放在首位
- 行业观察: 优先选择国内行业动态
- 投资洞察: 平衡国内外机构观点

### 1. 爆款选题筛选标准（优先级排序）

**第一优先级 - 普通人关心的爆款话题**:
- **财富效应**: 直接影响普通人钱包的(房产、股市、理财、就业、社保)
- **热点事件**: 具有传播性、争议性、话题性的事件
- **政策红利**: 新政策带来的机会或影响(降息、减税、补贴)
- **生活相关**: 消费、物价、工资、通胀等民生话题

**第二优先级 - 市场影响力**:
- **市场波动**: A股大跌大涨、热门板块轮动
- **龙头企业**: 腾讯、阿里、茅台、宁德时代等热门公司
- **新经济**: 电动车、AI、芯片、新能源、元宇宙

**第三优先级 - 国际重大事件**:
- 仅选择对国内市场有直接影响的国际新闻
- 避免纯国际政治新闻,除非涉及贸易、供应链

**剔除标准**:
- 纯国际政治新闻(除非涉及贸易、金融)
- 过于学术或专业的内容
- 普通人难以理解的专业术语
- 与国内市场无关的国际小众新闻

### 2. 板块结构（严格按以下顺序）

**🔥 今日热点（5条）**
- 从所有来源中筛选最重要、最受关注的5条
- 每条包含: 标题 + 链接 + **看点**（为什么重要 + 影响）
- 看点控制在50字内

**📈 市场动态（3-5条）**
- **必须包含A股**（放在首位），其次是港股、美股
- A股部分: 上证指数、深证成指、创业板指、热门板块
- 热门板块建议: 新能源、半导体、消费、医药、金融地产
- 大宗商品: 黄金、原油、铜、锂电池相关
- 每条包含: **数据 + 变化幅度 + 点评**
- 点评要说明对普通投资者的意义

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

**🎯 选题灵感（5-8条）**

针对财经博主的爆款选题推荐:

**内容策略**:
- **至少60%选题聚焦国内**
- **优先普通人感兴趣的话题**: 财富增值、避坑指南、政策红利
- **注重实用性和传播性**

**优先选题类型**:

1. **热点解读**（优先推荐）
   - 示例: "XX政策对你钱包的影响"
   - 理由: 时效性强,大众关注,容易出爆款
   - 切入点: 用大白话解读专业内容

2. **财富教育**
   - 示例: "小白理财的N个误区"
   - 理由: 实用性强,受众广
   - 切入点: 案例化教学,避免说教

3. **避坑指南**
   - 示例: "XX骗局最新套路"
   - 理由: 击中痛点,传播性强
   - 切入点: 真实案例+解决方案

4. **数据解读**
   - 示例: "从XX数据看投资机会"
   - 理由: 数据直观,有说服力
   - 切入点: 数据背后的趋势和机会

5. **行业分析**
   - 示例: "XX行业的黄金时代"
   - 理由: 专业深度,建立权威感
   - 切入点: 普通人能看懂的角度

**爆款特征**:
- ✅ 标题带有数字、疑问、对比
- ✅ 内容解决实际问题
- ✅ 语言通俗易懂,少用专业术语
- ✅ 有明确的行动建议

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

**标题风格**:
- 使用动词,增强画面感
- 加入数字,提高可信度
- 突出影响,引发共鸣

示例优化:
- ❌ "央行下调利率"
- ✅ "央行降息!你的房贷和存款会受什么影响?"

**内容风格**:
- 多用"你"、"普通人",拉近距离
- 少用专业术语,多用比喻
- 数据要配合解读,说明"意味着什么"
- 每条都要回答"跟我有什么关系"

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
