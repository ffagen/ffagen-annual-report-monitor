#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
年报公告监控 - 主脚本
抓取当天公布的年报公告，生成报告，发送到飞书
"""
import os
import sys
import json
import re
import requests
from datetime import datetime, date
from pathlib import Path
from typing import List, Dict, Optional
from config import (
    FEISHU_APP_ID, FEISHU_APP_SECRET, FEISHU_CHAT_ID,
    get_monitored_stocks_list, REPORT_DIR, EASTMONEY_API_BASE, HEADERS
)
from feishu_client import FeishuClient

# 添加当前目录到路径
sys.path.insert(0, str(Path(__file__).parent))

# 东方财富年报公告API
ANN_URL = "https://np-anotice-stock.eastmoney.com/api/security/ann"


def fetch_annual_reports(page: int = 1, page_size: int = 50) -> Optional[Dict]:
    """抓取东方财富年报公告"""
    try:
        # 年报密集期一般在3-4月，这里抓取最近7天的公告
        params = {
            "cb": "",
            "sr": "-1",
            "page_size": page_size,
            "page_index": page,
            "ann_type": "SHA,SZA,SWA",  # 沪深A股
            "client_source": "web",
            "f_ann_type": "",
            "keyword": "",
            "plate": "",
            "market_type": "",
        }
        print(f"[东方财富] 请求第{page}页...")
        resp = requests.get(ANN_URL, params=params, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        print(f"[东方财富] 抓取失败: {e}")
        return None


def parse_reports(data: Dict) -> List[Dict]:
    """解析公告数据"""
    reports = []
    try:
        items = data.get("data", {}).get("list", [])
        today = date.today()
        today_str = today.strftime("%Y-%m-%d")

        for item in items:
            # 提取公告日期
            notice_date = item.get("notice_date", "")
            if notice_date and isinstance(notice_date, str):
                # 格式可能是 2026-03-30 或时间戳
                if len(notice_date) == 10:
                    item_date = notice_date[:10]
                else:
                    continue
            else:
                continue

            # 只保留今天的
            if item_date != today_str:
                continue

            # 提取标题判断是否是年报
            title = item.get("title", "")
            if not title:
                continue

            # 年报标题通常包含"年度报告"或"年报"
            is_annual = "年度报告" in title or "年度审计" in title
            is_qreport = "季报" in title or "半年报" in title
            if not is_annual:
                continue

            # 提取股票代码
            codes = item.get("codes", [])
            if not codes:
                continue

            code = codes[0].get("code", "")
            name = codes[0].get("name", "")

            # 提取内容摘要
            summary = item.get("summary", "") or item.get("art_content", "") or ""

            reports.append({
                "code": code,
                "name": name,
                "title": title,
                "date": item_date,
                "url": item.get("art_url", ""),
                "summary": summary[:200] if summary else "",
            })
    except Exception as e:
        print(f"[解析] 解析数据异常: {e}")
    return reports


def fetch_from_eastmoney_data() -> List[Dict]:
    """从东方财富数据中心获取年报数据"""
    reports = []
    try:
        # 东方财富数据中心 - 年报公告
        url = "https://data.eastmoney.com/center/ajaxAnnouncementRequest"
        today = date.today()
        params = {
            "pageIndex": 1,
            "pageSize": 50,
            "announcetypes": "020001,020002",  # 年报类型
            "market": "全部",
            "startdate": today.strftime("%Y-%m-%d"),
            "enddate": today.strftime("%Y-%m-%d"),
        }
        print("[东方财富数据中心] 抓取年报...")
        resp = requests.get(url, params=params, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        data = resp.json()

        items = data.get("result", {}).get("list", []) if isinstance(data.get("result"), dict) else []
        for item in items:
            title = item.get("announcementTitle", "")
            if "年度报告" not in title:
                continue

            code_match = re.search(r'\((\d{6})\)', title)
            if not code_match:
                code_match = re.search(r'\d{6}', title)

            reports.append({
                "code": code_match.group(1) if code_match else "",
                "name": item.get("secuName", ""),
                "title": title,
                "date": item.get("publishDate", "")[:10] if item.get("publishDate") else "",
                "url": f"https://data.eastmoney.com/report/{item.get('id', '')}.html",
                "summary": "",
            })
    except Exception as e:
        print(f"[东方财富数据中心] 抓取失败: {e}")
    return reports


def generate_report_content(reports: List[Dict], monitored_stocks: List[str]) -> str:
    """生成报告内容"""
    today_str = date.today().strftime("%Y年%m月%d日")

    if not reports:
        return f"📅 {today_str}暂无新增年报公告"

    # 过滤持仓股
    if monitored_stocks:
        filtered = [r for r in reports if r["code"] in monitored_stocks]
        if filtered:
            reports = filtered

    # 排序
    reports.sort(key=lambda x: x.get("code", ""))

    # 生成分组内容
    lines = []
    lines.append(f"📊 **{today_str}年报公告速递**\n")
    lines.append(f"共 **{len(reports)}** 家公司发布年报\n")

    # 表格
    lines.append("│ 股票代码 │ 股票名称 │ 公告标题 │")
    lines.append("│----------|----------|----------|")

    for r in reports[:20]:  # 最多20条
        code = r.get("code", "")
        name = r.get("name", "")[:8]
        title = r.get("title", "")[:20]
        lines.append(f"│ `{code}` │ {name} │ {title} │")

    if len(reports) > 20:
        lines.append(f"\n...还有 **{len(reports) - 20}** 条")

    return "\n".join(lines)


def save_html_report(reports: List[Dict], output_path: Path):
    """保存HTML报告"""
    today_str = date.today().strftime("%Y年%m月%d日")
    html = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>{today_str}年报公告</title>
<style>
body{{font-family:Arial,sans-serif;margin:20px;background:#f5f5f5}}
h1{{color:#333}}table{{width:100%;border-collapse:collapse;background:#fff}}
th{{background:#1890f0;color:#fff;padding:10px;text-align:left}}
td{{padding:8px;border-bottom:1px solid #eee}}
tr:hover{{background:#f0f7ff}}a{{color:#1890f0;text-decoration:none}}
.badge{{display:inline-block;padding:2px 8px;border-radius:10px;font-size:12px}}
.badge-plus{{background:#e6f7ff;color:#1890f0}} .badge-minus{{background:#fff1f0;color:#ff4d4f}}
</style></head><body>
<h1>📊 {today_str} 年报公告速递</h1>
<p>共 {len(reports)} 家公司发布年报</p>
<table><thead><tr><th>股票代码</th><th>股票名称</th><th>公告标题</th><th>发布日期</th><th>链接</th></tr></thead><tbody>"""

    for r in reports:
        url = r.get("url", "#")
        html += f"""<tr>
<td><code>{r.get('code','')}</code></td>
<td>{r.get('name','')}</td>
<td>{r.get('title','')}</td>
<td>{r.get('date','')}</td>
<td><a href="{url}" target="_blank">查看</a></td>
</tr>"""

    html += "</tbody></table></body></html>"
    output_path.write_text(html, encoding="utf-8")
    print(f"[报告] 已保存到 {output_path}")


def main():
    print(f"[年报监控] 启动 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # 获取持仓股列表
    monitored_stocks = get_monitored_stocks_list()
    if monitored_stocks:
        print(f"[持仓] 仅监控: {monitored_stocks}")
    else:
        print("[持仓] 监控所有股票")

    # 抓取年报数据
    all_reports = []

    # 方法1: 东方财富年报公告
    print("[抓取] 东方财富年报公告...")
    data = fetch_annual_reports(page=1)
    if data:
        reports = parse_reports(data)
        all_reports.extend(reports)
        print(f"[抓取] 获取到 {len(reports)} 条年报")
    else:
        # 备用: 从数据中心抓
        reports = fetch_from_eastmoney_data()
        all_reports.extend(reports)
        print(f"[备用] 从数据中心获取 {len(reports)} 条")

    # 去重
    seen = set()
    unique_reports = []
    for r in all_reports:
        key = r.get("code", "") + r.get("title", "")
        if key and key not in seen:
            seen.add(key)
            unique_reports.append(r)

    print(f"[汇总] 共 {len(unique_reports)} 条唯一年报")

    # 保存HTML报告
    output_file = REPORT_DIR / f"annual_report_{date.today().strftime('%Y%m%d')}.html"
    save_html_report(unique_reports, output_file)

    # 生成消息内容
    msg_content = generate_report_content(unique_reports, monitored_stocks)

    # 发送到飞书
    if FEISHU_APP_ID and FEISHU_APP_SECRET and FEISHU_CHAT_ID:
        print("[飞书] 发送消息...")
        client = FeishuClient()
        if unique_reports:
            success = client.send_rich_text_message(
                title=f"📊 {date.today().strftime('%Y年%m月%d日')}年报公告速递",
                content=msg_content
            )
        else:
            # 无数据时发简单文本
            success = client.send_text_message(
                f"📊 {date.today().strftime('%Y年%m月%d日')}年报公告速递\n\n今日暂无新增年报公告（{date.today().strftime('%m月')}非年报密集期）"
            )
        if success:
            print("[完成] 飞书消息发送成功!")
        else:
            print("[失败] 飞书消息发送失败")
    else:
        print("[跳过] 飞书未配置，仅保存本地报告")

    print(f"[年报监控] 完成 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    main()
