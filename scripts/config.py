"""
年报公告监控 - 配置文件
读取环境变量配置
"""
import os
from pathlib import Path

# 飞书配置
FEISHU_APP_ID = os.getenv("FEISHU_APP_ID", "")
FEISHU_APP_SECRET = os.getenv("FEISHU_APP_SECRET", "")
FEISHU_CHAT_ID = os.getenv("FEISHU_CHAT_ID", "")

# 持仓股票列表（逗号分隔的股票代码）
# 例如: "03140,03186" 或 "03140(华夏港美AI),03186(易方达生物医药)"
MONITORED_STOCKS = os.getenv("MONITORED_STOCKS", "")

# 解析持仓股票为列表
def get_monitored_stocks_list():
    """返回持仓股票代码列表"""
    if not MONITORED_STOCKS:
        return []
    stocks = []
    for item in MONITORED_STOCKS.split(","):
        item = item.strip()
        if item:
            # 提取股票代码（去掉括号内的中文）
            code = item.split("(")[0].strip()
            stocks.append(code)
    return stocks

# 报告输出目录
REPORT_DIR = Path(os.getenv("REPORT_DIR", "/tmp/annual_reports"))
REPORT_DIR.mkdir(parents=True, exist_ok=True)

# 东方财富API配置
EASTMONEY_API_BASE = "https://np-anotice-stock.eastmoney.com/api/security/ann"

# User-Agent伪装
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://data.eastmoney.com/",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
}

def is_configured():
    """检查飞书配置是否完整"""
    return bool(FEISHU_APP_ID and FEISHU_APP_SECRET and FEISHU_CHAT_ID)

if __name__ == "__main__":
    print("=== 年报监控配置 ===")
    print(f"飞书APP_ID: {'已配置' if FEISHU_APP_ID else '未配置'}")
    print(f"飞书APP_SECRET: {'已配置' if FEISHU_APP_SECRET else '未配置'}")
    print(f"飞书CHAT_ID: {'已配置' if FEISHU_CHAT_ID else '未配置'}")
    print(f"持仓股票: {MONITORED_STOCKS or '未配置（监控所有）'}")
    print(f"报告目录: {REPORT_DIR}")
