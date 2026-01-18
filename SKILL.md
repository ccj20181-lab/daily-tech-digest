---
name: daily-tech-digest
description: 每日科技简报生成系统。整合 V2EX 热帖、Hacker News 和科技新闻 RSS 源，使用 Claude API 生成精炼的中文简报。当用户需要生成科技简报、抓取技术新闻、或自动化生成每日摘要时使用此 Skill。
---

# 每日科技简报生成系统

自动化的每日科技简报系统，整合多个技术社区和科技媒体内容，使用 Claude API 生成精炼的中文简报。

## 功能

1. **数据源抓取**
   - V2EX 热帖 API
   - Hacker News Firebase API
   - 多个科技媒体 RSS (36氪、少数派、虎嗅、InfoQ 等)

2. **Claude 分析**
   - 筛选热点话题
   - 技术趋势总结
   - 社区讨论提炼
   - 产业动态整理
   - 推荐阅读精选

3. **输出格式**
   - Markdown 简报文件
   - HTML 索引页面

## 使用方法

### 本地运行

```bash
cd /Users/pan/cron

# 安装依赖
pip install -r requirements.txt

# 设置 API Key
export ANTHROPIC_API_KEY="your-api-key"

# 运行标准版
python scripts/tech_digest.py

# 运行增强版（含趋势分析）
python scripts/advanced_digest.py

# 生成 HTML 索引
python scripts/generate_html.py
```

### 输出文件

- `digests/YYYY-MM-DD.md` - 日期简报
- `digests/latest.md` - 最新简报
- `digests/index.html` - HTML 索引页

## 文件结构

```
/Users/pan/cron/
├── scripts/
│   ├── tech_digest.py       # 主脚本
│   ├── advanced_digest.py   # 增强版（趋势分析）
│   ├── generate_html.py     # HTML 生成器
│   └── config.json          # RSS 源配置
├── digests/                  # 简报输出目录
├── .github/workflows/        # GitHub Actions
└── requirements.txt          # Python 依赖
```

## 配置

编辑 `scripts/config.json` 可自定义：
- RSS 源列表
- V2EX/HN 抓取数量
- Claude 模型和参数
- 输出目录和日期格式

## 自动化

GitHub Actions 配置为每天北京时间 6:00 自动运行，需要在 GitHub Secrets 中配置：
- `ANTHROPIC_API_KEY` - Claude API 密钥
