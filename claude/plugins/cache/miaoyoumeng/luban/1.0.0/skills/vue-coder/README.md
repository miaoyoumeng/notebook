# vue-coder

Vue 3 + TypeScript 全栈开发技能，覆盖从 PRD 解析到编译构建的完整工作流。

## 能力范围

- 页面布局：tdesign-vue-next
- 图表开发：echarts / vue-echarts，支持折线图、柱状图、饼图、雷达图、仪表盘、热力图、桑基图、漏斗图、K 线图等 11 种图表
- 工程流程：mock 数据先行 → API 封装 → 业务逻辑封装 → 组件提取 → 页面组装
- 完成标准：`pnpm run build` 编译通过

## 使用方式

把 `luban/skills/vue-coder` 目录放入 Claude 的技能路径后，在对话中描述 Vue 3 页面开发任务即可自动触发。也可以显式要求「使用 vue-coder 技能」。

触发示例：

- 「用 Vue 3 做一个设备管理后台页面，带表格和新增弹窗」
- 「把这份 PRD 实现成页面，图表用 echarts」
- 「这段 Composition API 报类型错误，帮我修一下」

## 目录结构

```text
vue-coder/
├── SKILL.md        # 技能指令正文
├── README.md       # 本文件
├── scripts/        # 确定性可执行脚本
├── references/     # 按需加载的参考文档
├── assets/         # 模板与资源文件
└── evals/
    └── evals.json  # 测试用例
```

## 完善与验证

- 补全或修改正文：`/pangu:commander-skill luban improve vue-coder`
- 编写测试用例：`/pangu:commander-skill luban evals vue-coder`
- 静态评分：`/pangu:commander-skill luban score vue-coder`
