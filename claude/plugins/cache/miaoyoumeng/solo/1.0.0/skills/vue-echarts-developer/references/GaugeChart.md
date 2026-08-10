# GaugeChart — 仪表盘完整参考

本文档包含 GaugeChart 在 Vue 3 环境中的完整代码示例。各步骤详细说明请参见 `../SKILL.md`。

---

## 第 1 步：组件开发

### TypeScript 类型定义

```typescript
import type { EChartsOption } from 'echarts'

interface GaugeDataItem {
  name: string
  value: number
  min?: number
  max?: number
  unit?: string
}

interface GaugeProps {
  data: GaugeDataItem
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
import { GaugeChart } from 'echarts/charts'
import {
  TitleComponent,
  TooltipComponent,
} from 'echarts/components'
import type { EChartsOption } from 'echarts'

use([
  CanvasRenderer,
  GaugeChart,
  TitleComponent,
  TooltipComponent,
])

const props = withDefaults(defineProps<{
  value: number
  title?: string
  min?: number
  max?: number
  unit?: string
  loading?: boolean
}>(), {
  title: '',
  min: 0,
  max: 100,
  unit: '',
  loading: false,
})

const option = computed<EChartsOption>(() => ({
  series: [
    {
      type: 'gauge',
      min: props.min,
      max: props.max,
      progress: { show: true, width: 18 },
      axisLine: { lineStyle: { width: 18 } },
      axisTick: { show: false },
      splitLine: { length: 15, lineStyle: { width: 3, color: '#auto' } },
      axisLabel: { distance: 25, color: '#999', fontSize: 12 },
      anchor: { show: true, showAbove: true, size: 25, itemStyle: { borderWidth: 10 } },
      pointer: { show: false },
      detail: {
        valueAnimation: true,
        fontSize: 30,
        offsetCenter: [0, '70%'],
        formatter: `{value}${props.unit}`,
      },
      title: { offsetCenter: [0, '100%'], fontSize: 14, color: '#666' },
      data: [{ name: props.title, value: props.value }],
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
  height: 300px;
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
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { GaugeChart } from 'echarts/charts'
import { TitleComponent, TooltipComponent } from 'echarts/components'
import type { EChartsOption } from 'echarts'
import axios from 'axios'

use([CanvasRenderer, GaugeChart, TitleComponent, TooltipComponent])

const loading = ref(true)
const error = ref('')
const gaugeValue = ref(0)
const gaugeTitle = ref('CPU 使用率')

const option = computed<EChartsOption>(() => ({
  series: [{
    type: 'gauge',
    min: 0,
    max: 100,
    progress: { show: true, width: 18 },
    axisLine: { lineStyle: { width: 18 } },
    axisTick: { show: false },
    splitLine: { length: 15, lineStyle: { width: 3, color: '#auto' } },
    axisLabel: { distance: 25, color: '#999', fontSize: 12 },
    anchor: { show: true, showAbove: true, size: 25, itemStyle: { borderWidth: 10 } },
    pointer: { show: false },
    detail: { valueAnimation: true, fontSize: 30, offsetCenter: [0, '70%'], formatter: '{value}%' },
    title: { offsetCenter: [0, '100%'], fontSize: 14, color: '#666' },
    data: [{ name: gaugeTitle.value, value: gaugeValue.value }],
  }],
}))

onMounted(async () => {
  try {
    const res = await axios.get('/api/metrics/cpu')
    gaugeValue.value = res.data.usage
  } catch (e: any) {
    error.value = e.message || '数据加载失败'
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div v-if="error" class="gauge-error">{{ error }}</div>
  <v-chart v-else class="chart" :option="option" :loading="loading" autoresize />
</template>

<style scoped>
.chart { width: 100%; height: 300px; }
.gauge-error { color: #ee6666; padding: 20px; text-align: center; }
</style>
```

### 实时数据更新（WebSocket / 轮询）

```vue
<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { GaugeChart } from 'echarts/charts'
import { TitleComponent } from 'echarts/components'
import type { EChartsOption } from 'echarts'

use([CanvasRenderer, GaugeChart, TitleComponent])

const chartRef = ref<any>(null)
const gaugeValue = ref(65)
let timer: ReturnType<typeof setInterval> | null = null

const option = computed<EChartsOption>(() => ({
  series: [{
    type: 'gauge',
    min: 0,
    max: 100,
    progress: { show: true, width: 18 },
    axisLine: { lineStyle: { width: 18 } },
    axisTick: { show: false },
    splitLine: { length: 15, lineStyle: { width: 3, color: '#auto' } },
    axisLabel: { distance: 25, color: '#999', fontSize: 12 },
    anchor: { show: true, showAbove: true, size: 25, itemStyle: { borderWidth: 10 } },
    pointer: { show: false },
    detail: { valueAnimation: true, fontSize: 30, offsetCenter: [0, '70%'], formatter: '{value}%' },
    title: { offsetCenter: [0, '100%'] },
    data: [{ value: gaugeValue.value }],
  }],
}))

onMounted(() => {
  timer = setInterval(async () => {
    const res = await fetch('/api/metrics/cpu')
    const data = await res.json()
    gaugeValue.value = data.usage
    // 使用 replaceMerge 避免全量重绘
    chartRef.value?.setOption({
      series: [{ data: [{ value: gaugeValue.value }] }],
    }, { replaceMerge: ['series'] })
  }, 2000)
})

onUnmounted(() => {
  if (timer) clearInterval(timer)
})
</script>

<template>
  <v-chart ref="chartRef" class="chart" :option="option" autoresize />
</template>

<style scoped>
.chart { width: 100%; height: 300px; }
</style>
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
  height: 300px;
}

@media (max-width: 768px) {
  .chart {
    height: 200px;
  }
}
</style>
```

### 大数据量/多仪表盘布局

```javascript
const option = {
  series: [
    {
      name: 'CPU',
      type: 'gauge',
      center: ['25%', '55%'],
      radius: '70%',
      min: 0, max: 100,
      progress: { show: true, width: 12 },
      detail: { fontSize: 16, offsetCenter: [0, '80%'], formatter: '{value}%' },
      title: { offsetCenter: [0, '110%'], fontSize: 12 },
      data: [{ value: 72, name: 'CPU' }],
    },
    {
      name: '内存',
      type: 'gauge',
      center: ['75%', '55%'],
      radius: '70%',
      min: 0, max: 100,
      progress: { show: true, width: 12 },
      detail: { fontSize: 16, offsetCenter: [0, '80%'], formatter: '{value}%' },
      title: { offsetCenter: [0, '110%'], fontSize: 12 },
      data: [{ value: 58, name: '内存' }],
    },
  ],
}
```

### 懒更新（避免全量重绘）

```javascript
chart.setOption({
  series: [{ data: [{ value: newValue }] }],
}, { replaceMerge: ['series'] })
```

---

## 第 4 步：主题适配

### 内置主题

```vue
<v-chart class="chart" :option="option" theme="dark" autoresize />
```

### 自定义主题（仪表盘配色）

```javascript
import * as echarts from 'echarts'

echarts.registerTheme('gauge-theme', {
  color: ['#5470c6', '#91cc75', '#fac858', '#ee6666'],
  textStyle: { fontFamily: 'inherit', fontSize: 12 },
  series: {
    gauge: {
      progress: { itemStyle: { color: '#5470c6' } },
      detail: { color: '#333' },
      title: { color: '#666' },
    },
  },
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
  formatter: (params) => {
    const { name, value } = params.data
    return `${name}: <b>${value}%</b>`
  },
}
```

### 进度条样式（progress）

```javascript
progress: {
  show: true,
  width: 18,
  itemStyle: {
    color: '#5470c6',
    shadowColor: 'rgba(84, 112, 198, 0.5)',
    shadowBlur: 10,
  },
}
```

### 分段颜色（axisLine 按值域变色）

```javascript
axisLine: {
  lineStyle: {
    width: 18,
    color: [
      [0.3, '#91cc75'],   // 0% - 30%  绿色
      [0.7, '#fac858'],   // 30% - 70% 黄色
      [1, '#ee6666'],     // 70% - 100% 红色
    ],
  },
}
```

### 指针 + 锚点（传统仪表盘风格）

```javascript
anchor: {
  show: true,
  showAbove: true,
  size: 20,
  itemStyle: { borderWidth: 8, borderColor: '#5470c6' },
},
pointer: {
  show: true,
  length: '60%',
  width: 6,
  itemStyle: { color: '#5470c6' },
},
```

### 数值格式化（detail）

```javascript
detail: {
  valueAnimation: true,
  formatter: (value) => {
    if (value >= 90) return `${value}% 过高!`
    return `${value}%`
  },
  fontSize: 28,
  fontWeight: 'bold',
  offsetCenter: [0, '70%'],
  color: 'auto',
}
```

---

## 常用仪表盘配置速查

### 基础仪表盘（单指标）

```javascript
{
  series: [{
    type: 'gauge',
    min: 0, max: 100,
    progress: { show: true, width: 18 },
    axisLine: { lineStyle: { width: 18 } },
    axisTick: { show: false },
    splitLine: { length: 15, lineStyle: { width: 3, color: '#auto' } },
    axisLabel: { distance: 25, color: '#999', fontSize: 12 },
    anchor: { show: true, showAbove: true, size: 25, itemStyle: { borderWidth: 10 } },
    pointer: { show: false },
    detail: { valueAnimation: true, fontSize: 30, offsetCenter: [0, '70%'], formatter: '{value}%' },
    title: { offsetCenter: [0, '100%'], fontSize: 14, color: '#666' },
    data: [{ name: '完成率', value: 75 }],
  }],
}
```

### 多仪表盘并列

```javascript
{
  series: [
    {
      type: 'gauge', center: ['20%', '50%'], radius: '70%',
      min: 0, max: 100,
      progress: { show: true, width: 12 },
      detail: { fontSize: 16, offsetCenter: [0, '80%'], formatter: '{value}%' },
      title: { offsetCenter: [0, '110%'], fontSize: 12 },
      data: [{ value: 72, name: 'CPU' }],
    },
    {
      type: 'gauge', center: ['50%', '50%'], radius: '70%',
      min: 0, max: 100,
      progress: { show: true, width: 12 },
      detail: { fontSize: 16, offsetCenter: [0, '80%'], formatter: '{value}%' },
      title: { offsetCenter: [0, '110%'], fontSize: 12 },
      data: [{ value: 58, name: '内存' }],
    },
    {
      type: 'gauge', center: ['80%', '50%'], radius: '70%',
      min: 0, max: 100,
      progress: { show: true, width: 12 },
      detail: { fontSize: 16, offsetCenter: [0, '80%'], formatter: '{value}%' },
      title: { offsetCenter: [0, '110%'], fontSize: 12 },
      data: [{ value: 45, name: '磁盘' }],
    },
  ],
}
```

### 带颜色分段的仪表盘

```javascript
{
  series: [{
    type: 'gauge',
    min: 0, max: 100,
    progress: { show: true, width: 18 },
    axisLine: {
      lineStyle: {
        width: 18,
        color: [
          [0.3, '#91cc75'],
          [0.7, '#fac858'],
          [1, '#ee6666'],
        ],
      },
    },
    axisTick: { show: false },
    splitLine: { length: 15, lineStyle: { width: 3, color: '#auto' } },
    axisLabel: { distance: 25, color: '#999', fontSize: 12 },
    anchor: { show: true, showAbove: true, size: 25, itemStyle: { borderWidth: 10 } },
    pointer: { show: false },
    detail: { valueAnimation: true, fontSize: 30, offsetCenter: [0, '70%'], formatter: '{value}%' },
    title: { offsetCenter: [0, '100%'] },
    data: [{ value: 65 }],
  }],
}
```

### 环形进度条（无刻度简洁版）

```javascript
{
  series: [{
    type: 'gauge',
    min: 0, max: 100,
    startAngle: 90,
    endAngle: -270,
    progress: { show: true, width: 24, itemStyle: { color: '#5470c6' } },
    axisLine: { show: true, lineStyle: { width: 24, color: [[1, '#eee']] } },
    axisTick: { show: false },
    splitLine: { show: false },
    axisLabel: { show: false },
    pointer: { show: false },
    anchor: { show: false },
    detail: { valueAnimation: true, fontSize: 32, offsetCenter: [0, 0], formatter: '{value}%' },
    data: [{ value: 75 }],
  }],
}
```

### 带指针的传统仪表盘

```javascript
{
  series: [{
    type: 'gauge',
    min: 0, max: 200,
    splitNumber: 10,
    axisLine: { lineStyle: { width: 20 } },
    axisTick: { splitNumber: 5, lineStyle: { width: 2 } },
    splitLine: { length: 20, lineStyle: { width: 3 } },
    axisLabel: { fontSize: 12, color: '#999' },
    pointer: { show: true, length: '70%', width: 8, itemStyle: { color: '#5470c6' } },
    anchor: { show: true, size: 15, itemStyle: { color: '#5470c6' } },
    detail: { valueAnimation: true, fontSize: 24, offsetCenter: [0, '70%'], formatter: '{value} km/h' },
    title: { offsetCenter: [0, '100%'], fontSize: 14 },
    data: [{ name: '速度', value: 120 }],
  }],
}
```
