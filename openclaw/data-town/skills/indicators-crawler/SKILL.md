---
name: indicators-crawler
description: 抓取政府官方网站内容并解析结构化数据，支持限速、断点续抓，每日限额抓取 240 个政府网页，将抓取的数据提取出关键官方指标，用于后续数据分析。
tools: ["Read", "Grep", "Glob", "Bash","Write", "Edit", "WebFetch"]
---

# 政府统计数据抓取 Skill

抓取 `https://<*>.gov.cn/` 网站内容，解析出"时间"、"区域"、"指标项"、"指标值"，输出为结构化 CSV。

## 工作流程

```
URL列表 → crawler.py(images_2_markdown.py) → markdown文件 → markdown_2_indicators.py → indicators.csv
```

## 脚本

| 脚本 | 功能 |
|------|------|
| `scripts/images_2_markdown.py` | 从 todolist/index.csv 读取 URL，抓取网页内容生成 markdown |
| `scripts/markdown_2_indicators.py` | 读取 markdown 文件，解析为结构化指标 CSV |

## 数据存储目录结构

```
{数据存储目录}/
├── todolist/
│   └── index.csv          # URL 待办列表 (时间,区域,URL)
├── markdowns/              # 生成的 markdown 文件
├── indicators/
│   └── indicators.csv     # 最终指标数据
├── logs/
│   ├── processed_urls.log # 已处理 URL 的 MD5
│   └── processed_md5.log  # 已处理 markdown 的 MD5
```

## 使用方法

### 1. 准备 URL 待办列表

在 `{数据存储目录}/todolist/index.csv` 中写入抓取目标：

```csv
2023,北京市,https://example.gov.cn/data/2023/
2023,上海市,https://example.gov.cn/data/2023/
```

### 2. 抓取网页内容

```bash
uv run python scripts/images_2_markdown.py --dir /path/to/data
```

- 自动断点续跑，已处理 URL 会跳过
- 生成的 markdown 存放在 `{dir}/markdowns/`

### 3. 解析指标数据

```bash
uv run python scripts/markdown_2_indicators.py --dir /path/to/data
```

- 读取 `{dir}/markdowns/*.md`，逐个提交 LLM 解析
- 断点续跑，已处理 markdown 不会重复提交
- 输出 CSV 格式：

```csv
时间,区域,指标项,指标值,来源网址
2023年,北京市,地区生产总值,43760.7亿元,https://...
```

### 4. 批量运行

```bash
# 完整流程
python scripts/images_2_markdown.py --dir /path/to/data
python scripts/markdown_2_indicators.py --dir /path/to/data
```

## 配置参考

- Python >= 3.12
- 依赖通过 `pyproject.toml` 管理，使用 `uv` 安装
- 虚拟环境路径：`.venv/`
