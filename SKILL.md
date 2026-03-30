---
id: xiao-zhua/ffagen-annual-report-monitor
owner_id: xiao-zhua
name: 年报公告监控
description: 定时爬取各大网站当天公布的A股/港股年报公告，筛选重点公司，生成分析报告并发送飞书通知。支持按股票池过滤、重要性分级。
version: 1.0.0
icon: "\U0001F4CA"
author: investor
metadata:
  clawdbot:
    emoji: "\U0001F4CA"
    requires:
      bins:
        - python3
        - curl
      env:
        - FEISHU_APP_ID
        - FEISHU_APP_SECRET
        - FEISHU_CHAT_ID
        - MONITORED_STOCKS
    primaryEnv: FEISHU_APP_ID
    install:
      - id: python-deps
        kind: pip
        packages:
          - requests
          - beautifulsoup4
          - pandas
          - python-dateutil
        label: Install Python dependencies
---

# 📊 年报公告监控

定时爬取东方财富/AI财报网等平台当天公布的年报公告，自动筛选、分类、生成报告并推送到飞书。

## ⚙️ 配置

### 环境变量

| 变量 | 必填 | 说明 | 示例 |
|------|------|------|------|
| `FEISHU_APP_ID` | ✅ | 飞书应用 App ID | cli_xxx |
| `FEISHU_APP_SECRET` | ✅ | 飞书应用 Secret | xxx |
| `FEISHU_CHAT_ID` | ✅ | 飞书群/用户 ID | oc_xxx |
| `MONITORED_STOCKS` | 否 | 关注的股票代码（逗号分隔） | 600519,000858 |
| `CHECK_INTERVAL` | 否 | 检查间隔（小时） | 4（默认4） |

### 飞书应用权限

- `im:message:send_as_bot` — 发送消息
- `drive:drive` — 云文档操作（如需上传报告）

## 🚀 使用方式

```
"帮我查一下今天有哪些公司公布了年报"
"运行年报监控"
"生成本周的年报汇总报告"
```

## 📋 功能说明

### 1. 数据来源
- **东方财富**：`push2his.eastmoney.com` 年报公告页面
- **AI财报网**：业绩大全页面（备用）
- 支持A股/港股

### 2. 筛选规则
- 过滤条件：当天公布、业绩增长/下滑前五、重大亏损
- 关键词：净利润增长、业绩下滑、ST、扭亏为盈
- 如设置 `MONITORED_STOCKS` 则只推送持仓股

### 3. 输出内容
- 📋 当天公布年报公司列表
- 📈 业绩增速排名（Top5 / Flop5）
- 🔍 重点公司摘要
- 📎 详细报告链接

### 4. 报告格式
发送飞书富文本消息，包含：
- 标题：📊 X月X日年报公告速递
- 表格：股票代码 | 股票名称 | 净利润增速 | 重要事项
- 简评：整体披露情况分析

## 📁 脚本结构

```
scripts/
├── report_monitor.py      # 主脚本：爬取+分析+推送
├── feishu_client.py       # 飞书发消息客户端
├── config.py              # 配置读取
└── run.sh                 # 一键运行脚本
```

## 🔧 本地调试

```bash
cd ~/.openclaw/skills/investor__annual-report-monitor/scripts
python3 report_monitor.py

# 或设置定时任务（crontab）
0 9,12,18 * * * /path/to/run.sh
```

## 📌 依赖

- Python 3.8+
- requests
- beautifulsoup4
- pandas
- python-dateutil
