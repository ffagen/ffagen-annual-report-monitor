---
id: xiao-zhua/annual-report-monitor
owner_id: xiao-zhua
name: 年报公告监控
description: 定时爬取各大网站当天公布的A股/港股年报公告，筛选重点公司，生成分析报告并发送飞书通知。支持按股票池过滤、重要性分级。
version: 1.0.0
icon: "📊"
author: ffagen
metadata:
  clawdbot:
    emoji: "📊"
    requires:
      bins:
        - python3
        - curl
      env:
        - FEISHU_APP_ID
        - FEISHU_APP_SECRET
        - FEISHU_CHAT_ID
        - MONITORED_STOCKS
        - OUT_DIR
    primaryEnv: FEISHU_APP_ID
    install:
      - id: python-deps
        kind: pip
        packages:
          - requests
          - beautifulsoup4
        label: Install Python dependencies
---

# 📊 年报公告监控

定时爬取东方财富等平台当天公布的年报公告，自动筛选、分类、生成报告并推送到飞书。

## ⚠️ 免责声明

**本工具仅供个人学习与信息参考，不构成任何投资建议。**

- 本工具数据来源于公开网络爬取，不保证数据完整性、准确性和及时性
- 年报内容仅供信息参考，**投资决策需自行研判公司基本面**
- 本项目基于开源社区精神开发，作者不对任何因使用本工具造成的直接或间接损失负责
- 如有侵权，请联系删除

## 环境变量

| 变量 | 必填 | 说明 | 示例 |
|------|------|------|------|
| `FEISHU_APP_ID` | ✅ | 飞书应用 App ID | cli_xxx |
| `FEISHU_APP_SECRET` | ✅ | 飞书应用 Secret | xxx |
| `FEISHU_CHAT_ID` | ✅ | 飞书群/用户 ID | oc_xxx |
| `MONITORED_STOCKS` | 否 | 关注的股票代码（逗号分隔） | 600519,000858 |
| `OUT_DIR` | 否 | 报告输出目录 | ~/Documents/财经信息 |

### 飞书应用权限

- `im:message:send_as_bot` — 发送消息

## 使用方式

```bash
# 设置环境变量
export FEISHU_APP_ID="cli_xxx"
export FEISHU_APP_SECRET="xxx"
export FEISHU_CHAT_ID="oc_xxx"
export MONITORED_STOCKS="600519,000858"  # 可选

# 运行
python3 ~/.openclaw/skills/ffagen__annual-report-monitor/scripts/report_monitor.py

# 定时任务示例（crontab）
0 9,12,18 * * 1-5 /usr/bin/python3 ~/.openclaw/skills/ffagen__annual-report-monitor/scripts/report_monitor.py
```

## 功能说明

### 数据来源
- **东方财富**：`np-anotice-stock.eastmoney.com` 年报公告页面

### 筛选规则
- 当天新公布年报
- 过滤摘要、英文、更新类公告
- 标注业绩增长/下滑/扭亏/ST等关键类型

### 输出内容
- 📋 当天公布年报公司列表
- 📈 业绩变化标注（📈/📉/⚠️）
- 🔗 公告原文链接

## 文件结构

```
ffagen__annual-report-monitor/
├── SKILL.md                # 本文件
└── scripts/
    ├── report_monitor.py   # 主脚本
    ├── config.py           # 配置
    └── feishu_client.py    # 飞书客户端
```

## 依赖

- Python 3.8+
- requests
- beautifulsoup4
