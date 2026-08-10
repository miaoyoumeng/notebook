# ui-vue-validator

Vue 需求开发完成后的视觉验证 skill。通过 Chrome 打开 HTML 静态设计稿和 Vue 开发服务，各自截图做视觉对比，判断功能是否开发完成。适用于任何 Vue 项目的前端视觉验收场景，特别是需要与设计稿逐项核对的情况。

## 何时使用

当用户提到以下场景时自动触发：
- Vue 页面/组件/功能已开发完毕，需要验证
- 对比设计稿与 Vue 实现
- 视觉验收 / 截图核对 / 设计稿一致性检查
- 用户提供了 HTML 设计稿路径和 Vue 项目路径

## 核心工作流程

```
第 1 步：识别路径     → 检测端口、启动服务、输出功能点清单（含响应式列）
第 2 步：HTML 截图    → 通过 file:// 协议访问 HTML 设计稿并截图
第 3 步：Vue 截图     → 访问 Vue 页面，等待渲染稳定后截图
第 4 步：AI 对比      → 配对截图对比（最多 5 对/批），输出差异表格
第 5 步：验证报告     → 生成概览、差异详情、未完成项
第 6 步：验证闭环     → 针对未通过项重新验证（最多 3 轮）
第 7 步：顽固 Issue   → 连续 3 轮未通过 → 生成顽固问题 issue
```

## 关键规则

| 规则 | 说明 |
|------|------|
| 截图配对 | 每个功能点必须有 HTML 设计稿截图（`ui-<prd>-<序号>.png`）和 Vue 实现截图（`vue-<prd>-<序号>.png`） |
| 视口尺寸 | 默认 desktop 1280x720；响应式功能点额外截取 mobile 375x667 |
| 渲染等待 | 截图前必须确认 loading 消失、DOM 稳定、数据已渲染 |
| 严重程度 | High：元素缺失/不可用 \| Medium：颜色/间距偏差 > 4px \| Low：像素级偏差 ≤ 2px |
| 重新验证 | 最多 3 轮，仅针对未通过项 |
| 顽固问题 | 连续 3 轮未通过 → 调用 `/solo:issues-writer` 生成 issue 并记录到 runner.md |

## 目录结构

```
ui-vue-validator/
├── SKILL.md                  # 核心工作流程（7 步）
├── README.md                 # 本文件
├── references/
│   └── severity-guide.md     # 严重程度判定详细指引
└── evals/
    └── evals.json            # 12 个测试用例，覆盖端口检测、截图、对比、报告等场景
```

## 文件存放

所有截图和报告统一存放在 `<当前工作目录>/.claude/logs/ui-vue-validator/<prd-name>/` 目录下。

## 依赖

- Vue 项目（已开发完毕）
- `/solo:playwright-cli` skill（浏览器操作与截图）
- `/solo:issues-writer` skill（顽固问题 issue 生成）

## 端口检测

按 5 级优先级自动识别开发服务器端口：
1. `package.json` 的 `scripts.serve` 中的 `--port` 参数
2. `vite.config.js/ts` 的 `server.port`
3. `vue.config.js` 的 `devServer.port`
4. `.env` / `.env.development` 的 `PORT` 或 `VUE_APP_PORT`
5. fallback：`8000`

检测到端口后，自动检测是否已有进程监听。未启动则执行 `pnpm run serve` 启动。
