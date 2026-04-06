# 📊 Annual Report Monitor - 年报公告监控

> 爬取 A股/港股年报公告 | 智能筛选 | 飞书推送

## ⚠️ Disclaimer / 免责声明

**本工具仅供个人学习与信息参考，不构成任何投资建议。**

**This tool is for educational and informational purposes only. It does not constitute any investment advice.**

- 数据来源于公开网络爬取，不保证准确性 | Data sourced from public web scraping — no accuracy guarantee
- 年报内容仅供信息参考，投资决策需自行研判基本面 | Annual report content is for reference only; investment decisions require your own fundamental analysis
- **投资风险自担 | Investment decisions are made at your own risk**
- 本项目基于开源社区精神开发 | Developed in the spirit of the open-source community
- 如有侵权请联系删除 | For any copyright concerns, please contact for removal

## ✨ Features

- 📋 **多源爬取** — 东方财富年报公告
- 🔍 **智能筛选** — 业绩增长/下滑/扭亏/ST 自动标注
- 🎯 **自选股过滤** — 仅推送持仓相关年报（可选）
- 🔔 **飞书推送** — 每日定时推送年报速递

## 📦 Installation

### Environment Variables / 环境变量

```bash
export FEISHU_APP_ID="cli_xxx"           # 必填 | Required
export FEISHU_APP_SECRET="xxx"            # 必填 | Required
export FEISHU_CHAT_ID="oc_xxx"           # 必填 | Required
export MONITORED_STOCKS="600519,000858"  # 可选 | Optional
export OUT_DIR="~/Documents/财经信息"      # 可选 | Optional
```

### Install Dependencies / 安装依赖

```bash
pip install requests beautifulsoup4
```

### Run / 运行

```bash
python3 ~/.openclaw/skills/ffagen__annual-report-monitor/scripts/report_monitor.py
```

### Cron Example / 定时任务示例

```bash
# Run at 9am, 12pm, 6pm on weekdays / 工作日9点、12点、18点运行
0 9,12,18 * * 1-5 /usr/bin/python3 ~/.openclaw/skills/ffagen__annual-report-monitor/scripts/report_monitor.py
```

## 📖 Usage Examples / 使用示例

```
"帮我查一下今天有哪些公司公布了年报"
"运行年报监控"
"生成本周的年报汇总报告"
```

## 📊 Output Sample / 输出示例

飞书推送内容：
- 📊 **X月X日年报公告速递**
- 📋 当天公布年报公司列表
- 📈/📉/⚠️ 业绩变化标注
- 公告原文链接

## 📁 File Structure / 文件结构

```
ffagen__annual-report-monitor/
├── SKILL.md                # Skill definition
└── scripts/
    ├── report_monitor.py   # Main script
    ├── config.py           # Configuration
    └── feishu_client.py    # Feishu client
```

## 📌 Requirements / 依赖

- Python 3.8+
- requests
- beautifulsoup4

## 📄 License

MIT License
