#!/usr/bin/env python3
"""
年报公告监控脚本
爬取当天A股/港股年报公告，推送飞书+保存文件

依赖环境变量:
  FEISHU_APP_ID      - 飞书应用 App ID
  FEISHU_APP_SECRET  - 飞书应用 Secret
  FEISHU_CHAT_ID     - 飞书群/用户 ID
  MONITORED_STOCKS   - 关注的股票代码，逗号分隔（可选）
  OUT_DIR            - 报告输出目录（可选，默认 ~/Documents/财经信息）
"""
import requests
import json
import re
import os
from datetime import datetime

APP_ID = os.getenv("FEISHU_APP_ID", "")
APP_SECRET = os.getenv("FEISHU_APP_SECRET", "")
OUT_DIR = os.getenv("OUT_DIR", os.path.expanduser("~/Documents/财经信息"))
FEISHU_GROUP_ID = os.getenv("FEISHU_CHAT_ID", "")

FEISHU_TOKEN_URL = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
FEISHU_MSG_URL = "https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=chat_id"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    "Referer": "https://data.eastmoney.com/",
    "Accept": "application/json, text/plain, */*",
}

def get_token():
    r = requests.post(FEISHU_TOKEN_URL, json={"app_id": APP_ID, "app_secret": APP_SECRET}, timeout=10)
    d = r.json()
    return d.get("tenant_access_token") if d.get("code") == 0 else None

def send_card(title: str, content: str, token: str) -> tuple:
    card = {
        "receive_id": FEISHU_GROUP_ID,
        "msg_type": "interactive",
        "content": json.dumps({
            "config": {"wide_screen_mode": True},
            "header": {"title": {"tag": "plain_text", "text": title}, "template": "purple"},
            "elements": [{"tag": "div", "text": {"tag": "lark_md", "content": content}}]
        })
    }
    r = requests.post(FEISHU_MSG_URL,
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        json=card, timeout=15)
    d = r.json()
    return d.get("code") == 0, d.get("msg", "")

def fetch_annual_reports():
    today = datetime.now().strftime("%Y-%m-%d")
    url = "https://np-anotice-stock.eastmoney.com/api/security/ann"
    params = {
        "sr": "-1", "page_size": 50, "page_index": 1, "ann_type": "A", "f": "1",
        "fields": "ann_title,ann_date,stock_code,stock_name,notice_type",
        "date_range": today,
    }
    try:
        r = requests.get(url, params=params, headers=HEADERS, timeout=15)
        d = r.json()
        if d.get("code") == 0:
            items = d.get("data", {}).get("list", [])
            return [i for i in items if i.get("ann_date", "").startswith(today)]
    except Exception as e:
        print(f"获取年报数据失败: {e}")
    return []

def save_report(content: str, filename: str) -> str:
    os.makedirs(OUT_DIR, exist_ok=True)
    path = os.path.join(OUT_DIR, filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return path

def main():
    if not APP_ID or not APP_SECRET or not FEISHU_GROUP_ID:
        print("❌ 请设置环境变量: FEISHU_APP_ID, FEISHU_APP_SECRET, FEISHU_CHAT_ID")
        return

    token = get_token()
    if not token:
        print("❌ Token获取失败")
        return

    reports = fetch_annual_reports()
    today_str = datetime.now().strftime("%m月%d日")
    today_ymd = datetime.now().strftime("%Y-%m-%d")

    if not reports:
        content = f"> 📭 今日（{today_str}）暂无新增年报公告\n\n可能原因：非交易日或发布时间较晚。"
        ok, msg = send_card(f"📊 {today_str} 年报公告速递", content, token)
        save_report(content, f"年报公告_{today_ymd}.md")
        print(f"{'✅' if ok else '❌'} 飞书:{'成功' if ok else '失败:'+msg} | 文件已保存")
        return

    important = []
    skip_keywords = ["摘要", "英文", "置换", "更新"]
    for r in reports:
        title = r.get("ann_title", "")
        if any(k in title for k in skip_keywords):
            continue
        important.append(r)

    lines = [f"# 📊 年报公告速递\n\n**统计时间：** {today_str}  |  共{len(important)}份重要年报\n\n---\n\n"]
    for r in important[:15]:
        code = r.get("stock_code", "")
        name = r.get("stock_name", "")
        title = r.get("ann_title", "")
        date = r.get("ann_date", "")[5:]
        if "利润" in title or "业绩" in title:
            emoji = "📈" if not ("下滑" in title or "亏损" in title) else "📉"
        elif "扭亏" in title:
            emoji = "🔄"
        elif "ST" in title:
            emoji = "⚠️"
        else:
            emoji = "📋"
        lines.append(f"{emoji} **{name}({code})**\n>{title}\n>📅 {date}\n\n")

    md_content = "\n".join(lines)
    card_content = md_content.replace("# 📊 年报公告速递\n\n", "").replace("**统计时间：**", "> 📅 统计时间：")

    ok, msg = send_card(f"📊 {today_str} 年报公告速递（共{len(important)}份）", card_content, token)
    path = save_report(md_content, f"年报公告_{today_ymd}.md")
    print(f"{'✅' if ok else '❌'} 飞书:{'成功' if ok else '失败:'+msg} | 文件:{path}")

if __name__ == "__main__":
    main()
