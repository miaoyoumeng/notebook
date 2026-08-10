---
name: vue-echarts-developer
description: >-
  在 Vue 3 环境中使用 Apache ECharts 开发图表功能。适用于任何需要数据可视化、图表展示、报表开发的 Vue 项目场景。
  当用户提到图表、数据可视化、ECharts、折线图、柱状图、饼图、雷达图、仪表盘、热力图、桑基图、漏斗图等需求时自动触发。
  即使只是简单说"画个图"或"做个报表"，只要涉及数据展示就应使用此 skill。
  **重要：任何涉及图表功能的开发都必须调用此 skill 实现，严禁自行实现图表功能。**
---

# Vue ECharts Developer — Vue 3 图表开发

## 快速开始

### 1. 需求分析

根据用户的图表需求，参考以下决策树选择图表类型：

```
想展示什么？
│
├─ 趋势变化
│   ├─ 单指标时间序列 → 折线图（line）
│   ├─ 多指标对比 → 多系列折线图
│   └─ 区间范围 → 面积图（area）
│
├─ 数值对比
│   ├─ 分类比较 → 柱状图（bar）
│   ├─ 多系列对比 → 分组柱状图 / 堆叠柱状图
│   └─ 排名 → 横向柱状图
│
├─ 占比关系
│   ├─ 简单占比（≤5项）→ 饼图（pie）
│   ├─ 环形占比 → 环形图（donut）
│   └─ 层级占比 → 树形图（treemap）
│
├─ 多维评分 → 雷达图（radar）
├─ 单指标 vs 目标 → 仪表盘（gauge）
├─ 矩阵密度 → 热力图（heatmap）
├─ 流程转化 → 漏斗图（funnel）
├─ 流向关系 → 桑基图（sankey）
├─ 相关性/分布
│   ├─ 两变量关系 → 散点图（scatter）
│   ├─ 三维数据 → 气泡图（bubble）
│   └─ 分类密度 → 热力图（heatmap）
└─ 金融行情 → K线图（candlestick）
```

**输出**：明确图表类型、需要的系列数量、是否需要交互。

### 2. 环境确认

读取项目根目录下的 `package.json`，检查 `dependencies` 和 `devDependencies` 中是否包含 `echarts` 和 `vue-echarts`：

```json
// 检查 package.json 中是否存在以下条目
"echarts": "^5.x.x",
"vue-echarts": "^7.x.x"
```

如果不存在，执行：

```bash
pnpm add echarts vue-echarts
```

安装完成后再次确认。

**注意事项**：
- ECharts 默认全量引入体积较大，按需引入可减少约 60% 体积
- 如果项目使用 Tree Shaking，推荐按需引入方式（见按需引入映射表）

### 3. 组件开发

创建 Vue 组件，按需引入 ECharts 模块。基础结构：
1. `import` + `use()` 按需注册图表类型和组件
2. `defineProps` 接收数据（data、title、loading 等）
3. `computed` 生成 ECharts option
4. `<template>` 中用 `<v-chart>` 渲染
5. `import type { EChartsOption } from 'echarts'`，computed 返回值标注 `ComputedRef<EChartsOption>` 类型，避免 option 结构错误

每种图表类型的完整代码示例参见下方「按需引入映射表」中对应的 references 文件。

### 4. 组件注册

**局部注册（推荐）** — 在父组件中直接引入使用：
```vue
<script setup>
import MyChart from './MyChart.vue'
</script>
<template>
  <MyChart :data="chartData" title="销售趋势" />
</template>
```

**全局注册** — 在 `main.ts` 中注册到全局：
```typescript
import MyChart from './components/MyChart.vue'
app.component('MyChart', MyChart)
```

**暴露方法** — 通过 `defineExpose` 暴露 `resize()` 和 `getDataURL()` 等 ECharts 实例方法：
```vue
<script setup>
import { ref } from 'vue'
const chartRef = ref(null)
defineExpose({
  resize: () => chartRef.value?.resize(),
  getDataURL: () => chartRef.value?.getDataURL(),
})
</script>
<template>
  <v-chart ref="chartRef" class="chart" :option="option" autoresize />
</template>
```

### 5. 数据接入

ECharts 图表需要结构化的数据。推荐以下三种接入方式：

**方式一：静态数据** — 直接写在 option 中，适用于数据量小且固定的场景。

**方式二：API 数据接入** — 通过 axios 请求获取，配合 Loading 和 Error 状态处理：
```vue
<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const loading = ref(true)
const error = ref('')
const chartData = ref([])

onMounted(async () => {
  try {
    const res = await axios.get('/api/chart-data')
    chartData.value = res.data
  } catch (e) {
    error.value = '数据加载失败'
  } finally {
    loading.value = false
  }
})
</script>
```

**方式三：Dataset 共享数据** — 多系列图表推荐使用 dataset + dimensions 格式，数据结构更清晰：
```javascript
{
  dataset: {
    source: [
      ['季度', '产品A', '产品B'],
      ['Q1', 320, 280],
      ['Q2', 450, 380],
      ['Q3', 510, 420],
      ['Q4', 600, 490],
    ],
    dimensions: ['quarter', 'productA', 'productB'],
  },
  xAxis: { type: 'category' },
  yAxis: { type: 'value' },
  series: [{ type: 'bar', name: '产品A' }, { type: 'bar', name: '产品B' }],
}
```

---

## 按需引入映射表

### 图表类型

| 图表类型 | 按需引入模块 | 速查变体 | 参考文档 |
|----------|-------------|---------|----------|
| 折线图/面积图 | `echarts/charts` → `LineChart` | 基础、多系列、面积图、标记线、数据缩放 | [LineChart.md](references/LineChart.md) |
| 柱状图 | `echarts/charts` → `BarChart` | 基础、多系列、堆叠、横向、数据缩放 | [BarChart.md](references/BarChart.md) |
| 饼图/环形图 | `echarts/charts` → `PieChart` | 基础、环形图、南丁格尔玫瑰图、嵌套环形图、百分比标签 | [PieChart.md](references/PieChart.md) |
| 散点图/气泡图 | `echarts/charts` → `ScatterChart` | 基础、多系列、气泡图、分类颜色、带趋势线 | [ScatterChart.md](references/ScatterChart.md) |
| 雷达图 | `echarts/charts` → `RadarChart` | 基础、多系列、面积填充、多雷达图并列对比 | [RadarChart.md](references/RadarChart.md) |
| 仪表盘 | `echarts/charts` → `GaugeChart` | 基础、多表盘、颜色分段、环形进度条、传统指针 | [GaugeChart.md](references/GaugeChart.md) |
| 热力图 | `echarts/charts` → `HeatmapChart` | 基础、分类热力图、日历热力图、相关性矩阵 | [HeatmapChart.md](references/HeatmapChart.md) |
| 漏斗图 | `echarts/charts` → `FunnelChart` | 基础、多系列、转化率漏斗、金字塔形 | [FunnelChart.md](references/FunnelChart.md) |
| 树形图 | `echarts/charts` → `TreemapChart` | 基础、多层级、可下钻、颜色深浅映射 | [TreemapChart.md](references/TreemapChart.md) |
| 桑基图 | `echarts/charts` → `SankeyChart` | 基础、垂直布局、多层级流向、自定义节点颜色 | [SankeyChart.md](references/SankeyChart.md) |
| K线图 | `echarts/charts` → `CandlestickChart` | 基础、多周期、技术指标叠加 | [CandlestickChart.md](references/CandlestickChart.md) |

### 组件功能

| 组件功能 | ECharts 模块 |
|----------|-------------|
| 标题 | `echarts/components` → `TitleComponent` |
| 提示框 | `echarts/components` → `TooltipComponent` |
| 图例 | `echarts/components` → `LegendComponent` |
| 网格 | `echarts/components` → `GridComponent` |
| 数据缩放 | `echarts/components` → `DataZoomComponent` |
| 工具栏 | `echarts/components` → `ToolboxComponent` |
| 数据集 | `echarts/components` → `DatasetComponent` |
| 数据转换 | `echarts/components` → `TransformComponent` |
| 标记线 | `echarts/components` → `MarkLineComponent` |
| Canvas 渲染 | `echarts/renderers` → `CanvasRenderer` |
| SVG 渲染 | `echarts/renderers` → `SVGRenderer` |

---

## 常见坑与最佳实践

| 坑 | 解决方案 |
|---|---|
| ECharts 全量引入体积过大 | 使用按需引入，减少约 60% 体积 |
| 大数据量卡顿 | 启用 `sampling`、关闭 `animation`、不显示 `showSymbol` |
| 容器尺寸为 0 导致图表不显示 | 确保容器有明确的 height（不能只靠父容器） |
| 响应式不生效 | 使用 `autoresize` 属性或手动监听 `resize` 事件 |
| tooltip 不显示 | 检查是否注册了 `TooltipComponent` |
| 暗黑模式样式不统一 | 使用 ECharts 内置 `dark` 主题：`theme: 'dark'` |
| 散点图数据点密集重叠 | 启用 `sampling`，减小 `symbolSize`，或使用热力图替代 |
| 气泡图尺寸差异过大 | `symbolSize` 使用对数或平方根缩放：`Math.sqrt(data[2])` |

---

## 高级功能

### 优化适配

当图表数据量大或交互复杂时，需进行性能优化：
- **大数据量渲染**（10 万+）：启用 `sampling: 'lttb'`，关闭 `animation`，隐藏 `showSymbol`；柱状图使用 `large: true` + `largeThreshold`
- **懒更新**：数据频繁变化时，用 `chart.setOption()` 配合 `replaceMerge: ['series']` 避免全量重绘
- **响应式适配**：确保容器有明确的 `height`，使用 `autoresize` 属性或手动监听 `resize` 事件

完整代码示例见各 references 文件中的「优化适配」章节。

### 主题适配

保持图表风格与项目视觉统一：
- **内置主题**：`<v-chart theme="dark" />` 或 `theme="light"`
- **自定义主题**：通过 `echarts.registerTheme()` 注册项目主题，统一颜色、字体、坐标轴样式
- **暗色模式切换**：用 `computed` 动态绑定 `:theme` 属性，随系统或用户偏好切换

完整代码示例见各 references 文件中的「主题适配」章节。

### 交互增强

提升图表可用性和信息密度：
- **Tooltip 自定义**：通过 `formatter` 函数定制提示内容，格式化数值单位、添加图标
- **Toolbox 工具箱**：内置 `saveAsImage`（导出图片）、`dataZoom`（缩放）、`restore`（还原）、`magicType`（图表类型切换）
- **DataZoom 数据缩放**：同时配置 `type: 'slider'`（滑块）和 `type: 'inside'`（鼠标滚轮）
- **图表联动**：设置 `groupId` 实现多图表同步高亮、同步缩放

完整代码示例见各 references 文件中的「交互增强」章节。

---

## 输出规范

每次图表开发完成后：
1. 提供完整的 Vue 组件代码
2. 确认依赖已正确安装
3. 说明如何使用该组件（props、事件、暴露的 API）
4. 验证图表 option 配置正确（数据结构完整、类型匹配、颜色协调）
