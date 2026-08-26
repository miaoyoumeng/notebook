# ECharts 图表开发指南

## 图表类型决策树

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

## 环境确认

检查 `package.json` 中是否存在：

```json
"echarts": "^5.x.x",
"vue-echarts": "^7.x.x"
```

如果不存在，执行：

```bash
pnpm add echarts vue-echarts
```

## 组件基础结构

```vue
<script setup lang="ts">
import { use } from 'echarts/core';
import { CanvasRenderer } from 'echarts/renderers';
import { LineChart } from 'echarts/charts';
import {
  TooltipComponent,
  GridComponent,
} from 'echarts/components';
import VChart, { type EChartsOption } from 'vue-echarts';
import type { ComputedRef } from 'vue';

use([CanvasRenderer, LineChart, TooltipComponent, GridComponent]);

const props = defineProps<{ data: any[]; title: string }>();

const option = computed<ComputedRef<EChartsOption>>(() => ({
  title: { text: props.title },
  tooltip: { trigger: 'axis' },
  grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
  xAxis: { type: 'category', data: props.data.map(d => d.name) },
  yAxis: { type: 'value' },
  series: [{ type: 'line', data: props.data.map(d => d.value) }],
}));
</script>

<template>
  <v-chart class="chart" :option="option" autoresize />
</template>
```

## 按需引入映射表

### 图表类型

| 图表类型 | 引入模块 |
|----------|---------|
| 折线图/面积图 | `echarts/charts` → `LineChart` |
| 柱状图 | `echarts/charts` → `BarChart` |
| 饼图/环形图 | `echarts/charts` → `PieChart` |
| 散点图/气泡图 | `echarts/charts` → `ScatterChart` |
| 雷达图 | `echarts/charts` → `RadarChart` |
| 仪表盘 | `echarts/charts` → `GaugeChart` |
| 热力图 | `echarts/charts` → `HeatmapChart` |
| 漏斗图 | `echarts/charts` → `FunnelChart` |
| 树形图 | `echarts/charts` → `TreemapChart` |
| 桑基图 | `echarts/charts` → `SankeyChart` |
| K线图 | `echarts/charts` → `CandlestickChart` |

### 组件功能

| 功能 | 引入模块 |
|------|---------|
| 标题 | `TitleComponent` |
| 提示框 | `TooltipComponent` |
| 图例 | `LegendComponent` |
| 网格 | `GridComponent` |
| 数据缩放 | `DataZoomComponent` |
| 工具栏 | `ToolboxComponent` |
| 数据集 | `DatasetComponent` |
| Canvas 渲染 | `CanvasRenderer` |
| SVG 渲染 | `SVGRenderer` |

## 常见坑与解决

| 坑 | 解决 |
|---|------|
| ECharts 全量引入体积过大 | 按需引入，减少约 60% 体积 |
| 大数据量卡顿 | 启用 `sampling`、关闭 `animation`、隐藏 `showSymbol` |
| 容器尺寸为 0 | 确保容器有明确的 height |
| 响应式不生效 | 使用 `autoresize` 属性 |
| tooltip 不显示 | 检查是否注册了 `TooltipComponent` |
| 暗黑模式 | 使用 `theme: 'dark'` |

## 优化适配

- **大数据量**（10 万+）：`sampling: 'lttb'`，关闭 `animation`，隐藏 `showSymbol`
- **柱状图大量数据**：`large: true` + `largeThreshold`
- **懒更新**：`chart.setOption()` 配合 `replaceMerge: ['series']`

## 交互增强

- **Tooltip 自定义**：`formatter` 函数定制提示
- **DataZoom**：同时配置 `type: 'slider'` 和 `type: 'inside'`
- **图表联动**：设置 `groupId` 实现多图表同步

## 暴露方法

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
