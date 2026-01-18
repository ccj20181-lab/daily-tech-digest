---
name: daily-tech-digest
description: 每日财经简报生成系统。整合全球财经媒体 RSS 源（华尔街日报、金融时报、CNBC 等），使用 Claude API 生成精炼的中文财经简报。当用户需要生成财经简报、抓取财经新闻、或自动化生成每日财经摘要时使用此 Skill。
---

# 每日财经简报生成系统

自动化的每日财经简报系统，整合全球顶级财经媒体内容，使用 Claude API 生成精炼的中文财经简报。

## 功能

1. **数据源抓取**
   - 华尔街日报 (WSJ)
   - 金融时报 (FT)
   - CNBC
   - 彭博社
   - 路透社
   - 其他财经媒体 RSS

2. **Claude 分析**
   - 筛选热点话题
   - 市场动态总结
   - 宏观政策解读
   - 产业趋势整理
   - 推荐阅读精选

3. **输出格式**
   - Markdown 简报文件
   - HTML 索引页面
   - 微信推送通知 (PushPlus)

## 使用方法

### 本地运行

```bash
cd ~/.claude/skills/daily-tech-digest

# 安装依赖
pip install -r requirements.txt

# 设置 API Key
export ANTHROPIC_API_KEY="your-api-key"

# 运行财经简报生成
python scripts/finance_digest.py

# 生成 HTML 索引
python scripts/generate_html.py
```

### 输出文件

- `digests/YYYY-MM-DD.md` - 日期简报
- `digests/latest.md` - 最新简报
- `digests/index.html` - HTML 索引页

## 文件结构

```
~/.claude/skills/daily-tech-digest/
├── scripts/
│   ├── finance_digest.py    # 财经简报主脚本
│   ├── financial_calendar.py # 财经日历
│   ├── send_pushplus.py     # 微信推送
│   ├── generate_html.py     # HTML 生成器
│   └── config.json          # RSS 源配置
├── digests/                  # 简报输出目录
├── .github/workflows/        # GitHub Actions
└── requirements.txt          # Python 依赖
```

## 配置

编辑 `scripts/config.json` 可自定义：
- RSS 源列表
- 抓取数量限制
- Claude 模型和参数
- 输出目录和日期格式

## 自动化

GitHub Actions 配置为每天北京时间 06:30 自动运行，需要在 GitHub Secrets 中配置：
- `ANTHROPIC_API_KEY` - Claude API 密钥 (智谱 AI)
- `PUSHPLUS_TOKEN` - 微信推送令牌 (可选)
