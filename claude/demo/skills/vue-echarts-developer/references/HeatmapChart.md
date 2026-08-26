# HeatmapChart — 热力图完整参考

本文档包含 HeatmapChart 在 Vue 3 环境中的完整代码示例。各步骤详细说明请参见 `../SKILL.md`。

---

## 第 1 步：组件开发

### TypeScript 类型定义

```typescript
import type { EChartsOption } from 'echarts'

interface HeatmapDataItem {
  x: number | string
  y: number | string
  value: number
}

interface HeatmapProps {
  data: HeatmapDataItem[]
  xLabels: string[]
  yLabels: string[]
  title?: string
  loading?: boolean
}
```

### 基础组件模板（TypeScript + Composition API）

```vue
<script setup lang="ts">
import { computed } from 'vue'
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { HeatmapChart } from 'echarts/charts'
import {
  TitleComponent,
  TooltipComponent,
  GridComponent,
  VisualMapComponent,
} from 'echarts/components'
import type { EChartsOption } from 'echarts'

use([
  CanvasRenderer,
  HeatmapChart,
  TitleComponent,
  TooltipComponent,
  GridComponent,
  VisualMapComponent,
])

const props = defineProps<{
  data: HeatmapDataItem[]
  xLabels: string[]
  yLabels: string[]
  title?: string
}>()

const option = computed<EChartsOption>(() => {
  const heatmapData = props.data.map((d) => [
    props.xLabels.indexOf(d.x as string),
    props.yLabels.indexOf(d.y as string),
    d.value,
  ])

  return {
    title: { text: props.title, left: 'center' },
    tooltip: {
      position: 'top',
      formatter: (p: any) =>
        `${props.xLabels[p.data[0]]}<br/>${props.yLabels[p.data[1]]}<br/>值: ${p.data[2]}`,
    },
    grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
    xAxis: {
      type: 'category',
      data: props.xLabels,
      splitArea: { show: true },
    },
    yAxis: {
      type: 'category',
      data: props.yLabels,
      splitArea: { show: true },
    },
    visualMap: {
      min: 0,
      max: Math.max(...props.data.map((d) => d.value)),
      calculable: true,
      orient: 'vertical',
      left: 'right',
      top: 'center',
    },
    series: [
      {
        type: 'heatmap',
        data: heatmapData,
        label: { show: true },
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowColor: 'rgba(0, 0, 0, 0.5)',
          },
        },
      },
    ],
  }
})
</script>

<template>
  <v-chart class="chart" :option="option" autoresize />
</template>

<style scoped>
.chart {
  width: 100%;
  height: 500px;
}
</style>
```

---

## 第 2 步：数据接入

### API 数据接入（含 Loading 和 Error 状态）

```vue
<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import VChart from 'vue-echarts'
import axios from 'axios'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { HeatmapChart } from 'echarts/charts'
import {
  TooltipComponent,
  GridComponent,
  VisualMapComponent,
} from 'echarts/components'
import type { EChartsOption } from 'echarts'

use([CanvasRenderer, HeatmapChart, TooltipComponent, GridComponent, VisualMapComponent])

const loading = ref(true)
const error = ref('')
const xLabels = ref<string[]>([])
const yLabels = ref<string[]>([])
const heatmapData = ref<number[][]>([])

const option = computed<EChartsOption>(() => ({
  tooltip: { position: 'top' },
  grid: { left: '3%', right: '4%', bottom: '10%', containLabel: true },
  xAxis: { type: 'category', data: xLabels.value, splitArea: { show: true } },
  yAxis: { type: 'category', data: yLabels.value, splitArea: { show: true } },
  visualMap: {
    min: 0,
    max: Math.max(...heatmapData.value.map((d) => d[2]), 1),
    calculable: true,
    orient: 'horizontal',
    left: 'center',
    bottom: '0%',
  },
  series: [{
    type: 'heatmap',
    data: heatmapData.value,
    label: { show: true },
  }],
}))

onMounted(async () => {
  try {
    const res = await axios.get('/api/heatmap-data')
    xLabels.value = res.data.xLabels
    yLabels.value = res.data.yLabels
    heatmapData.value = res.data.data
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
.chart { width: 100%; height: 500px; }
.chart-error { color: #ee6666; padding: 20px; text-align: center; }
</style>
```

### 矩阵数据转换（相关性矩阵场景）

```javascript
// 将二维矩阵转为热力图所需的 [x, y, value] 格式
function matrixToHeatmapData(matrix, rowLabels, colLabels) {
  const data = []
  for (let i = 0; i < matrix.length; i++) {
    for (let j = 0; j < matrix[i].length; j++) {
      data.push([j, i, matrix[i][j]])
    }
  }
  return { data, xLabels: colLabels, yLabels: rowLabels }
}

// 示例：相关性矩阵
const correlationMatrix = [
  [1.0, 0.8, 0.3, -0.2],
  [0.8, 1.0, 0.5,  0.1],
  [0.3, 0.5, 1.0,  0.7],
  [-0.2, 0.1, 0.7, 1.0],
]
const labels = ['指标A', '指标B', '指标C', '指标D']
const { data, xLabels, yLabels } = matrixToHeatmapData(correlationMatrix, labels, labels)
```

---

## 第 3 步：优化适配

### 响应式适配

```vue
<v-chart class="chart" :option="option" autoresize />
```

容器尺寸：

```vue
<style scoped>
.chart {
  width: 100%;
  height: 500px;
}

@media (max-width: 768px) {
  .chart {
    height: 350px;
  }
}
</style>
```

### 大数据量渲染

```javascript
const option = {
  xAxis: { type: 'category', data: largeXLabels, axisLabel: { show: false } },
  yAxis: { type: 'category', data: largeYLabels, axisLabel: { show: false } },
  visualMap: { show: false },
  series: [{
    type: 'heatmap',
    data: largeHeatmapData,
    label: { show: false },
  }],
}
```

大数据量热力图需关闭 label 显示和 visualMap 计算以提升渲染性能。

### 渐进渲染

```javascript
const chartInstance = chartRef.value?.getInstance?.()
chartInstance?.setOption(option, { progressive: 500 })
```

---

## 第 4 步：主题适配

### 内置主题

```vue
<v-chart class="chart" :option="option" theme="dark" autoresize />
```

### 自定义颜色映射

```javascript
visualMap: {
  min: 0,
  max: 100,
  calculable: true,
  inRange: {
    color: ['#313695', '#4575b4', '#74add1', '#abd9e9', '#fee090', '#f46d43', '#d73027'],
  },
  text: ['高', '低'],
}
```

### 暗色模式适配

```vue
<script setup>
import { computed } from 'vue'

const props = defineProps({
  isDark: { type: Boolean, default: false },
})

const visualMapConfig = computed(() => ({
  inRange: {
    color: props.isDark
      ? ['#0d1b2a', '#1b2838', '#3a506b', '#5b8a72', '#7bc67e']
      : ['#f7fbff', '#c6dbef', '#6baed6', '#2171b5', '#08306b'],
  },
}))
</script>
```

---

## 第 5 步：交互增强

### Tooltip 自定义

```javascript
tooltip: {
  position: 'top',
  formatter: (params) => {
    const { x, y, value } = { x: params.data[0], y: params.data[1], value: params.data[2] }
    return `
      <div style="font-weight:bold">${xLabels[x]}</div>
      <div>${yLabels[y]}</div>
      <div style="color:#fac858;font-size:16px">${value}</div>
    `
  },
}
```

### 点击事件交互

```vue
<script setup>
import { ref } from 'vue'

const chartRef = ref()

const onChartClick = (params) => {
  const xLabel = xLabels.value[params.data[0]]
  const yLabel = yLabels.value[params.data[1]]
  const value = params.data[2]
  console.log(`点击了 ${xLabel} × ${yLabel}: ${value}`)
}
</script>

<template>
  <v-chart ref="chartRef" class="chart" :option="option" @click="onChartClick" autoresize />
</template>
```

### visualMap 联动

```javascript
// 多热力图共享 visualMap 范围
const sharedVisualMap = {
  min: 0,
  max: 100,
  calculable: true,
  seriesIndex: [0, 1],
  orient: 'horizontal',
  left: 'center',
  bottom: '0%',
}
```

---

## 常用热力图配置速查

### 基础热力图

```javascript
{
  tooltip: { position: 'top' },
  grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
  xAxis: { type: 'category', data: ['A', 'B', 'C', 'D'], splitArea: { show: true } },
  yAxis: { type: 'category', data: ['周一', '周二', '周三'], splitArea: { show: true } },
  visualMap: { min: 0, max: 10, calculable: true, orient: 'vertical', left: 'right' },
  series: [{
    type: 'heatmap',
    data: [[0, 0, 5], [1, 0, 8], [2, 0, 3], [3, 0, 7],
           [0, 1, 2], [1, 1, 6], [2, 1, 9], [3, 1, 4],
           [0, 2, 7], [1, 2, 3], [2, 2, 5], [3, 2, 8]],
    label: { show: true },
  }],
}
```

### 分类热力图（带文字标签）

```javascript
{
  tooltip: { position: 'top' },
  grid: { left: '10%', right: '10%', bottom: '10%' },
  xAxis: {
    type: 'category',
    data: ['产品A', '产品B', '产品C', '产品D', '产品E'],
    axisLabel: { rotate: 30 },
  },
  yAxis: { type: 'category', data: ['北京', '上海', '广州', '深圳'] },
  visualMap: {
    min: 0,
    max: 100,
    inRange: { color: ['#f7fbff', '#2171b5', '#08306b'] },
    left: 'right',
  },
  series: [{
    type: 'heatmap',
    data: categoryHeatmapData,
    label: { show: true, fontSize: 12 },
    emphasis: { itemStyle: { shadowBlur: 10, shadowColor: 'rgba(0,0,0,0.5)' } },
  }],
}
```

### 日历热力图

```javascript
{
  tooltip: { position: 'top' },
  visualMap: {
    min: 0,
    max: 1000,
    orient: 'horizontal',
    left: 'center',
    bottom: '0%',
    inRange: { color: ['#ebedf0', '#c6e48b', '#7bc96f', '#239a3b', '#196127'] },
  },
  calendar: {
    range: '2024',
    left: '5%',
    right: '5%',
    cellSize: ['auto', 20],
    yearLabel: { show: true },
    itemStyle: { borderWidth: 4, borderColor: '#fff' },
  },
  series: [{
    type: 'heatmap',
    coordinateSystem: 'calendar',
    data: calendarHeatmapData,
  }],
}
```

### 相关性矩阵热力图

```javascript
{
  tooltip: {
    position: 'top',
    formatter: (p) => `${metrics[p.data[0]]} vs ${metrics[p.data[1]]}<br/>r = ${p.data[2].toFixed(2)}`,
  },
  grid: { left: '15%', right: '5%', top: '5%', bottom: '5%' },
  xAxis: { type: 'category', data: metrics, axisLabel: { rotate: 45 } },
  yAxis: { type: 'category', data: metrics },
  visualMap: {
    min: -1,
    max: 1,
    calculable: true,
    inRange: { color: ['#d73027', '#fc8d59', '#fee08b', '#d9ef8b', '#91bfdb', '#4575b4'] },
    left: 'right',
  },
  series: [{
    type: 'heatmap',
    data: correlationData,
    label: {
      show: true,
      formatter: (p) => p.data[2].toFixed(2),
      fontSize: 10,
    },
  }],
}
```
