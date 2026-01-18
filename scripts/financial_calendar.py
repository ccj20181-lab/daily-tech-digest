#!/usr/bin/env python3
"""
Financial Calendar Reminder
Fetches economic events for today and tomorrow, and sends a notification via PushPlus.
"""

import os
import sys
import datetime
import pytz
import akshare as ak
import pandas as pd
import traceback

# Add current directory to sys.path to import send_pushplus
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

try:
    from send_pushplus import send_pushplus_notification
except ImportError:
    # Fallback if running from root directory
    sys.path.append(os.path.join(os.getcwd(), 'scripts'))
    from send_pushplus import send_pushplus_notification

def get_current_time():
    """Get current time in Shanghai timezone"""
    tz = pytz.timezone('Asia/Shanghai')
    return datetime.datetime.now(tz)

def fetch_economic_calendar(date_obj):
    """
    Fetch economic calendar for a specific date using akshare.
    Returns a DataFrame or None if failed/empty.
    """
    date_str = date_obj.strftime("%Y%m%d")
    print(f"Fetching economic calendar for {date_str}...")

    try:
        # Use Baidu interface as it is stable and verified
        df = ak.news_economic_baidu(date=date_str)
        return df
    except Exception as e:
        print(f"Error fetching Baidu calendar: {e}")
        return None

def format_event_row(row):
    """Format a single event row from the dataframe"""
    # Columns: '日期', '时间', '地区', '事件', '公布', '预期', '前值', '重要性'
    time = row.get('时间', 'N/A')
    country = row.get('地区', 'N/A')
    event = row.get('事件', 'N/A')
    importance = row.get('重要性', '')
    actual = row.get('公布', '')
    forecast = row.get('预期', '')
    previous = row.get('前值', '')

    # Map importance (Baidu usually uses 1, 2, 3 stars)
    try:
        imp_val = int(importance)
    except:
        imp_val = 1

    if imp_val >= 3:
        icon = "🔴" # High
    elif imp_val == 2:
        icon = "🟡" # Medium
    else:
        icon = "⚪" # Low

    # Format string
    # - 09:30 🔴 **中国**: CPI年率 (前: 0.7%, 预: 0.8%)
    details = []
    if previous and str(previous).strip() != 'nan':
        details.append(f"前:{previous}")
    if forecast and str(forecast).strip() != 'nan':
        details.append(f"预:{forecast}")

    detail_str = f" ({', '.join(details)})" if details else ""

    return f"- {time} {icon} **{country}**: {event}{detail_str}"

def process_calendar_data(df):
    """
    Process and filter calendar data.
    Returns a list of formatted strings for important events.
    """
    if df is None or df.empty:
        return []

    formatted_events = []

    for _, row in df.iterrows():
        try:
            importance = int(row.get('重要性', 0))
        except:
            importance = 0

        # Filter for Medium (2) and High (3) importance
        if importance >= 2:
            formatted_events.append(format_event_row(row))

    return formatted_events

def get_current_report_period(date_obj):
    """
    Determine which report period is active.
    A-share Disclosure Season:
    - Annual Report (previous year): Jan 1 - Apr 30
    - Q1 Report: Apr 1 - Apr 30
    - Semi-Annual: Jul 1 - Aug 30
    - Q3 Report: Oct 1 - Oct 31
    """
    month = date_obj.month
    year = date_obj.year

    if 1 <= month <= 4:
        return f"{year - 1}年报"
    elif 7 <= month <= 8:
        return f"{year}中报" # Semi-annual
    elif month == 10:
        return f"{year}三季报"
    else:
        # Outside standard mandatory disclosure windows, checking for annual report of previous year is safest bet or return None
        if month > 4 and month < 7:
             return f"{year}一季报" # Just in case
        return f"{year-1}年报"

def fetch_earnings_calendar(date_obj):
    """
    Fetch earnings calendar (disclosure schedule) for a specific date.
    Returns DataFrame or None.
    """
    try:
        period = get_current_report_period(date_obj)
        print(f"Fetching earnings calendar for {period}...")

        # This function returns the whole schedule for the period.
        # We need to cache it or filter it.
        # Since we are running this daily, fetching the whole list (thousands of rows) might be heavy
        # but akshare usually handles it.
        df = ak.stock_report_disclosure(market="沪深京", period=period)

        if df is None or df.empty:
            return None

        # Filter for the specific date
        # Columns usually: '股票代码', '股票简称', '首次预约', '初次变更', '二次变更', '三次变更', '实际披露'
        # We check '首次预约' (First Reservation) matching our date string YYYY-MM-DD
        date_str = date_obj.strftime("%Y-%m-%d")

        # Ensure column is string or datetime
        # Simple string matching

        # We need to handle potential multiple reservation columns, but '首次预约' is the main one for reminders.
        # If '实际披露' exists and matches, it's confirmed. But for reminders, we use reservation.

        target_df = df[df['首次预约'].astype(str) == date_str].copy()

        return target_df

    except Exception as e:
        print(f"Error fetching earnings calendar: {e}")
        return None

def format_earnings_row(row):
    """Format a single earnings row"""
    code = row.get('股票代码', '')
    name = row.get('股票简称', '')
    return f"- 📊 **{name}** ({code})"

def process_earnings_data(df):
    """
    Process earnings data.
    Returns list of formatted strings.
    """
    if df is None or df.empty:
        return []

    events = []
    # Limit to top 15 to avoid spamming if many companies report on the same day
    count = 0
    max_count = 15

    for _, row in df.iterrows():
        if count >= max_count:
            events.append(f"- ... (共 {len(df)} 家)")
            break
        events.append(format_earnings_row(row))
        count += 1

    return events

def main():
    # 1. Setup
    token = os.environ.get("PUSHPLUS_TOKEN")
    if not token:
        print("[Error] PUSHPLUS_TOKEN not found")
        sys.exit(1)

    now = get_current_time()
    today = now.date()
    tomorrow = today + datetime.timedelta(days=1)

    print(f"Running Financial Calendar for {today}")

    # 2. Fetch Data
    print("Fetching Economic Data...")
    today_eco_df = fetch_economic_calendar(today)
    tomorrow_eco_df = fetch_economic_calendar(tomorrow)

    today_eco_events = process_calendar_data(today_eco_df)
    tomorrow_eco_events = process_calendar_data(tomorrow_eco_df)

    print("Fetching Earnings Data...")
    today_earnings_df = fetch_earnings_calendar(today)
    tomorrow_earnings_df = fetch_earnings_calendar(tomorrow)

    today_earnings_events = process_earnings_data(today_earnings_df)
    tomorrow_earnings_events = process_earnings_data(tomorrow_earnings_df)

    # 3. Build Message
    message_parts = []

    # Header
    message_parts.append(f"# 📅 财经日历提醒 ({today})")
    message_parts.append(f"> 生成时间: {now.strftime('%H:%M')}")
    message_parts.append("---")

    # Today's Economic Events
    message_parts.append("## 🚨 今日重要数据 (Today)")
    if today_eco_events:
        message_parts.extend(today_eco_events)
    else:
        message_parts.append("今日无重点关注的高重要性数据。")

    # Today's Earnings
    if today_earnings_events:
        message_parts.append("")
        message_parts.append("## 📊 今日财报披露")
        message_parts.extend(today_earnings_events)

    message_parts.append("")

    # Tomorrow's Economic Events
    message_parts.append("## 🔮 明日预告 (Tomorrow)")
    if tomorrow_eco_events:
        message_parts.extend(tomorrow_eco_events)
    else:
        message_parts.append("明日暂无高重要性数据预告。")

    # Tomorrow's Earnings
    if tomorrow_earnings_events:
        message_parts.append("")
        message_parts.append("## 📝 明日财报预约")
        message_parts.extend(tomorrow_earnings_events)

    message_parts.append("")
    message_parts.append("---")
    message_parts.append("**注**: 🔴=高重要性 🟡=中重要性")

    full_content = "\n".join(message_parts)
    print("Generated Content:")
    print(full_content)

    # 4. Send Notification
    title = f"📅 财经日历提醒 {today}"
    success = send_pushplus_notification(token, title, full_content)

    if success:
        print("Notification sent successfully.")
    else:
        print("Failed to send notification.")
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        traceback.print_exc()
        sys.exit(1)
