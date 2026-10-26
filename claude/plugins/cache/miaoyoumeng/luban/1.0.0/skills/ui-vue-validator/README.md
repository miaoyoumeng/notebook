# ui-vue-validator

Vue 需求开发完成后的视觉验收技能。用浏览器分别打开 HTML 静态设计稿与 Vue 开发服务，逐功能点截图并做视觉对比，输出差异清单与验证报告。

## 何时使用

- Vue 页面、组件或功能开发完毕，需要验证与设计稿是否一致。
- 用户提供 HTML 设计稿路径与 Vue 项目路径，要求视觉验收。
- 用户提到对比设计稿、截图核对、还原度检查、UI 走样排查。
- 用户要求对上一轮未通过的功能点重新验证。

## 核心流程

```text
第 1 步：识别输入     → 检测端口、启动服务、输出功能点清单（含响应式列）
第 2 步：HTML 截图    → 通过 file:// 协议访问 HTML 设计稿并截图
第 3 步：Vue 截图     → 访问 Vue 页面，等待渲染稳定后截图
第 4 步：AI 对比      → 配对截图对比（每批最多 5 对），输出差异表格
第 5 步：验证报告     → 生成概览、差异详情、未完成项
第 6 步：重新验证     → 仅针对未通过项，累计最多 3 轮
第 7 步：顽固 Issue   → 连续 3 轮未通过 → 生成 issue 并登记
```

## 关键规则

| 规则 | 说明 |
|------|------|
| 截图配对 | 每个功能点必须有 `ui-<prd>-<序号>.png` 与 `vue-<prd>-<序号>.png` |
| 视口尺寸 | 默认 desktop 1280x720；响应式功能点额外截取 mobile 375x667 |
| 渲染等待 | 截图前确认 loading 消失、DOM 稳定、数据已渲染 |
| 严重程度 | High：元素缺失或功能不可用；Medium：颜色、间距偏差超过 4px；Low：像素级偏差不超过 2px |
| 重新验证 | 最多 3 轮，仅针对未通过项 |
| 顽固问题 | 连续 3 轮未通过 → 调用 `fangdu:issues-writer` 生成 issue |

## 目录结构

```text
ui-vue-validator/
├── SKILL.md                  # 触发条件与 7 步流程
├── README.md                 # 本文件
├── references/
│   └── severity-guide.md     # 严重程度判定指引
├── scripts/                  # 预留，当前无脚本
├── assets/                   # 预留，当前无资源
└── evals/
    └── evals.json            # 测试用例
```

## 文件存放

截图、报告与 issue 存放在 `<当前工作目录>/.claude/logs/ui-vue-validator/<prd-name>/`。顽固问题生成后登记到 `<当前工作目录>/.claude/issues/todolist.md`。

## 依赖

- Vue 项目，功能已开发完毕。
- `pangu:playwright-cli`：浏览器操作与截图。
- `fangdu:issues-writer`：顽固问题 issue 生成。

## 端口检测

按顺序读取，取第一个命中的值：

1. `package.json` 的 `scripts.serve` 中的 `--port` 参数。
2. `vite.config.js` / `vite.config.ts` 的 `server.port`。
3. `vue.config.js` 的 `devServer.port`。
4. `.env` / `.env.development` 的 `PORT` 或 `VUE_APP_PORT`。
5. 兜底值 `8000`。

检测端口是否已有进程监听，未启动时执行 `pnpm run serve`。
