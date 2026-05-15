---
name: gov-crawler
description: 抓取国家各个行政区域官方网站的内容，并解析出数据，支持限速、断点续抓、每日限额，输出 CSV。
tools_required:
  - bash
  - curl
  - sleep
  - echo
  - date
triggers:
  - "抓取北京政府网站数据"
  - "抓取北京发改委数据"
  - "查看当前抓取进度"
---

# Statistics Crawler Skill

本技能利用 `firecrawl` skill 抓取 `https://<*>.gov.cn/` 网站下页面，并自动提取“时间”、“区域”、“指标项”、“指标值”写入 CSV 文件。**完全无 Python 代码**，抓取控制通过 Bash 脚本实现，字段解析由 Agent（LLM）完成。

## 使用方法

### 方式一：一键运行（推荐）

```bash
# 首次完整抓取（自动发现所有页面，限速 3~10 秒/页，每日最多 120 页）
./scripts/crawler.sh --mode full

# 从上次中断处继续
./scripts/crawler.sh --mode resume

# 查看抓取状态（已处理页面数、今日已抓页数、剩余页数）
./scripts/crawler.sh --mode status

# 重置所有状态（从头开始，不清除已有 CSV）
./scripts/crawler.sh --mode reset