#!/usr/bin/env python3
"""
生成 GitHub Pages 友好的 HTML 页面
完整展示 Markdown 内容，带样式和导航
"""

import json
import re
from datetime import datetime
from pathlib import Path

import pytz

try:
    import markdown
except ImportError:
    print("警告: 需要安装 markdown")
    print("运行: pip install markdown")
    exit(1)


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
                # 提取标题
                title_match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
                title = title_match.group(1) if title_match else f"{date_str} 科技简报"

            files.append({
                "date": date_str,
                "filename": file.name,
                "title": title,
                "content": content
            })

    # 按日期倒序排列
    files.sort(key=lambda x: x["date"], reverse=True)
    return files


def markdown_to_html(md_content: str) -> str:
    """将 Markdown 转换为 HTML"""
    md = markdown.Markdown(
        extensions=[
            'extra',
            'codehilite',
            'toc',
            'tables',
            'fenced_code',
            'nl2br',
            'sane_lists'
        ],
        extension_configs={
            'codehilite': {
                'linenums': False,
                'css_class': 'highlight'
            }
        }
    )
    return md.convert(md_content)


def generate_page(files: list[dict], output_path: Path):
    """生成完整的 HTML 页面"""
    tz = pytz.timezone("Asia/Shanghai")
    now = datetime.now(tz).strftime("%Y年%m月%d日")

    # 为每个文件生成 HTML
    digest_htmls = []
    for item in files[:10]:  # 最多显示 10 份
        content_html = markdown_to_html(item["content"])
        digest_htmls.append(f"""
        <article class="digest-item" data-date="{item['date']}">
            <div class="digest-header">
                <div class="digest-icon">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"/>
                        <polyline points="14 2 14 8 20 8"/>
                        <line x1="16" y1="13" x2="8" y2="13"/>
                        <line x1="16" y1="17" x2="8" y2="17"/>
                        <line x1="10" y1="9" x2="8" y2="9"/>
                    </svg>
                </div>
                <div>
                    <h2 class="digest-title">{item['title']}</h2>
                    <span class="digest-date">{item['date']}</span>
                </div>
            </div>
            <div class="digest-content">
                {content_html}
            </div>
        </article>
        """)

    digests_section = "\n".join(digest_htmls) if files else '<p class="empty">暂无简报</p>'

    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>每日科技简报 | Daily Tech Digest</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Noto+Sans+SC:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        *, *::before, *::after {{
                       box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}

        :root {{
            --bg-primary: #0a0a0b;
            --bg-secondary: #111113;
            --bg-tertiary: #18181b;
            --bg-hover: #1f1f23;
            --border: #27272a;
            --border-subtle: #1e1e21;
            --text-primary: #fafafa;
            --text-secondary: #a1a1aa;
            --text-tertiary: #71717a;
            --accent: #10b981;
            --accent-dim: rgba(16, 185, 129, 0.15);
            --accent-hover: #059669;
        }}

        html {{
            font-family: 'Inter', 'Noto Sans SC', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            -webkit-font-smoothing: antialiased;
            background: var(--bg-primary);
            color: var(--text-primary);
            font-size: 14px;
            line-height: 1.6;
        }}

        body {{
            min-height: 100vh;
        }}

        ::selection {{
            background: var(--accent-dim);
            color: var(--text-primary);
        }}

        a {{
            color: var(--accent);
            text-decoration: none;
            transition: color 0.15s;
        }}

        a:hover {{
            color: var(--accent-hover);
        }}

        .container {{
            max-width: 1000px;
            margin: 0 auto;
            padding: 0 24px;
        }}

        /* Header */
        header {{
            position: sticky;
            top: 0;
            z-index: 100;
            background: rgba(10, 10, 11, 0.85);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border-bottom: 1px solid var(--border-subtle);
        }}

        .header-inner {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            height: 64px;
        }}

        .logo {{
            display: flex;
            align-items: center;
            gap: 12px;
            font-weight: 600;
            font-size: 18px;
            letter-spacing: -0.02em;
        }}

        .logo-icon {{
            width: 36px;
            height: 36px;
            background: linear-gradient(135deg, #10b981, #06b6d4);
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
        }}

        .logo-icon svg {{
            width: 20px;
            height: 20px;
            stroke: #000;
        }}

        .header-right {{
            display: flex;
            align-items: center;
            gap: 16px;
        }}

        .date-badge {{
            font-size: 12px;
            color: var(--text-tertiary);
            padding: 6px 12px;
            background: var(--bg-tertiary);
            border-radius: 6px;
            border: 1px solid var(--border-subtle);
        }}

        .github-link {{
            display: flex;
            align-items: center;
            gap: 8px;
            color: var(--text-secondary);
            font-size: 13px;
            transition: color 0.15s;
        }}

        .github-link:hover {{
            color: var(--text-primary);
        }}

        /* Main Content */
        main {{
            padding: 48px 0;
        }}

        /* Digest Item */
        .digest-item {{
            background: var(--bg-secondary);
            border: 1px solid var(--border-subtle);
            border-radius: 16px;
            margin-bottom: 32px;
            overflow: hidden;
            transition: border-color 0.2s;
        }}

        .digest-item:hover {{
            border-color: var(--border);
        }}

        .digest-header {{
            display: flex;
            align-items: center;
            gap: 16px;
            padding: 20px 24px;
            background: var(--bg-tertiary);
            border-bottom: 1px solid var(--border-subtle);
        }}

        .digest-icon {{
            width: 40px;
            height: 40px;
            background: var(--accent-dim);
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            flex-shrink: 0;
        }}

        .digest-icon svg {{
            width: 20px;
            height: 20px;
            color: var(--accent);
        }}

        .digest-title {{
            font-size: 18px;
            font-weight: 600;
            color: var(--text-primary);
            margin-bottom: 4px;
        }}

        .digest-date {{
            font-size: 13px;
            color: var(--text-tertiary);
            font-family: "SF Mono", Monaco, "Cascadia Code", monospace;
        }}

        .digest-content {{
            padding: 24px;
        }}

        /* Markdown Content Styles */
        .digest-content h3 {{
            font-size: 16px;
            font-weight: 600;
            margin: 24px 0 16px;
            color: var(--text-primary);
            display: flex;
            align-items: center;
            gap: 10px;
        }}

        .digest-content h3::before {{
            content: '';
            width: 4px;
            height: 18px;
            background: var(--accent);
            border-radius: 2px;
        }}

        .digest-content h4 {{
            font-size: 14px;
            font-weight: 600;
            margin: 20px 0 12px;
            color: var(--text-primary);
        }}

        .digest-content p {{
            margin-bottom: 12px;
            color: var(--text-secondary);
        }}

        .digest-content strong {{
            color: var(--text-primary);
            font-weight: 600;
        }}

        .digest-content em {{
            color: var(--text-tertiary);
        }}

        .digest-content ul {{
            margin-bottom: 20px;
            padding-left: 24px;
        }}

        .digest-content li {{
            margin-bottom: 12px;
            color: var(--text-secondary);
        }}

        .digest-content li::marker {{
            color: var(--accent);
        }}

        .digest-content a {{
            color: var(--accent);
            border-bottom: 1px solid transparent;
            transition: border-color 0.15s;
        }}

        .digest-content a:hover {{
            border-bottom-color: var(--accent);
        }}

        .digest-content hr {{
            border: none;
            border-top: 1px solid var(--border-subtle);
            margin: 32px 0;
        }}

        .digest-content blockquote {{
            border-left: 3px solid var(--accent);
            padding-left: 16px;
            margin: 20px 0;
            color: var(--text-tertiary);
        }}

        .digest-content code {{
            background: var(--bg-tertiary);
            padding: 3px 8px;
            border-radius: 4px;
            font-family: "SF Mono", Monaco, "Cascadia Code", monospace;
            font-size: 0.9em;
            color: var(--text-primary);
        }}

        .digest-content pre {{
            background: var(--bg-tertiary);
            padding: 16px;
            border-radius: 8px;
            overflow-x: auto;
            margin: 16px 0;
            border: 1px solid var(--border-subtle);
        }}

        .digest-content pre code {{
            background: none;
            padding: 0;
            color: var(--text-secondary);
        }}

        /* Empty State */
        .empty {{
            text-align: center;
            padding: 80px 24px;
            color: var(--text-tertiary);
            font-size: 15px;
        }}

        /* Footer */
        footer {{
            border-top: 1px solid var(--border-subtle);
            padding: 32px 0;
            margin-top: 48px;
        }}

        .footer-inner {{
            display: flex;
            align-items: center;
            justify-content: space-between;
        }}

        .footer-text {{
            font-size: 13px;
            color: var(--text-tertiary);
        }}

        .footer-links {{
            display: flex;
            gap: 24px;
        }}

        .footer-link {{
            font-size: 13px;
            color: var(--text-tertiary);
            text-decoration: none;
            transition: color 0.15s;
        }}

        .footer-link:hover {{
            color: var(--text-primary);
        }}

        /* Responsive */
        @media (max-width: 768px) {{
            .container {{
                padding: 0 16px;
            }}

            .header-inner {{
                height: 56px;
            }}

            .logo {{
                font-size: 16px;
            }}

            .logo-icon {{
                width: 32px;
                height: 32px;
            }}

            .digest-header {{
                flex-direction: column;
                align-items: flex-start;
                gap: 12px;
                padding: 16px 20px;
            }}

            .digest-content {{
                padding: 20px 16px;
            }}

            .digest-title {{
                font-size: 16px;
            }}

            .footer-inner {{
                flex-direction: column;
                gap: 16px;
                text-align: center;
            }}

            .header-right {{
                gap: 8px;
            }}

            .date-badge {{
                display: none;
            }}
        }}
    </style>
</head>
<body>
    <header>
        <div class="container">
            <div class="header-inner">
                <div class="logo">
                    <div class="logo-icon">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                            <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/>
                        </svg>
                    </div>
                    <span>每日科技简报</span>
                </div>
                <div class="header-right">
                    <span class="date-badge">{now}</span>
                    <a href="https://github.com/biyan113/cron" class="github-link">
                        <svg width="18" height="18" viewBox="0 0 16 16" fill="currentColor">
                            <path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0016 8c0-4.42-3.58-8-8-8z"/>
                        </svg>
                        GitHub
                    </a>
                </div>
            </div>
        </div>
    </header>

    <main>
        <div class="container">
            {digests_section}
        </div>
    </main>

    <footer>
        <div class="container">
            <div class="footer-inner">
                <div class="footer-text">&copy; 2026 每日科技简报 · 由 Claude AI 自动生成</div>
                <div class="footer-links">
                    <a href="https://github.com/biyan113/cron" class="footer-link">GitHub</a>
                    <a href="https://github.com/biyan113/cron" class="footer-link">V2EX</a>
                    <a href="https://github.com/biyan113/cron" class="footer-link">Hacker News</a>
                </div>
            </div>
        </div>
    </footer>
</body>
</html>
"""

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"[完成] 已生成: {output_path}")


def main():
    """主函数"""
    print("=" * 50)
    print("GitHub Pages 生成器")
    print("=" * 50)

    config = load_config()
    digests_dir = PROJECT_ROOT / config["output"]["digests_dir"]

    print(f"\n扫描目录: {digests_dir}")

    files = get_digest_files(digests_dir)
    print(f"找到 {len(files)} 份简报")

    # 生成到根目录，用于 GitHub Pages
    output_path = PROJECT_ROOT / "index.html"
    generate_page(files, output_path)

    print("\n" + "=" * 50)
    print("生成完成!")
    print("=" * 50)


if __name__ == "__main__":
    main()
