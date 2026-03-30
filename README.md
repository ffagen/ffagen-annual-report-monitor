# 📊 A股/港股年报公告监控

定时爬取东方财富、AI财报网等平台当天公布的年报公告，AI自动筛选重点公司（业绩增长/下滑前五、重大亏损），生成分析报告并发送飞书通知。

## ✨ 功能特性

- 📋 **实时爬取** — 东方财富 + AI财报网双数据源，支持A股/港股
- 🤖 **智能筛选** — 按业绩增速排名，自动标记 Top5 / Flop5
- 🏭 **重点公司摘要** — 关键词识别：净利润增长、业绩下滑、ST、扭亏为盈
- 📱 **飞书推送** — 富文本消息，包含表格、简评、报告链接
- 🎯 **股票池过滤** — 支持只关注持仓股票（`MONITORED_STOCKS`）
- ⏰ **定时监控** — 可配置检查间隔，默认每天 9:00 / 12:00 / 18:00

## 📖 报告示例

```
📊 3月30日年报公告速递

| 股票代码 | 股票名称 | 净利润增速 | 重要事项 |
|---------|---------|-----------|---------|
| 600519 | 贵州茅台 | +18.5% | 业绩稳健增长 |
| 000858 | 五粮液 | +12.3% | 白酒龙头 |
...

整体披露情况：今日共XX家公司公布年报...
```

## ⚙️ 配置

### 环境变量

| 变量 | 必填 | 说明 |
|------|------|------|
| `FEISHU_APP_ID` | ✅ | 飞书应用 App ID |
| `FEISHU_APP_SECRET` | ✅ | 飞书应用 Secret |
| `FEISHU_CHAT_ID` | ✅ | 飞书群/用户 ID |
| `MONITORED_STOCKS` | 否 | 关注的股票代码（逗号分隔）|
| `CHECK_INTERVAL` | 否 | 检查间隔（小时），默认4 |

### 飞书应用权限

- `im:message:send_as_bot` — 发送消息

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install requests beautifulsoup4 pandas python-dateutil
```

### 2. 配置飞书机器人

参考 [飞书开放平台文档](https://open.feishu.cn/) 创建应用并获取 App ID / Secret

### 3. 运行

```bash
cd scripts
export FEISHU_APP_ID=cli_xxx
export FEISHU_APP_SECRET=xxx
export FEISHU_CHAT_ID=oc_xxx
python3 report_monitor.py
```

### 4. 定时任务（crontab）

```bash
0 9,12,18 * * * /path/to/run.sh
```

## 📁 目录结构

```
ffagen-annual-report-monitor/
├── SKILL.md              # OpenClaw Skill 定义
├── README.md             # 本文件
├── scripts/
│   ├── report_monitor.py   # 主脚本：爬取+分析+推送
│   ├── feishu_client.py     # 飞书发消息客户端
│   ├── config.py            # 配置读取
│   └── run.sh               # 一键运行脚本
```

## 🔧 数据来源

| 网站 | 地址 | 说明 |
|------|------|------|
| 东方财富 | push2his.eastmoney.com | 年报公告页面 |
| AI财报网 | caireport.com | 业绩大全（备用）|

## 📌 依赖

- Python 3.8+
- requests
- beautifulsoup4
- pandas
- python-dateutil

## ⚠️ 免责声明

- 数据来源于公开网络接口，不保证完整性、准确性和及时性
- 本工具仅供参考学习，不构成任何投资建议
- 投资者据此操作，风险自担

## 📄 开源协议

MIT License

## 🙏 致谢

本项目为个人学习研究用途，基于开源社区精神开发
