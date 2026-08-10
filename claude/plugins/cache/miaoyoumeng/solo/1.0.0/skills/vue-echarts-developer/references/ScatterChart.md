# ScatterChart — 散点图/气泡图完整参考

本文档包含 ScatterChart 在 Vue 3 环境中的完整代码示例。各步骤详细说明请参见 `../SKILL.md`。

---

## 第 1 步：组件开发

### TypeScript 类型定义

```typescript
import type { EChartsOption } from 'echarts'

interface ScatterDataItem {
  x: number
  y: number
  value?: number
  name?: string
  [key: string]: any
}

interface ChartProps {
  data: ScatterDataItem[]
  title: string
  loading?: boolean
}
```

### 基础组件模板（TypeScript + Composition API）

```vue
<script setup>
import { ref, computed, watch } from 'vue'
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { ScatterChart } from 'echarts/charts'
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
} from 'echarts/components'

// 按需注册
use([
  CanvasRenderer,
  ScatterChart,
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
])

const props = defineProps({
  data: { type: Array, default: () => [] },
  title: { type: String, default: '' },
})

const option = computed(() => ({
  title: { text: props.title, left: 'center' },
  tooltip: { trigger: 'item' },
  legend: { bottom: 0 },
  grid: { left: '3%', right: '4%', bottom: '10%', containLabel: true },
  xAxis: { type: 'value', name: 'X 轴' },
  yAxis: { type: 'value', name: 'Y 轴' },
  series: [
    {
      name: '数据点',
      type: 'scatter',
      data: props.data.map((d) => [d.x, d.y]),
      symbolSize: 10,
      itemStyle: { color: '#5470c6' },
    },
  ],
}))
</script>

<template>
  <v-chart class="chart" :option="option" autoresize />
</template>

<style scoped>
.chart {
  width: 100%;
  height: 400px;
}
</style>
```

---

## 第 2 步：数据接入

### API 数据接入（含 Loading 和 Error 状态）

```vue
<script setup>
import { ref, computed, onMounted } from 'vue'
import VChart from 'vue-echarts'
import axios from 'axios'
import type { EChartsOption } from 'echarts'

const loading = ref(true)
const error = ref('')
const chartData = ref<any[]>([])

const option = computed<EChartsOption>(() => ({
  tooltip: { trigger: 'item' },
  xAxis: { type: 'value' },
  yAxis: { type: 'value' },
  series: [{
    name: '指标',
    type: 'scatter',
    data: chartData.value.map((d) => [d.x, d.y]),
    symbolSize: 8,
  }],
}))

onMounted(async () => {
  try {
    const res = await axios.get('/api/scatter-data')
    chartData.value = res.data
  } catch (e: any) {
    error.value = e.message || '数据加载失败'
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div v-if="error" class="chart-error">{{ error }}</div>
  <v-chart v-else class="chart" :option="option" :loading="loading" autoresize />
</template>

<style scoped>
.chart { width: 100%; height: 400px; }
.chart-error { color: #ee6666; padding: 20px; text-align: center; }
</style>
```

### Dataset 共享数据（多系列推荐）

```javascript
const option = {
  dataset: {
    source: [
      ['产品', '价格', '销量', '评分'],
      ['产品A', 120, 850, 4.5],
      ['产品B', 200, 620, 3.8],
      ['产品C', 150, 730, 4.2],
      ['产品D', 80, 910, 4.7],
    ],
    dimensions: ['product', 'price', 'sales', 'rating'],
  },
  xAxis: { type: 'value', name: '价格' },
  yAxis: { type: 'value', name: '销量' },
  series: [
    {
      type: 'scatter',
      name: '产品分布',
      encode: { x: 'price', y: 'sales' },
      symbolSize: 12,
    },
  ],
}
```

---

## 第 3 步：优化适配

### 响应式适配

```vue
<v-chart class="chart" :option="option" autoresize />
```

容器尺寸必须明确指定：

```vue
<style scoped>
.chart {
  width: 100%;
  height: 400px;
}

@media (max-width: 768px) {
  .chart {
    height: 250px;
  }
}
</style>
```

### 大数据量渲染（10万+数据点）

```javascript
const option = {
  xAxis: { type: 'value' },
  yAxis: { type: 'value' },
  series: [{
    type: 'scatter',
    data: largeScatterArray,
    sampling: 'lttb',
    animation: false,
    symbolSize: 4,
  }],
}
```

### 懒更新（避免全量重绘）

```javascript
chart.setOption({ series: [{ data: newData }] }, { replaceMerge: ['series'] })
```

---

## 第 4 步：主题适配

### 内置主题

```vue
<v-chart class="chart" :option="option" theme="dark" autoresize />
```

### 自定义主题

```javascript
import * as echarts from 'echarts'

echarts.registerTheme('project-theme', {
  color: ['#5470c6', '#91cc75', '#fac858', '#ee6666', '#73c0de'],
  backgroundColor: 'transparent',
  textStyle: { fontFamily: 'inherit', fontSize: 12 },
  categoryAxis: { axisLine: { lineStyle: { color: '#ccc' } } },
  valueAxis: { axisLine: { lineStyle: { color: '#ccc' } } },
})
```

### 暗色模式适配

```vue
<script setup>
import { computed } from 'vue'

const props = defineProps({
  isDark: { type: Boolean, default: false },
})

const theme = computed(() => props.isDark ? 'dark' : 'light')
</script>

<template>
  <v-chart class="chart" :option="option" :theme="theme" autoresize />
</template>
```

---

## 第 5 步：交互增强

### Tooltip 自定义

```javascript
tooltip: {
  trigger: 'item',
  formatter: (params) => {
    return `${params.name || '数据点'}<br/>X: ${params.value[0]}<br/>Y: ${params.value[1]}`
  },
}
```

### Toolbox 工具箱

```javascript
toolbox: {
  feature: {
    saveAsImage: { title: '保存图片' },
    dataZoom: { title: { zoom: '缩放', back: '还原' } },
    restore: { title: '还原' },
    magicType: {
      type: ['scatter'],
      title: { scatter: '散点' },
    },
  },
}
```

### DataZoom 数据缩放

```javascript
dataZoom: [
  { type: 'slider', start: 0, end: 100, xAxisIndex: 0 },
  { type: 'slider', start: 0, end: 100, yAxisIndex: 0 },
  { type: 'inside', start: 0, end: 100, xAxisIndex: 0 },
  { type: 'inside', start: 0, end: 100, yAxisIndex: 0 },
]
```

### 图表联动（多图表同步）

```javascript
const option1 = { groupId: 'scatter-group' }
const option2 = { groupId: 'scatter-group' }

chart1.on('highlight', (params) => {
  chart2.dispatchAction({
    type: 'highlight',
    seriesIndex: params.seriesIndex,
    dataIndex: params.dataIndex,
  })
})
```

---

## 常用散点图配置速查

### 基础散点图

```javascript
{
  tooltip: { trigger: 'item' },
  xAxis: { type: 'value', name: 'X' },
  yAxis: { type: 'value', name: 'Y' },
  series: [{
    type: 'scatter',
    data: [[10, 20], [15, 25], [30, 40], [50, 60]],
    symbolSize: 10,
  }],
}
```

### 多系列散点图

```javascript
{
  tooltip: { trigger: 'item' },
  legend: { bottom: 0 },
  xAxis: { type: 'value', name: '年龄' },
  yAxis: { type: 'value', name: '收入' },
  series: [
    { name: '男性', type: 'scatter', data: [[25, 5000], [30, 7000], [35, 9000]], itemStyle: { color: '#5470c6' } },
    { name: '女性', type: 'scatter', data: [[25, 4500], [30, 6500], [35, 8500]], itemStyle: { color: '#91cc75' } },
  ],
}
```

### 气泡图（三维数据）

```javascript
{
  tooltip: { trigger: 'item' },
  xAxis: { type: 'value', name: '人均GDP' },
  yAxis: { type: 'value', name: '平均寿命' },
  series: [{
    type: 'scatter',
    data: [
      { value: [30000, 80, 500], name: '日本' },
      { value: [60000, 78, 330], name: '美国' },
      { value: [10000, 72, 1400], name: '中国' },
    ],
    symbolSize: (data) => Math.sqrt(data[2]) * 2,
  }],
}
```

### 带分类颜色散点图

```javascript
{
  tooltip: { trigger: 'item' },
  legend: { bottom: 0 },
  xAxis: { type: 'value' },
  yAxis: { type: 'value' },
  visualMap: {
    min: 0,
    max: 3,
    dimension: 2,
    categories: ['A类', 'B类', 'C类', 'D类'],
    inRange: { color: ['#5470c6', '#91cc75', '#fac858', '#ee6666'] },
  },
  series: [{
    type: 'scatter',
    data: [
      [10, 20, 0], [30, 40, 1], [50, 60, 2], [70, 80, 3],
    ],
    symbolSize: 12,
  }],
}
```

### 带趋势线的散点图（回归分析）

```javascript
{
  tooltip: { trigger: 'item' },
  xAxis: { type: 'value' },
  yAxis: { type: 'value' },
  series: [
    {
      name: '数据点',
      type: 'scatter',
      data: [[1, 2], [2, 3], [3, 5], [4, 4], [5, 6]],
      symbolSize: 10,
    },
    {
      name: '趋势线',
      type: 'line',
      data: [[1, 1.5], [5, 6.5]],
      smooth: false,
      lineStyle: { type: 'dashed', color: '#ee6666' },
      symbol: 'none',
    },
  ],
}
```
