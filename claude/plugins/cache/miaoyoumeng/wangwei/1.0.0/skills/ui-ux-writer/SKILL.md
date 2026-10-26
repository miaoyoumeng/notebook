---
name: ui-ux-writer
description: "为 Web 与移动端提供 UI/UX 设计决策：规划页面、选择风格与配色、确定字体与布局、实现组件、审查无障碍与交互质量。内置 84 种风格、160 套配色、73 组字体搭配、161 种产品类型、98 条 UX 指南、25 种图表类型、104 个图标与 16 个技术栈的可检索数据库，通过 BM25 检索与推理规则生成设计系统。当用户要设计或重构界面、挑选风格配色字体、制作落地页或仪表盘、添加图表、检查无障碍与交互、优化界面观感，或提到 UI、UX、设计系统、暗色模式、响应式、组件库时使用本技能，即使用户没有明确说「设计」。"
---

# ui-ux-writer

## 概述

提供可检索的 UI/UX 设计知识库与推荐流程。数据覆盖 84 种风格、160 套配色、73 组字体搭配、161 种产品类型、98 条 UX 指南、25 种图表类型、104 个图标、16 个技术栈；检索使用 BM25 排序，`--design-system` 结合推理规则输出完整设计系统。

本技能输出设计决策与实现建议，不产出视觉稿文件。

## 上下文层级

按下列顺序取用信息，前一层不足时进入下一层：

| 层级 | 内容 | 获取方式 |
|------|------|----------|
| 决策流程 | 触发条件、检索步骤、交付方式 | 本文件 |
| 规则清单 | 10 类 UX 规则、优先级与反模式 | `references/ux-rules.md` |
| App 检查表 | 图标、交互、明暗模式、布局、无障碍检查项 | `references/app-ui-checklist.md` |
| 页面布局 | 后台管理系统页面结构 | `references/page.md` |
| 数据集 | 风格、配色、字体、产品、图表、图标、技术栈 | `assets/data/*.csv`，经 `scripts/search.py` 检索 |

## 使用时机

满足下列任一条件时使用：

- 设计新页面：落地页、仪表盘、管理后台、SaaS、移动应用
- 创建或重构 UI 组件：按钮、模态框、表单、表格、图表
- 选择配色方案、字体系统、间距标准或布局系统
- 审查 UI 的无障碍性、交互质量或视觉一致性
- 实现导航结构、动画或响应式行为
- 做出产品级设计决策：风格、信息层级、品牌表达
- 界面「不够专业」但原因不明，或收到可用性反馈
- 跨平台设计对齐、构建设计系统或组件库

按场景确定起始步骤：

| 场景 | 起始步骤 |
|------|----------|
| 新项目、新页面 | 第 1 步 → 第 2 步 |
| 新组件或单个界面元素 | 第 4 步（`--domain style`、`--domain ux`） |
| 选择风格、配色、字体 | 第 2 步 |
| 审查现有 UI、修复界面问题 | 第 6 步，按 `references/ux-rules.md` 定位条目 |
| 实现暗色模式 | 第 4 步（`--domain style "dark mode"`）+ 第 6 步核对 §6 |
| 添加图表或数据可视化 | 第 4 步（`--domain chart`） |
| 技术栈最佳实践 | 第 5 步 |

不适用：纯后端逻辑、API 或数据库设计、与界面无关的性能优化、基础设施与 DevOps、非可视化脚本。

判断标准：任务会改变界面的外观、感受、动效或交互方式时使用。

## 编码四原则

1. **检索先行**：风格、配色、字体、效果取自 `--design-system` 或 `--domain` 的检索结果，不自行指定色值与字体。
2. **令牌化**：颜色、间距、字号以语义令牌表达，组件内不写原始色值。
3. **无障碍内建**：对比度、聚焦环、触摸目标在实现时满足，不推迟到交付前修补。
4. **移动优先**：先按最小视口实现，再用断点扩展，容器不使用固定 px 宽度。

## 流程

以下命令均以技能根目录为工作目录：

```bash
cd <插件根目录>/skills/ui-ux-writer
```

### 第 1 步：分析需求

从请求中提取四项输入：

| 变量 | 取值 |
|------|------|
| 产品类型 | 社交、电商、金融、医疗、工具、生产力等 |
| 目标受众 | C 端或 B 端；年龄、使用场景、熟练度 |
| 风格关键词 | 极简、活力、暗色、内容优先、沉浸式等 |
| 技术栈 | 见第 5 步支持的 16 个栈；未指定时按项目现状 |

### 第 2 步：生成设计系统（必须）

```bash
uv run python scripts/search.py "<产品类型> <行业> <关键词>" --design-system [-p "项目名"]
```

该命令并行检索 product、style、color、landing、typography，再按 `assets/data/ui-reasoning.csv` 的推理规则选出最佳组合，输出模式、风格、颜色、字体、效果与反模式。

```bash
uv run python scripts/search.py "beauty spa wellness service" --design-system -p "Serenity Spa"
```

### 第 3 步：持久化设计系统（跨会话时）

需要跨会话保留设计决策时追加 `--persist`：

```bash
uv run python scripts/search.py "<查询>" --design-system --persist -p "项目名" [--page "dashboard"]
```

生成 `design-system/<项目名>/MASTER.md` 作为全局事实源；带 `--page` 时同时生成 `design-system/<项目名>/pages/<页面>.md` 作为页面级覆盖。目录名取项目名的小写形式，空格替换为连字符。

检索顺序：先读页面级文件，存在则覆盖 MASTER；不存在则只用 MASTER。

### 第 4 步：按需补充领域检索

```bash
uv run python scripts/search.py "<关键词>" --domain <domain> [-n <条数>]
```

| 领域 | 用途 | 示例 |
|------|------|------|
| `product` | 产品类型模式 | `--domain product "entertainment social"` |
| `style` | 风格、颜色、效果 | `--domain style "glassmorphism dark"` |
| `color` | 配色方案 | `--domain color "fintech crypto"` |
| `typography` | 字体搭配 | `--domain typography "playful modern"` |
| `google-fonts` | 单个 Google 字体 | `--domain google-fonts "sans serif variable"` |
| `landing` | 落地页结构 | `--domain landing "hero social-proof"` |
| `chart` | 图表类型与库 | `--domain chart "real-time dashboard"` |
| `ux` | UX 规则与反模式 | `--domain ux "animation accessibility"` |
| `icons` | 图标库与用法 | `--domain icons "navigation arrow"` |
| `react` | React/Next.js 性能 | `--domain react "rerender memo list"` |
| `web` | App 界面指南 | `--domain web "accessibilityLabel touch safe-areas"` |

未指定 `--domain` 时按查询词自动判定领域。

### 第 5 步：技术栈检索

```bash
uv run python scripts/search.py "<关键词>" --stack <stack>
```

可用技术栈：`react`、`nextjs`、`vue`、`svelte`、`astro`、`swiftui`、`react-native`、`flutter`、`nuxtjs`、`nuxt-ui`、`html-tailwind`、`shadcn`、`jetpack-compose`、`threejs`、`angular`、`laravel`。

### 第 6 步：核对规则并实现

实现前读取 `references/ux-rules.md`，按优先级 1→10 核对相关条目；App UI 追加 `references/app-ui-checklist.md`。设计决策以第 2 步输出为准，不自行指定配色与字体。

### 第 7 步：交付

输出内容包含：

1. 设计系统：模式、风格、配色、字体、效果
2. 关键页面的结构与交互说明
3. 与规则的对应关系：用到的条目与规避的反模式
4. 遗留风险：未满足项及原因

交付文档模板：

```markdown
# <项目名> 设计交付

## 设计系统
- 模式：<检索得到的页面模式>
- 风格：<风格名称与关键词>
- 配色：<主色、辅色、强调色、背景、前景、语义色>
- 字体：<标题字体、正文字体>
- 效果：<阴影、圆角、动效>

## 页面结构与交互
- <页面名>：<区块顺序与交互说明>

## 规则对应
- 使用的条目：<规则 ID>
- 规避的反模式：<反模式名称>

## 遗留风险
- <未满足项与原因>
```

`--design-system` 的输出需要文档格式时追加 `-f markdown`；终端查看使用默认 `ascii`。

查询策略：组合产品、行业、基调、密度等多维关键词，如 `"entertainment social vibrant content-dense"`；结果不满意时更换关键词重跑，仍不确定再用 `--domain` 深入单个维度。

### 示例工作流

需求："做一个 AI 搜索首页。"

```bash
# 第 1 步：产品类型为工具，受众为 C 端，关键词为现代、极简、内容优先
# 第 2 步：生成设计系统
uv run python scripts/search.py "AI search tool modern minimal" --design-system -p "AI Search"

# 第 4 步：补充风格与交互规则
uv run python scripts/search.py "minimalism dark mode" --domain style
uv run python scripts/search.py "search loading animation" --domain ux

# 第 5 步：技术栈指南
uv run python scripts/search.py "list performance navigation" --stack react-native
```

综合设计系统与检索结果实现界面，第 6 步核对规则后交付。

## 代码分析

检索链路：`search.py` 是唯一入口；`--design-system` 分支调用 `design_system.py`，其余分支调用 `core.py`；`design_system.py` 复用 `core.py` 的 `search()` 与 `DATA_DIR`。`sync_data.py` 独立运行，不依赖其他脚本。

| 脚本 | 用途 | 调用方式 |
|------|------|----------|
| `scripts/search.py` | 检索 CLI：领域检索、技术栈检索、设计系统生成与持久化 | `uv run python scripts/search.py "fintech crypto" --domain color -n 3` |
| `scripts/core.py` | CSV 配置、BM25 算法、领域自动判定 | 由 `search.py`、`design_system.py` 导入，不单独执行 |
| `scripts/design_system.py` | 设计系统生成，输出 ascii/markdown，持久化 MASTER 与页面覆盖 | 由 `search.py --design-system` 调用，不单独执行 |
| `scripts/sync_data.py` | 依据 `products.csv` 重建 `colors.csv` 与 `ui-reasoning.csv` | `uv run python scripts/sync_data.py` |

数据集：`assets/data/*.csv` 为 14 个领域数据集，`assets/data/stacks/*.csv` 为 16 个技术栈数据集。`core.py` 的 `CSV_CONFIG` 定义 11 个检索领域，`STACK_CONFIG` 定义 16 个技术栈。

## 验证清单

- [ ] 已运行 `--design-system`，风格、配色、字体来自检索结果
- [ ] 普通文本对比度 ≥4.5:1，大文本 ≥3:1
- [ ] 触摸目标 ≥44×44pt（iOS）/ 48×48dp（Android），间距 ≥8px
- [ ] 移动端无横向滚动，正文 ≥16px
- [ ] 悬停、按下、聚焦、禁用四种状态齐备且视觉可区分
- [ ] 破坏性操作有二次确认
- [ ] 图表有图例、轴标签与表格替代方案
- [ ] 亮色与暗色模式分别验证对比度
- [ ] 动画 150–300ms，仅使用 transform/opacity
- [ ] App UI 已逐项核对 `references/app-ui-checklist.md`

## 危险信号

| 错误模式 | 表现 | 修正 |
|----------|------|------|
| 跳过设计系统 | 未运行 `--design-system` 直接写代码 | 先检索，再实现 |
| 自由发挥配色 | 自行指定十六进制色值 | 使用检索结果或语义化令牌 |
| Emoji 当图标 | 导航或控件中使用 🎨 🚀 | 使用 SVG 图标（Lucide、Heroicons） |
| 仅用颜色表意 | 错误状态只变红，不加图标或文字 | 颜色 + 图标 + 文字 |
| 移除聚焦环 | `outline: none` 且无替代样式 | 保留 2–4px 可见聚焦环 |
| 只靠悬停 | 主交互仅在 hover 时可用 | 点击或轻触触发，悬停仅作增强 |
| 固定宽度 | 移动端固定 px 容器导致横向滚动 | 移动优先断点与弹性布局 |
| 动画过度 | 时长 >500ms，或对 width/height 做动画 | 150–300ms，仅 transform/opacity |

## 常见卡点

| 问题 | 处理方法 |
|------|----------|
| 无法决定风格或配色 | 换一组关键词重跑 `--design-system` |
| 暗色模式对比度不足 | `ux-rules.md` §6：`color-dark-mode`、`color-accessible-pairs` |
| 动画不自然 | §7：`spring-physics`、`easing`、`exit-faster-than-enter` |
| 表单体验差 | §8：`inline-validation`、`error-clarity`、`focus-management` |
| 导航混乱 | §9：`nav-hierarchy`、`bottom-nav-limit`、`back-behavior` |
| 小屏布局崩溃 | §5：`mobile-first`、`breakpoint-consistency` |
| 列表卡顿 | §3：`virtualize-lists`、`main-thread-budget`、`debounce-throttle` |

## 理由辩解

| 理由 | 驳回依据 |
|------|----------|
| "直接写代码更快" | 风格、配色、字体各凭感觉，返工时逐处替换的成本高于一次检索 |
| "设计系统输出太长" | 用 `-f markdown` 或 `-n` 控制篇幅；省略检索会遗漏反模式 |
| "先做出来再优化" | 布局与配色改动波及面大，事后优化的成本高于开始前确认 |
| "小改动不用查规则" | 无障碍与触摸目标的最低值必须在写入时满足，事后补漏更容易遗漏 |
| "配色看着差不多" | 未经对比度验证的配色在暗色模式与弱光环境下不可读 |

## 验证

以下命令在技能根目录执行，与「验证清单」互补：

1. 环境：`uv run python --version` 能输出版本号
2. 数据完整：`ls assets/data/*.csv | wc -l` 输出 14；`ls assets/data/stacks/*.csv | wc -l` 输出 16
3. 检索自检：`uv run python scripts/search.py "fintech crypto" --domain color -n 1` 输出含 `Found: 1 results`
4. 设计系统自检：`uv run python scripts/search.py "saas dashboard" --design-system -f markdown` 输出含 `### Pattern`、`### Style`、`### Colors`
5. 错误路径：`uv run python scripts/search.py "test" --stack unknown` 输出包含可用技术栈清单的报错
6. 引用完整：`diff <(grep -o 'references/[a-z-]*\.md' SKILL.md | sort -u) <(ls references/ | sed 's|^|references/|')` 输出为空

## 实现检查表

实现过程中逐项确认：

- [ ] 四项输入已明确：产品类型、目标受众、风格关键词、技术栈
- [ ] 已运行 `--design-system`，配色与字体全部来自其输出
- [ ] 涉及的 UX 规则条目已在 `references/ux-rules.md` 中定位
- [ ] App UI 已按 `references/app-ui-checklist.md` 的「应该」列落地
- [ ] 交互组件已实现全部状态，不只默认态
- [ ] 断点与目标技术栈的约定一致

## 参考资料

| 资源 | 内容 | 何时读取或调用 |
|------|------|----------------|
| `references/ux-rules.md` | 10 类 UX 规则、优先级与反模式 | 实现或审查前，按优先级核对 |
| `references/app-ui-checklist.md` | App UI 通用规则与交付前清单 | 交付 App UI 前 |
| `references/page.md` | 后台管理系统页面布局 | 设计管理后台页面时 |
| `scripts/search.py` | 检索 CLI：领域检索、技术栈检索、设计系统生成与持久化 | 第 2–5 步 |
| `scripts/core.py` | 检索库：CSV 配置、BM25 算法、领域判定 | 由 `search.py` 导入，不单独调用 |
| `scripts/design_system.py` | 设计系统生成与持久化 | 由 `search.py` 导入，不单独调用 |
| `scripts/sync_data.py` | 维护脚本：依据 `products.csv` 重建 `colors.csv` 与 `ui-reasoning.csv` | 数据维护时执行 `uv run python scripts/sync_data.py` |
