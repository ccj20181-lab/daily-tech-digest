#!/usr/bin/env python3
"""
PushPlus 微信推送通知
将每日简报推送到微信
"""

import os
import sys
import requests
from datetime import datetime
import pytz


def send_pushplus_notification(token: str, title: str, content: str, digest_url: str):
    """
    发送 PushPlus 通知

    Args:
        token: PushPlus Token
        title: 消息标题
        content: 消息内容
        digest_url: 简报URL
    """
    # 构建完整消息（使用HTML格式）
    full_content = f"""
{content}

<br>
<hr>
<h3>📱 快速访问</h3>
<p>
🔗 <b><a href="{digest_url}">点击查看完整简报</a></b><br>
📚 <a href="{digest_url.replace('latest.md', '')}">查看历史归档</a><br>
🌐 <a href="https://github.com/ccj20181-lab/daily-tech-digest">GitHub 仓库</a>
</p>
<hr>
<p style="color: #999; font-size: 12px;">
🤖 由 Claude AI + 智谱 GLM-4.7 自动生成<br>
⏰ 生成时间: {datetime.now(pytz.timezone('Asia/Shanghai')).strftime('%Y-%m-%d %H:%M:%S')}
</p>
"""

    # PushPlus API
    url = f"http://www.pushplus.plus/send/{token}"

    payload = {
        "title": title,
        "content": full_content,
        "template": "html"  # 使用 HTML 模板支持链接
    }

    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        result = response.json()

        if result.get("code") == 200:
            print(f"[成功] 微信推送已发送")
            return True
        else:
            print(f"[失败] {result.get('msg', '未知错误')}")
            return False

    except Exception as e:
        print(f"[错误] 推送失败: {e}")
        return False


def main():
    """主函数"""
    # 从环境变量获取配置
    token = os.environ.get("PUSHPLUS_TOKEN")
    if not token:
        print("[错误] 请设置 PUSHPLUS_TOKEN 环境变量")
        sys.exit(1)

    # 简报URL（从 GitHub Actions 环境变量获取）
    github_repo = os.environ.get("GITHUB_REPOSITORY", "ccj20181-lab/daily-tech-digest")
    run_id = os.environ.get("GITHUB_RUN_ID", "")

    digest_url = f"https://github.com/{github_repo}/actions/runs/{run_id}"
    web_url = f"https://{github_repo.replace('/', '.github.io/')}/digests/latest.md"

    # 读取最新的简报内容
    digest_file = os.environ.get("DIGEST_FILE", "digests/latest.md")

    try:
        with open(digest_file, "r", encoding="utf-8") as f:
            content = f.read()

        # 提取前800字符作为摘要（更适合HTML展示）
        if len(content) > 800:
            summary = content[:800].replace("\n", "<br>") + "..."
        else:
            summary = content.replace("\n", "<br>")

        # 添加HTML换行
        summary = "<p>" + summary + "</p>"

        # 构建标题
        tz = pytz.timezone("Asia/Shanghai")
        today = datetime.now(tz).strftime("%Y-%m-%d")
        title = f"📊 每日科技简报 {today}"

        # 发送通知
        success = send_pushplus_notification(
            token=token,
            title=title,
            content=summary,
            digest_url=web_url
        )

        sys.exit(0 if success else 1)

    except FileNotFoundError:
        print(f"[错误] 找不到简报文件: {digest_file}")
        sys.exit(1)
    except Exception as e:
        print(f"[错误] {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
