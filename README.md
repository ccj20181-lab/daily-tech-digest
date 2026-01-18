# 每日财经简报生成系统 - GitHub Actions 定时任务配置指南

## 📖 项目简介

这是一个基于 Claude Agent Skills 和 GitHub Actions 的自动化财经简报生成系统。它会每天定时抓取全球顶级财经媒体的热点内容，通过 AI 分析整理成结构化简报，并自动发布到 GitHub Pages 和微信推送。

### ✨ 核心特性

- ⏰ **全自动定时任务** - 每天自动运行，无需人工干预
- 🌐 **多源数据抓取** - 华尔街见闻、财新网、FT中文网、Bloomberg、路透社、CNBC 等
- 🤖 **AI 智能分析** - 使用智谱 GLM-4-Plus 模型自动筛选热点、提炼趋势
- 💰 **零成本运行** - GitHub Actions 个人使用完全免费
- 📱 **自动发布** - 生成 Markdown 和 HTML，支持 GitHub Pages 托管
- 💬 **微信推送** - 集成 PushPlus 自动推送到微信

---

## 🚀 快速开始

### 步骤 1: 准备 GitHub 仓库

1. **创建或使用现有仓库**
   ```bash
   # 在你的 GitHub 账号下创建一个新仓库
   # 例如: daily-finance-digest
   ```

2. **将 skill 文件复制到仓库**
   ```bash
   cp -r ~/.claude/skills/daily-tech-digest/* ~/Projects/daily-finance-digest/
   cd ~/Projects/daily-finance-digest
   ```

### 步骤 2: 配置 GitHub Secrets

在 GitHub 仓库中配置以下 Secrets：

1. **打开仓库设置**
   - 进入你的 GitHub 仓库
   - 点击 `Settings` > `Secrets and variables` > `Actions`
   - 点击 `New repository secret`

2. **添加以下 Secrets**:
   ```
   Name: ANTHROPIC_API_KEY
   Value: 你的智谱AI API Key

   Name: PUSHPLUS_TOKEN (可选)
   Value: 你的 PushPlus Token
   ```

### 步骤 3: 验证 GitHub Actions 配置

GitHub Actions 配置文件位于：
```
.github/workflows/daily-tech-digest.yml
```

配置说明：

```yaml
# 定时任务：每天北京时间 06:30 运行（UTC 前一天 22:30）
schedule:
  - cron: '30 22 * * *'

# 支持手动触发（用于测试）
workflow_dispatch: true
```

### 步骤 4: 测试运行

**方式1: 手动触发（推荐）**
1. 进入 `Actions` 标签页
2. 选择 `每日财经简报生成器` 工作流
3. 点击 `Run workflow` > `Run workflow`

**方式2: 等待定时触发**
- 系统会在每天北京时间 06:30 自动运行

---

## 📊 数据源配置

当前配置的财经媒体 RSS 源：

| 媒体 | 分类 | 覆盖内容 |
|------|------|----------|
| 华尔街见闻 | 市场动态 | A股、港股、美股实时资讯 |
| 财新网 | 深度分析 | 财经深度调查和评论 |
| 第一财经 | 综合财经 | 宏观、产业、公司新闻 |
| FT中文网 | 市场分析 | 国际市场、中国经济 |
| 央行政策 | 政策公告 | 货币政策、监管动态 |
| Bloomberg | 国际财经 | 全球市场、经济数据 |
| 路透社 | 国际新闻 | 突发财经新闻 |
| CNBC | 美股聚焦 | 美股市场、科技股 |

---

## 📱 微信推送配置（可选）

### 获取 PushPlus Token

1. 访问 [PushPlus官网](https://www.pushplus.plus/)
2. 微信扫码登录
3. 复制你的 Token
4. 添加到 GitHub Secrets: `PUSHPLUS_TOKEN`

---

## 🌐 配置 GitHub Pages（可选）

如果想在线查看生成的简报：

### 步骤 1: 启用 GitHub Pages

1. 进入仓库 `Settings` > `Pages`
2. Source 选择:
   - **Source**: Deploy from a branch
   - **Branch**: `main` / `root`
3. 点击 `Save`

### 步骤 2: 访问在线页面

```
https://你的用户名.github.io/仓库名/digests/
```

---

## 💰 费用说明

### GitHub Actions
- ✅ **个人账户**：每月 2000 分钟免费
- ✅ **公共仓库**：完全免费
- 本次任务每次运行约 2-3 分钟

### 智谱 AI API
- GLM-4-Plus 模型经济实惠
- 每次生成简报约消耗 3000-5000 tokens
- 智谱新用户通常有免费额度
- 即使付费，成本极低（¥0.05/次以内）

---

## 📈 输出文件

- `digests/YYYY-MM-DD.md` - 按日期归档的简报
- `digests/latest.md` - 最新简报
- `digests/index.html` - HTML 索引页面

简报内容结构：
- 🔥 今日热点
- 📈 市场动态
- 💰 宏观与政策
- 🏢 产业要闻
- 📊 数据日历

---

**创建时间**: 2026-01-18
**维护者**: Henry
**许可证**: MIT
