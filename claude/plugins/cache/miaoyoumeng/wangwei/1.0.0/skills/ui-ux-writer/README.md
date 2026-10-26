# ui-ux-writer

为 Web 与移动端提供 UI/UX 设计决策。内置可检索的设计数据库：84 种风格、160 套配色、73 组字体搭配、161 种产品类型、98 条 UX 指南、25 种图表类型、104 个图标、16 个技术栈。

## 使用

在 Claude Code 中描述界面设计需求即可触发，例如：

- 「帮我设计一个数据分析仪表盘，深色优先」
- 「这个落地页看起来不够专业，帮我审查一下」
- 「给这个 SaaS 产品选一套配色和字体」
- 「列表滚动卡顿，帮我排查性能问题」

技能会先运行 `--design-system` 生成设计系统，再按需检索细分领域与技术栈，最后按规则清单核对交付质量。

## 手动调用

```bash
cd skills/ui-ux-writer

# 生成设计系统
uv run python scripts/search.py "saas dashboard analytics" --design-system -p "Demo"

# 领域检索
uv run python scripts/search.py "fintech crypto" --domain color -n 3

# 技术栈检索
uv run python scripts/search.py "list performance" --stack react-native
```

## 目录结构

| 路径 | 说明 |
|------|------|
| `SKILL.md` | 触发条件、检索流程、验证方式 |
| `references/ux-rules.md` | 10 类 UX 规则与优先级 |
| `references/app-ui-checklist.md` | App UI 规则与交付前清单 |
| `references/page.md` | 后台管理系统页面布局 |
| `scripts/search.py` | 检索 CLI 入口 |
| `scripts/core.py` | BM25 检索与 CSV 配置 |
| `scripts/design_system.py` | 设计系统生成与持久化 |
| `scripts/sync_data.py` | 数据维护脚本 |
| `assets/data/` | 风格、配色、字体、图表等 CSV 数据集 |
| `evals/evals.json` | 测试用例 |

## 前置条件

Python 3.12 及以上，命令通过 `uv run python` 执行。
