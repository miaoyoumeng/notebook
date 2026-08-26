# FunnelChart — 漏斗图完整参考

本文档包含 FunnelChart 在 Vue 3 环境中的完整代码示例。各步骤详细说明请参见 `../SKILL.md`。

---

## 第 1 步：组件开发

### TypeScript 类型定义

```typescript
import type { EChartsOption } from 'echarts'

interface FunnelDataItem {
  name: string
  value: number
  [key: string]: any
}

interface FunnelProps {
  data: FunnelDataItem[]
  title: string
  loading?: boolean
  sort?: 'ascending' | 'descending' | 'none'
  orient?: 'vertical' | 'horizontal'
}
```

### 基础组件模板（TypeScript + Composition API）

```vue
<script setup>
import { ref, computed, watch } from 'vue'
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { FunnelChart } from 'echarts/charts'
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
} from 'echarts/components'

// 按需注册（漏斗图不需要 GridComponent）
use([
  CanvasRenderer,
  FunnelChart,
  TitleComponent,
  TooltipComponent,
  LegendComponent,
])

const props = defineProps({
  data: { type: Array, default: () => [] },
  title: { type: String, default: '' },
  sort: { type: String, default: 'descending' },
})

const option = computed(() => ({
  title: { text: props.title, left: 'center' },
  tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)' },
  legend: { bottom: 0 },
  series: [
    {
      name: '转化漏斗',
      type: 'funnel',
      left: '20%',
      right: '20%',
      top: 60,
      bottom: 60,
      width: '60%',
      min: 0,
      max: 1000,
      minSize: '0%',
      maxSize: '100%',
      sort: props.sort,
      gap: 2,
      label: {
        show: true,
        formatter: '{b}: {c}',
      },
      labelLine: { length: 10, lineStyle: { width: 1, type: 'solid' } },
      itemStyle: { borderColor: '#fff', borderWidth: 1 },
      data: props.data,
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
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { FunnelChart } from 'echarts/charts'
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
} from 'echarts/components'
import axios from 'axios'
import type { EChartsOption } from 'echarts'

use([CanvasRenderer, FunnelChart, TitleComponent, TooltipComponent, LegendComponent])

const loading = ref(true)
const error = ref('')
const chartData = ref<any[]>([])

const option = computed<EChartsOption>(() => ({
  title: { text: '转化漏斗', left: 'center' },
  tooltip: { trigger: 'item', formatter: '{b}: {c}人 ({d}%)' },
  series: [{
    type: 'funnel',
    left: '20%',
    right: '20%',
    top: 60,
    bottom: 60,
    width: '60%',
    min: 0,
    max: 1000,
    sort: 'descending',
    gap: 2,
    label: { show: true, formatter: '{b}: {c}人' },
    itemStyle: { borderColor: '#fff', borderWidth: 1 },
    data: chartData.value,
  }],
}))

onMounted(async () => {
  try {
    const res = await axios.get('/api/funnel-data')
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

### Dataset 共享数据（多漏斗对比）

```javascript
const option = {
  title: { text: '多渠道转化漏斗对比', left: 'center' },
  tooltip: { trigger: 'item', formatter: '{a}: {b} ({c}人)' },
  legend: { bottom: 0 },
  series: [
    {
      name: 'PC端',
      type: 'funnel',
      left: '5%',
      right: '55%',
      width: '40%',
      sort: 'descending',
      label: { position: 'inside', formatter: '{b}: {c}' },
      data: [
        { value: 1000, name: '访问' },
        { value: 600, name: '咨询' },
        { value: 300, name: '订单' },
        { value: 150, name: '支付' },
      ],
    },
    {
      name: '移动端',
      type: 'funnel',
      left: '55%',
      right: '5%',
      width: '40%',
      sort: 'descending',
      label: { position: 'inside', formatter: '{b}: {c}' },
      data: [
        { value: 2000, name: '访问' },
        { value: 800, name: '咨询' },
        { value: 200, name: '订单' },
        { value: 80, name: '支付' },
      ],
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
    height: 300px;
  }
}
</style>
```

### 大数据量标签适配

```javascript
const option = {
  series: [{
    type: 'funnel',
    data: largeFunnelData,
    label: {
      show: true,
      formatter: (params) => {
        if (largeFunnelData.length > 10) {
          return params.name
        }
        return `${params.name}: ${params.value}`
      },
    },
    labelLine: {
      show: largeFunnelData.length <= 10,
    },
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

echarts.registerTheme('funnel-theme', {
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
  formatter: (params) => {
    const percent = ((params.value / maxVal) * 100).toFixed(1)
    return `${params.name}<br/>
      数量: ${params.value.toLocaleString()}<br/>
      占比: ${percent}%`
  },
}
```

### 转化率标签（核心交互）

```javascript
series: [{
  type: 'funnel',
  data: funnelData,
  label: {
    show: true,
    position: 'outside',
    formatter: (params) => {
      const idx = funnelData.findIndex(d => d.name === params.name)
      if (idx === 0) return `${params.name}: ${params.value}`
      const prev = funnelData[idx - 1].value
      const rate = ((params.value / prev) * 100).toFixed(1)
      return `${params.name}: ${params.value} (转化率 ${rate}%)`
    },
  },
}]
```

### 点击事件（转化明细跳转）

```vue
<script setup>
import { ref, computed, onMounted } from 'vue'
import VChart from 'vue-echarts'

const chartRef = ref(null)

const onFunnelClick = (params) => {
  emit('stage-select', params.name)
  router.push({ path: `/funnel/${params.name}/detail` })
}
</script>

<template>
  <v-chart
    ref="chartRef"
    class="chart"
    :option="option"
    autoresize
    @click="onFunnelClick"
  />
</template>
```

### 排序切换

```javascript
const sortMode = ref('descending')

const toggleSort = () => {
  sortMode.value = sortMode.value === 'descending' ? 'ascending' : 'descending'
  chart.setOption({
    series: [{ sort: sortMode.value }],
  })
}
```

---

## 常用漏斗图配置速查

### 基础漏斗图

```javascript
{
  tooltip: { trigger: 'item' },
  series: [{
    type: 'funnel',
    left: '20%',
    right: '20%',
    top: 60,
    bottom: 60,
    width: '60%',
    sort: 'descending',
    gap: 2,
    label: { show: true, formatter: '{b}: {c}' },
    data: [
      { value: 100, name: '访问' },
      { value: 80, name: '咨询' },
      { value: 60, name: '订单' },
      { value: 40, name: '支付' },
      { value: 20, name: '复购' },
    ],
  }],
}
```

### 金字塔图（ascending 排序）

```javascript
{
  tooltip: { trigger: 'item' },
  series: [{
    type: 'funnel',
    sort: 'ascending',
    left: '20%',
    right: '20%',
    top: 60,
    bottom: 60,
    width: '60%',
    gap: 2,
    label: { show: true, formatter: '{b}: {c}' },
    data: [
      { value: 20, name: '复购' },
      { value: 40, name: '支付' },
      { value: 60, name: '订单' },
      { value: 80, name: '咨询' },
      { value: 100, name: '访问' },
    ],
  }],
}
```

### 双漏斗对比（左右并排）

```javascript
{
  tooltip: { trigger: 'item', formatter: '{a}: {b} ({c}人)' },
  legend: { bottom: 0 },
  series: [
    {
      name: '目标',
      type: 'funnel',
      left: '5%',
      right: '55%',
      width: '40%',
      sort: 'descending',
      data: [
        { value: 1000, name: '线索' },
        { value: 500, name: '商机' },
        { value: 200, name: '成交' },
      ],
    },
    {
      name: '实际',
      type: 'funnel',
      left: '55%',
      right: '5%',
      width: '40%',
      sort: 'descending',
      data: [
        { value: 800, name: '线索' },
        { value: 350, name: '商机' },
        { value: 150, name: '成交' },
      ],
    },
  ],
}
```

### 带转化率的漏斗图

```javascript
{
  tooltip: {
    trigger: 'item',
    formatter: (params) => {
      const idx = funnelData.findIndex(d => d.name === params.name)
      const rate = idx === 0 ? '100' : ((params.value / funnelData[idx - 1].value) * 100).toFixed(1)
      return `${params.name}: ${params.value}人<br/>转化率: ${rate}%`
    },
  },
  series: [{
    type: 'funnel',
    sort: 'descending',
    gap: 2,
    label: {
      formatter: (params) => {
        const idx = funnelData.findIndex(d => d.name === params.name)
        if (idx === 0) return `${params.name}: ${params.value}`
        const rate = ((params.value / funnelData[idx - 1].value) * 100).toFixed(1)
        return `${params.name}\n${params.value} (转化 ${rate}%)`
      },
    },
    data: funnelData,
  }],
}
```

### 水平漏斗图

```javascript
{
  tooltip: { trigger: 'item' },
  series: [{
    type: 'funnel',
    orient: 'horizontal',
    left: '10%',
    right: '10%',
    top: '10%',
    bottom: '10%',
    sort: 'descending',
    gap: 2,
    label: { show: true, position: 'inside', formatter: '{b}: {c}' },
    data: [
      { value: 100, name: '曝光' },
      { value: 60, name: '点击' },
      { value: 30, name: '转化' },
    ],
  }],
}
```
