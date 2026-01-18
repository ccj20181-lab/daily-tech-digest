#!/usr/bin/env python3
"""
HTML 索引页生成器
为简报归档生成一个美观的 HTML 索引页面
"""

import json
import re
from datetime import datetime
from pathlib import Path

import pytz


# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent
CONFIG_PATH = Path(__file__).parent / "config.json"


def load_config() -> dict:
    """加载配置文件"""
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def get_digest_files(digests_dir: Path) -> list[dict]:
    """获取所有简报文件信息"""
    files = []
    pattern = re.compile(r"^\d{4}-\d{2}-\d{2}\.md$")

    for file in digests_dir.glob("*.md"):
        if pattern.match(file.name):
            date_str = file.stem
            with open(file, "r", encoding="utf-8") as f:
                content = f.read()
                # 提取第一行作为标题
                first_line = content.split("\n")[0].strip("# ").strip()

            files.append({
                "date": date_str,
                "filename": file.name,
                "title": first_line or f"{date_str} 科技简报",
                "size": len(content)
            })

    # 按日期倒序排列
    files.sort(key=lambda x: x["date"], reverse=True)
    return files


def generate_html(files: list[dict], output_path: Path):
    """生成 HTML 索引页"""
    tz = pytz.timezone("Asia/Shanghai")
    now = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")

    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>每日科技简报归档</title>
    <style>
        :root {{
            --bg-color: #f5f5f5;
            --card-bg: #ffffff;
            --text-color: #333333;
            --accent-color: #2563eb;
            --border-color: #e5e5e5;
        }}

        @media (prefers-color-scheme: dark) {{
            :root {{
                --bg-color: #1a1a1a;
                --card-bg: #2d2d2d;
                --text-color: #e5e5e5;
                --accent-color: #60a5fa;
                --border-color: #404040;
            }}
        }}

        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            background-color: var(--bg-color);
            color: var(--text-color);
            line-height: 1.6;
            padding: 2rem;
        }}

        .container {{
            max-width: 800px;
            margin: 0 auto;
        }}

        header {{
            text-align: center;
            margin-bottom: 3rem;
        }}

        h1 {{
            font-size: 2rem;
            font-weight: 600;
            margin-bottom: 0.5rem;
        }}

        .subtitle {{
            color: #666;
            font-size: 0.9rem;
        }}

        .digest-list {{
            display: flex;
            flex-direction: column;
            gap: 1rem;
        }}

        .digest-item {{
            background: var(--card-bg);
            border: 1px solid var(--border-color);
            border-radius: 8px;
            padding: 1.25rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            transition: box-shadow 0.2s;
        }}

        .digest-item:hover {{
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        }}

        .digest-info {{
            flex: 1;
        }}

        .digest-date {{
            font-size: 0.85rem;
            color: var(--accent-color);
            font-weight: 500;
            margin-bottom: 0.25rem;
        }}

        .digest-title {{
            font-size: 1.1rem;
            font-weight: 500;
        }}

        .digest-link {{
            background: var(--accent-color);
            color: white;
            text-decoration: none;
            padding: 0.5rem 1rem;
            border-radius: 6px;
            font-size: 0.9rem;
            transition: opacity 0.2s;
        }}

        .digest-link:hover {{
            opacity: 0.9;
        }}

        .empty {{
            text-align: center;
            padding: 3rem;
            color: #666;
        }}

        footer {{
            text-align: center;
            margin-top: 3rem;
            padding-top: 1.5rem;
            border-top: 1px solid var(--border-color);
            font-size: 0.85rem;
            color: #666;
        }}

        footer a {{
            color: var(--accent-color);
            text-decoration: none;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>每日科技简报</h1>
            <p class="subtitle">整合 V2EX、Hacker News、科技媒体的每日精选</p>
        </header>

        <div class="digest-list">
"""

    if files:
        for item in files:
            html += f"""            <div class="digest-item">
                <div class="digest-info">
                    <div class="digest-date">{item['date']}</div>
                    <div class="digest-title">{item['title']}</div>
                </div>
                <a href="{item['filename']}" class="digest-link">阅读</a>
            </div>
"""
    else:
        html += """            <div class="empty">
                <p>暂无简报</p>
            </div>
"""

    html += f"""        </div>

        <footer>
            <p>最后更新: {now}</p>
            <p>由 Claude AI 驱动 · <a href="https://github.com">GitHub</a></p>
        </footer>
    </div>
</body>
</html>
"""

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"[完成] 已生成: {output_path}")


def main():
    """主函数"""
    print("=" * 50)
    print("HTML 索引页生成器")
    print("=" * 50)

    config = load_config()
    digests_dir = PROJECT_ROOT / config["output"]["digests_dir"]

    print(f"\n扫描目录: {digests_dir}")

    files = get_digest_files(digests_dir)
    print(f"找到 {len(files)} 份简报")

    output_path = digests_dir / "index.html"
    generate_html(files, output_path)

    print("\n" + "=" * 50)
    print("生成完成!")
    print("=" * 50)


if __name__ == "__main__":
    main()
