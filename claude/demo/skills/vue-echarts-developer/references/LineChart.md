# LineChart — 折线图完整参考

本文档包含 LineChart 在 Vue 3 环境中的完整代码示例。各步骤详细说明请参见 `../SKILL.md`。

---

## 第 1 步：组件开发

### TypeScript 类型定义

```typescript
import type { EChartsOption } from 'echarts'

interface ChartDataItem {
  name: string
  value: number
  [key: string]: any
}

interface ChartProps {
  data: ChartDataItem[]
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
import { LineChart } from 'echarts/charts'
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
} from 'echarts/components'

// 按需注册
use([
  CanvasRenderer,
  LineChart,
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
  tooltip: { trigger: 'axis' },
  legend: { bottom: 0 },
  grid: { left: '3%', right: '4%', bottom: '10%', containLabel: true },
  xAxis: {
    type: 'category',
    data: props.data.map((d) => d.name),
  },
  yAxis: { type: 'value' },
  series: [
    {
      name: '数值',
      type: 'line',
      data: props.data.map((d) => d.value),
      smooth: true,
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
  tooltip: { trigger: 'axis' },
  xAxis: { type: 'category', data: chartData.value.map((d) => d.date) },
  yAxis: { type: 'value' },
  series: [{
    name: '指标',
    type: 'line',
    data: chartData.value.map((d) => d.value),
    smooth: true,
  }],
}))

onMounted(async () => {
  try {
    const res = await axios.get('/api/chart-data')
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
      ['月份', '收入', '成本', '利润'],
      ['1月', 120, 80, 40],
      ['2月', 200, 120, 80],
      ['3月', 150, 90, 60],
    ],
    dimensions: ['month', 'revenue', 'cost', 'profit'],
  },
  xAxis: { type: 'category' },
  yAxis: { type: 'value' },
  series: [
    { type: 'line', name: '收入', smooth: true, lineStyle: { width: 3 } },
    { type: 'line', name: '成本', smooth: true, lineStyle: { width: 2, type: 'dashed' } },
    { type: 'line', name: '利润', smooth: true, areaStyle: { opacity: 0.1 } },
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
  xAxis: { type: 'category', data: largeDataArray },
  yAxis: { type: 'value' },
  series: [{
    type: 'line',
    data: largeDataArray,
    sampling: 'lttb',
    animation: false,
    showSymbol: false,
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
  title: { textStyle: { fontSize: 16, fontWeight: 'bold' } },
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
  trigger: 'axis',
  formatter: (params) => {
    const rows = params.map((p) => {
      return `${p.seriesName}: ${p.value.toLocaleString()}`
    })
    return `${params[0].name}<br/>${rows.join('<br/>')}`
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
      type: ['line'],
      title: { line: '折线' },
    },
  },
}
```

### DataZoom 数据缩放

```javascript
dataZoom: [
  { type: 'slider', start: 0, end: 50 },
  { type: 'inside', start: 0, end: 50 },
]
```

### 图表联动（多图表同步）

```javascript
const option1 = { groupId: 'report' }
const option2 = { groupId: 'report' }

chart1.on('highlight', (params) => {
  chart2.dispatchAction({
    type: 'highlight',
    seriesIndex: params.seriesIndex,
    dataIndex: params.dataIndex,
  })
})
```

---

## 常用折线图配置速查

### 基础折线图

```javascript
{
  tooltip: { trigger: 'axis' },
  xAxis: { type: 'category', data: ['周一', '周二', '周三'] },
  yAxis: { type: 'value' },
  series: [{ type: 'line', data: [120, 200, 150], smooth: true }],
}
```

### 多系列折线图

```javascript
{
  tooltip: { trigger: 'axis' },
  legend: { bottom: 0 },
  xAxis: { type: 'category', data: ['1月', '2月', '3月'] },
  yAxis: { type: 'value' },
  series: [
    { name: '收入', type: 'line', data: [320, 332, 301], smooth: true },
    { name: '成本', type: 'line', data: [120, 132, 101], smooth: true, lineStyle: { type: 'dashed' } },
  ],
}
```

### 面积图

```javascript
{
  tooltip: { trigger: 'axis' },
  xAxis: { type: 'category', data: ['A', 'B', 'C'] },
  yAxis: { type: 'value' },
  series: [{
    type: 'line',
    data: [335, 310, 234],
    smooth: true,
    areaStyle: { opacity: 0.3 },
  }],
}
```

### 带标记线的折线图

```javascript
{
  tooltip: { trigger: 'axis' },
  xAxis: { type: 'category', data: ['1月', '2月', '3月', '4月'] },
  yAxis: { type: 'value' },
  series: [{
    type: 'line',
    data: [80, 70, 90, 85],
    smooth: true,
    markLine: {
      data: [{ type: 'average', name: '平均值' }],
    },
  }],
}
```

### 带数据缩放的折线图

```javascript
{
  tooltip: { trigger: 'axis' },
  xAxis: { type: 'category', data: ['1月', '2月', '3月', '4月', '5月', '6月'] },
  yAxis: { type: 'value' },
  dataZoom: [{ type: 'slider', start: 0, end: 50 }],
  series: [{ type: 'line', data: [120, 200, 150, 180, 220, 190], smooth: true }],
}
```
