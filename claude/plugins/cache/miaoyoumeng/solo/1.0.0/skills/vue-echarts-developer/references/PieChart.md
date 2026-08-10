# PieChart — 饼图/环形图完整参考

本文档包含 PieChart 在 Vue 3 环境中的完整代码示例。各步骤详细说明请参见 `../SKILL.md`。

---

## 第 1 步：组件开发

### TypeScript 类型定义

```typescript
import type { EChartsOption } from 'echarts'

interface PieDataItem {
  name: string
  value: number
  [key: string]: any
}

interface PieChartProps {
  data: PieDataItem[]
  title: string
  radius?: string[]
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
import { PieChart } from 'echarts/charts'
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
} from 'echarts/components'

// 按需注册
use([
  CanvasRenderer,
  PieChart,
  TitleComponent,
  TooltipComponent,
  LegendComponent,
])

const props = defineProps({
  data: { type: Array, default: () => [] },
  title: { type: String, default: '' },
})

const option = computed(() => ({
  title: { text: props.title, left: 'center' },
  tooltip: { trigger: 'item' },
  legend: { orient: 'vertical', left: 'left' },
  series: [
    {
      name: '占比',
      type: 'pie',
      radius: '50%',
      data: props.data,
      emphasis: {
        itemStyle: {
          shadowBlur: 10,
          shadowOffsetX: 0,
          shadowColor: 'rgba(0, 0, 0, 0.5)',
        },
      },
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
  legend: { orient: 'vertical', left: 'left' },
  series: [{
    name: '占比',
    type: 'pie',
    radius: '50%',
    data: chartData.value,
  }],
}))

onMounted(async () => {
  try {
    const res = await axios.get('/api/pie-data')
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

### 静态数据格式

```javascript
const data = [
  { name: '直接访问', value: 335 },
  { name: '邮件营销', value: 310 },
  { name: '联盟广告', value: 234 },
  { name: '视频广告', value: 135 },
  { name: '搜索引擎', value: 1548 },
]
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

### 环形图（Donut）

```javascript
const option = {
  series: [{
    type: 'pie',
    radius: ['40%', '70%'],
    data: pieData,
  }],
}
```

### 南丁格尔图（Rose）

```javascript
const option = {
  series: [{
    type: 'pie',
    radius: [20, 100],
    center: ['50%', '50%'],
    roseType: 'area',
    data: roseData,
  }],
}
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

echarts.registerTheme('pie-theme', {
  color: ['#5470c6', '#91cc75', '#fac858', '#ee6666', '#73c0de'],
  backgroundColor: 'transparent',
  textStyle: { fontFamily: 'inherit', fontSize: 12 },
  title: { textStyle: { fontSize: 16, fontWeight: 'bold' } },
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
  formatter: '{a} <br/>{b} : {c} ({d}%)'
}
```

### 标签显示（Label）

```javascript
series: [{
  type: 'pie',
  radius: '50%',
  data: pieData,
  label: {
    show: true,
    formatter: '{b}: {d}%',
  },
  labelLine: { show: true },
}]
```

### 图例滚动（数据项多时）

```javascript
legend: {
  type: 'scroll',
  orient: 'vertical',
  left: 'left',
  pageButtonItemGap: 5,
  pageButtonGap: 10,
}
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

## 常用饼图/环形图配置速查

### 基础饼图

```javascript
{
  tooltip: { trigger: 'item' },
  legend: { orient: 'vertical', left: 'left' },
  series: [{
    type: 'pie',
    radius: '50%',
    data: [
      { name: '直接访问', value: 335 },
      { name: '邮件营销', value: 310 },
      { name: '搜索引擎', value: 1548 },
    ],
  }],
}
```

### 环形图（Donut）

```javascript
{
  tooltip: { trigger: 'item' },
  legend: { bottom: 0 },
  series: [{
    type: 'pie',
    radius: ['40%', '70%'],
    avoidLabelOverlap: false,
    label: { show: false, position: 'center' },
    emphasis: {
      label: { show: true, formatter: '{b}\n{d}%', fontSize: 16 },
    },
    data: [
      { name: '搜索引擎', value: 1548 },
      { name: '直接访问', value: 335 },
      { name: '邮件营销', value: 310 },
    ],
  }],
}
```

### 南丁格尔玫瑰图

```javascript
{
  tooltip: { trigger: 'item' },
  legend: { bottom: 0 },
  series: [{
    type: 'pie',
    radius: [20, 100],
    center: ['50%', '50%'],
    roseType: 'area',
    itemStyle: { borderRadius: 8 },
    data: [
      { name: '分类A', value: 40 },
      { name: '分类B', value: 38 },
      { name: '分类C', value: 32 },
      { name: '分类D', value: 30 },
      { name: '分类E', value: 28 },
    ],
  }],
}
```

### 嵌套环形图

```javascript
{
  tooltip: { trigger: 'item' },
  legend: { bottom: 0 },
  series: [
    {
      name: '内环',
      type: 'pie',
      radius: [0, '30%'],
      data: [
        { name: 'A', value: 40 },
        { name: 'B', value: 60 },
      ],
    },
    {
      name: '外环',
      type: 'pie',
      radius: ['45%', '60%'],
      data: [
        { name: 'A1', value: 20 },
        { name: 'A2', value: 20 },
        { name: 'B1', value: 30 },
        { name: 'B2', value: 30 },
      ],
    },
  ],
}
```

### 带百分比标签的环形图

```javascript
{
  tooltip: { trigger: 'item' },
  series: [{
    type: 'pie',
    radius: ['50%', '70%'],
    center: ['50%', '50%'],
    label: {
      formatter: '{b}: {d}%',
    },
    labelLine: { length: 15, length2: 30 },
    data: [
      { name: '已完成', value: 75 },
      { name: '未完成', value: 25 },
    ],
  }],
}
```
