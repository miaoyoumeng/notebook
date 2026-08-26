# vue-coder

Vue 3 全栈开发专家 Skill。为 Claude Code 提供从 PRD 解析到编译通过的完整 Vue 3 + TypeScript 开发工作流。

## 适用场景

当你需要以下功能时，此 skill 会自动触发：

- **页面开发**：创建 Vue 3 管理后台页面、表单/表格/弹窗组件
- **数据可视化**：ECharts 图表（折线图、柱状图、饼图、雷达图、仪表盘、热力图、桑基图、漏斗图、K 线图等）
- **状态管理**：Pinia store 创建、持久化配置
- **TypeScript 集成**：类型定义、泛型、接口声明
- **组件库布局**：TDesign Vue Next 组件（72 个组件全量参考）
- **TDD 测试**：单元测试编写、覆盖率提升、bug 修复
- **API 对接**：Axios 封装、接口定义、Mock 数据

即使未明确说"使用 Vue"，只要涉及 `.vue` 文件、组件开发、响应式数据、computed/ref、watch 等 Vue 3 概念，也会触发此 skill。

## 快速入门

告诉 Claude 你的需求，包含以下信息效果最佳：

```
帮我创建一个用户管理页面，路由路径是 /system/user，
需要展示用户列表表格，包含搜索框、状态筛选、分页功能。
PRD 在 docs/prd/user-manage.md，UI 设计稿在 docs/ui/user-list.html。
```

Claude 会按以下工作流自动推进：

1. 解析 PRD 和 UI 设计稿
2. 使用 TDesign 组件画静态页面
4. 定义数据模型 + Mock 数据
5. 封装业务逻辑函数
6. 页面组装与事件绑定
7. 格式化 + 编译验证
8. 检查功能点完成情况

## 核心能力

### 技术栈

| 技术 | 用途 |
|------|------|
| Vue 3 | Composition API + `<script setup lang="ts">` |
| TypeScript | 类型安全、泛型、接口 |
| TDesign Vue Next | 页面布局组件（72 个） |
| ECharts + vue-echarts | 数据可视化（11 种图表） |
| Pinia | 状态管理 |
| Axios | HTTP 请求封装 |

### 4 条核心规则

| # | 规则 | 说明 |
|---|------|------|
| 1 | **仅用 TDesign 组件** | 布局只能使用 `tdesign-vue-next`，禁止其他布局库 |
| 2 | **API 调用封装** | 禁止组件内直接调 API，必须通过 `request/` + `api/` + `stores` |
| 3 | **Mock 数据先行** | 先写 JSON mock 再开发交互逻辑，禁止跳过 mock |
| 4 | **TDD 铁律** | 没有失败的测试之前，禁止写产品代码 |

## 开发工作流

```
PRD 解析 → Vue 页面开发 → 数据模型 → Mock 数据 → 业务逻辑封装 → 页面组装 → 格式构建 → 验证
```

详细流程图见 [SKILL.md](SKILL.md) 中的 mermaid 图。

## 参考文档索引

### 核心参考

| 文档 | 内容 | 何时阅读 |
|------|------|----------|
| [vue-component-patterns](references/vue-component-patterns.md) | 组件模式、Props/事件设计、性能优化 | 开发业务组件时 |
| [echart-component-chart-guide](references/echart-component-chart-guide.md) | ECharts 图表决策树、按需引入 | 开发图表时 |
| [api-guide](references/api-guide.md) | Axios 封装、API 定义、Mock 数据 | 定义接口时 |
| [vue-state-management](references/vue-state-management.md) | Pinia store、Options Store、持久化 | 状态管理时 |
| [typescript-testing-guide](references/typescript-testing-guide.md) | 测试策略、Vue/E2E 测试、覆盖率 | 编写测试时 |

### TDesign 组件（72 个）

完整组件列表见 [SKILL.md](SKILL.md) 中的 TDesign 组件表格。常用组件快速索引：

- **布局**：Layout, Grid, Space, Divider
- **导航**：Menu, Tabs, Breadcrumb, Pagination, Steps
- **表单**：Form, Input, Select, DatePicker, Upload, Checkbox, Radio
- **展示**：Table, Card, List, Tree, Tag, Avatar, Badge
- **反馈**：Dialog, Drawer, Message, Notification, Loading, Alert

### ECharts 图表（11 种）

| 图表类型 | 参考文档 |
|---------|---------|
| 折线图/面积图 | [LineChart](references/echart-component-linechart.md) |
| 柱状图 | [BarChart](references/echart-component-barchart.md) |
| 饼图/环形图 | [PieChart](references/echart-component-piechart.md) |
| 散点图/气泡图 | [ScatterChart](references/echart-component-scatterchart.md) |
| 雷达图 | [RadarChart](references/echart-component-radarchart.md) |
| 仪表盘 | [GaugeChart](references/echart-component-gaugechart.md) |
| 热力图 | [HeatmapChart](references/echart-component-heatmapchart.md) |
| 漏斗图 | [FunnelChart](references/echart-component-funnelchart.md) |
| 树形图 | [TreemapChart](references/echart-component-treemapchart.md) |
| 桑基图 | [SankeyChart](references/echart-component-sankeychart.md) |
| K 线图 | [CandlestickChart](references/echart-component-candlestickchart.md) |

## 项目结构

```
src/
├── api/                  # API 接口
├── assets/               # 图片 / 全局样式 / JSON mock 数据
├── components/           # 通用业务组件
├── layouts/              # 布局框架
├── request/              # Axios 封装 + 拦截器
├── stores/               # Pinia 状态管理
├── views/                # 业务视图
├── App.vue
└── main.ts               # 入口文件
```


### 测试用例

- **12 个 eval 用例**，97 个断言
- 覆盖：页面布局、图表开发、Pinia store、TDD 测试、工具函数、Bug 修复
- 详细测试集见 [evals/evals.json](evals/evals.json)
