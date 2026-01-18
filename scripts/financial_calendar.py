#!/usr/bin/env python3
"""
Financial Calendar Reminder
Fetches economic events and earnings reports for today and tomorrow.
Also scans the next 7 days for "Super Events" (High impact).
Sends notification via PushPlus.
"""

import sys
import os
import time
import akshare as ak
import pandas as pd
from datetime import datetime, timedelta
import pytz
import traceback

# Ensure we can import from the same directory
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from send_pushplus import send_pushplus_notification
except ImportError:
    # Fallback if running from root
    sys.path.append(os.path.join(os.getcwd(), 'scripts'))
    from send_pushplus import send_pushplus_notification

# Configuration
MAX_RETRIES = 3
RETRY_DELAY = 5  # seconds
TZ = pytz.timezone('Asia/Shanghai')

# Super Event Keywords (High Impact)
SUPER_EVENT_KEYWORDS = [
    "利率决议", "央行", "非农", "GDP", "CPI", "PPI", "失业率",
    "会议纪要", "美联储", "欧洲央行", "财政预算"
]

def get_current_time():
    return datetime.now(TZ)

def fetch_data_with_retry(func, *args, **kwargs):
    """Run an akshare function with retry logic."""
    for attempt in range(MAX_RETRIES):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(f"[Warning] Attempt {attempt + 1}/{MAX_RETRIES} failed for {func.__name__}: {e}")
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY)
            else:
                print(f"[Error] All retries failed for {func.__name__}")
                return None

# -----------------------------------------------------------------------------
# Economic Calendar (Jin10 / Baidu)
# -----------------------------------------------------------------------------

def fetch_economic_events(date_str):
    """
    Fetch economic events for a specific date.
    date_str: 'YYYYmmdd'
    """
    print(f"Fetching economic events for {date_str}...")

    # Try Jin10 first (richer data)
    try:
        df = fetch_data_with_retry(ak.calendar_economic_jin10, date=date_str)
        if df is not None and not df.empty:
            return df
    except Exception as e:
        print(f"Jin10 fetch failed: {e}")

    # Fallback to Baidu? Baidu structure is different.
    # For now, let's rely on Jin10 or return empty if failed.
    return pd.DataFrame()

def format_daily_events(df, date_label):
    """Format the main list of events for the daily reminder."""
    if df.empty:
        return "暂无高重要性数据/事件。"

    lines = []
    # Jin10 Columns: "时间", "地区", "指标", "重要性", "前值", "预测值", "公布值", "事件"

    for _, row in df.iterrows():
        importance = str(row.get('重要性', ''))
        # Only show High importance
        if '高' in importance or 'High' in importance or '3' in str(importance):
            time_str = row.get('时间', '')
            region = row.get('地区', '')
            indicator = row.get('指标', '')
            event = row.get('事件', '')

            content = indicator if indicator else event
            if event and indicator and event != indicator:
                content = f"{indicator} ({event})"

            prediction = row.get('预测值', '')
            previous = row.get('前值', '')

            line = f"- **{time_str}** {region} {content}"
            extra = []
            if prediction: extra.append(f"预:{prediction}")
            if previous: extra.append(f"前:{previous}")

            if extra:
                line += f" ({', '.join(extra)})"

            lines.append(line)

    if not lines:
        return "暂无高重要性数据/事件。"

    return "\n".join(lines)

def filter_super_events(df, date_display):
    """Filter events that match super keywords for the weekly scan."""
    if df.empty:
        return []

    super_events = []
    for _, row in df.iterrows():
        content = str(row.get('事件', '')) + " " + str(row.get('指标', ''))
        importance = str(row.get('重要性', ''))

        # Check keywords
        matched = False
        for kw in SUPER_EVENT_KEYWORDS:
            if kw in content:
                matched = True
                break

        # Must be High importance OR contain critical keyword
        is_high = '高' in importance or 'High' in importance

        if matched and is_high:
            time_str = row.get('时间', '')
            region = row.get('地区', '')
            event_str = f"**{date_display} {time_str}** {region} {content.strip()}"
            super_events.append(event_str)

    return super_events

def scan_next_week():
    """Scan the next 7 days for super events."""
    today = get_current_time().date()
    # Start looking from Day+2 (since Tomorrow is already covered in detail)
    # Actually, user wants "Future" lookahead.
    # If we run on Day 0 evening (for Day 1), Day 1 is "Tomorrow".
    # So "Future" usually means Day 2 to Day 7.

    start_date = today + timedelta(days=2)
    end_date = today + timedelta(days=7)

    all_super_events = []

    current = start_date
    while current <= end_date:
        date_str = current.strftime("%Y%m%d")
        display_date = current.strftime("%m-%d %a") # e.g., 01-18 Sat

        df = fetch_economic_events(date_str)
        events = filter_super_events(df, display_date)
        all_super_events.extend(events)

        current += timedelta(days=1)
        time.sleep(1) # Rate limit politeness

    return all_super_events

# -----------------------------------------------------------------------------
# Earnings Calendar (A-Share)
# -----------------------------------------------------------------------------

def get_report_period(date_obj):
    year = date_obj.year
    month = date_obj.month
    if 1 <= month <= 4: return f"{year - 1}年报"
    if 4 < month <= 8: return f"{year}中报"
    if 8 < month <= 10: return f"{year}三季报"
    return f"{year}年报" # Default fallback

def fetch_earnings_events(date_obj):
    """Fetch earnings disclosure for a specific date."""
    date_str = date_obj.strftime("%Y-%m-%d")
    print(f"Fetching earnings for {date_str}...")

    try:
        period = get_report_period(date_obj)
        # Fetch period data (cached if possible, but here we just fetch)
        # Note: This might be heavy if called multiple times.
        # Ideally we fetch once per period, but script runs once daily.
        df = fetch_data_with_retry(ak.stock_report_disclosure, market="沪深京", period=period)

        if df is None or df.empty:
            return []

        # Filter for date
        # Check columns. Usually '首次预约'
        if '首次预约' not in df.columns:
            return []

        # Filter
        target = df[df['首次预约'].astype(str) == date_str]

        events = []
        count = 0
        for _, row in target.iterrows():
            if count >= 10: # Limit to 10
                events.append(f"- ... (共 {len(target)} 家)")
                break
            name = row.get('股票简称', '')
            code = row.get('股票代码', '')
            events.append(f"- 📊 **{name}** ({code})")
            count += 1

        return events

    except Exception as e:
        print(f"Earnings fetch failed: {e}")
        return []

# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------

def main():
    token = os.environ.get("PUSHPLUS_TOKEN")
    if not token:
        print("[Error] PUSHPLUS_TOKEN not found")
        sys.exit(1)

    now = get_current_time()
    today_date = now.date()
    tomorrow_date = today_date + timedelta(days=1)

    today_str = today_date.strftime("%Y%m%d")
    tomorrow_str = tomorrow_date.strftime("%Y%m%d")

    print(f"--- Starting Financial Calendar Check for {today_date} ---")

    # 1. Fetch Today & Tomorrow Economic Events
    print("\n[1/4] Fetching Economic Data...")
    df_today = fetch_economic_events(today_str)
    df_tomorrow = fetch_economic_events(tomorrow_str)

    txt_today_eco = format_daily_events(df_today, "Today")
    txt_tomorrow_eco = format_daily_events(df_tomorrow, "Tomorrow")

    # 2. Fetch Earnings
    print("\n[2/4] Fetching Earnings Data...")
    list_today_earnings = fetch_earnings_events(today_date)
    list_tomorrow_earnings = fetch_earnings_events(tomorrow_date)

    # 3. Lookahead Scan
    print("\n[3/4] Scanning Next Week...")
    super_events = scan_next_week()

    # 4. Build Message
    print("\n[4/4] Building Notification...")
    lines = []

    # Title
    lines.append(f"# 📅 财经日历提醒 {tomorrow_date.strftime('%m-%d')}")
    lines.append(f"> 生成时间: {now.strftime('%H:%M')}")
    lines.append("---")

    # Part A: Tomorrow (Focus)
    lines.append(f"## 📌 明日预告 ({tomorrow_date.strftime('%m-%d %a')})")
    lines.append(txt_tomorrow_eco)
    if list_tomorrow_earnings:
        lines.append("\n**财报披露**:")
        lines.extend(list_tomorrow_earnings)
    else:
        lines.append("\n(无重点财报)")
    lines.append("")

    # Part B: Today (Review/Urgent)
    lines.append(f"## 🚨 今日概览 ({today_date.strftime('%m-%d')})")
    lines.append(txt_today_eco)
    if list_today_earnings:
        lines.append("\n**今日财报**:")
        lines.extend(list_today_earnings)
    lines.append("")

    # Part C: Future Lookahead
    lines.append("## 🌟 未来一周重磅前瞻")
    if super_events:
        for ev in super_events:
            lines.append(f"- {ev}")
    else:
        lines.append("无重大央行决议或核心数据发布。")

    lines.append("\n---")
    lines.append("Generated by Financial-Calendar-Bot")

    final_content = "\n".join(lines)

    # Send
    title = f"财经日历 {tomorrow_date.strftime('%m-%d')} 前瞻"
    success = send_pushplus_notification(token, title, final_content)

    if success:
        print("Done.")
    else:
        print("Failed to send.")
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        traceback.print_exc()
        sys.exit(1)
