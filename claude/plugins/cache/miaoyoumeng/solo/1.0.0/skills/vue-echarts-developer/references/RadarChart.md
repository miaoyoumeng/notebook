# RadarChart — 雷达图完整参考

本文档包含 RadarChart 在 Vue 3 环境中的完整代码示例。各步骤详细说明请参见 `../SKILL.md`。

---

## 第 1 步：组件开发

### TypeScript 类型定义

```typescript
import type { EChartsOption } from 'echarts'

interface RadarIndicator {
  name: string
  max?: number
  min?: number
}

interface RadarSeriesData {
  name: string
  value: number[]
}

interface ChartProps {
  indicators: RadarIndicator[]
  series: RadarSeriesData[]
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
import { RadarChart } from 'echarts/charts'
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
} from 'echarts/components'

// 按需注册
use([
  CanvasRenderer,
  RadarChart,
  TitleComponent,
  TooltipComponent,
  LegendComponent,
])

const props = defineProps({
  indicators: { type: Array, default: () => [] },
  series: { type: Array, default: () => [] },
  title: { type: String, default: '' },
})

const option = computed(() => ({
  title: { text: props.title, left: 'center' },
  tooltip: { trigger: 'item' },
  legend: { bottom: 0 },
  radar: {
    indicator: props.indicators,
    radius: '65%',
    center: ['50%', '50%'],
  },
  series: [{
    type: 'radar',
    data: props.series,
  }],
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

const loading = ref(true)
const error = ref('')
const indicators = ref([])
const seriesData = ref([])

const option = computed(() => ({
  tooltip: { trigger: 'item' },
  legend: { bottom: 0 },
  radar: { indicator: indicators.value, radius: '65%' },
  series: [{
    type: 'radar',
    data: seriesData.value,
  }],
}))

onMounted(async () => {
  try {
    const res = await axios.get('/api/radar-data')
    indicators.value = res.data.indicators
    seriesData.value = res.data.series
  } catch (e) {
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
const indicators = [
  { name: '销售', max: 100 },
  { name: '管理', max: 100 },
  { name: '技术', max: 100 },
  { name: '客服', max: 100 },
  { name: '研发', max: 100 },
]

const seriesData = [
  {
    name: '预算分配',
    value: [80, 70, 60, 90, 85],
    areaStyle: { opacity: 0.3 },
  },
  {
    name: '实际开销',
    value: [70, 75, 65, 80, 78],
    areaStyle: { opacity: 0.3 },
  },
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
    height: 300px;
  }
}
</style>
```

### 大数据量渲染（多指标场景）

```javascript
const option = {
  radar: {
    indicator: largeIndicatorArray,
    radius: '70%',
    splitNumber: 4,
  },
  series: [{
    type: 'radar',
    data: seriesData,
    animation: false,
    symbol: 'none',
  }],
}
```

### 懒更新（避免全量重绘）

```javascript
chart.setOption({
  series: [{ data: newData }],
}, { replaceMerge: ['series'] })
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
  radar: {
    axisLine: { lineStyle: { color: '#ccc' } },
    splitLine: { lineStyle: { color: '#666' } },
    splitArea: { areaStyle: { color: ['rgba(100,100,100,0.1)', 'rgba(100,100,100,0.2)'] } },
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
  trigger: 'item',
  formatter: (params) => {
    const values = params.data.value
      .map((v, i) => `${params.seriesName} - ${v}`)
      .join('<br/>')
    return `${params.name}<br/>${values}`
  },
}
```

### Toolbox 工具箱

```javascript
toolbox: {
  feature: {
    saveAsImage: { title: '保存图片' },
    restore: { title: '还原' },
  },
}
```

### 图表联动（多雷达图同步高亮）

```javascript
const option1 = { groupId: 'radar-group' }
const option2 = { groupId: 'radar-group' }

chart1.on('highlight', (params) => {
  chart2.dispatchAction({
    type: 'highlight',
    seriesIndex: params.seriesIndex,
    dataIndex: params.dataIndex,
  })
})
```

---

## 常用雷达图配置速查

### 基础雷达图

```javascript
{
  tooltip: { trigger: 'item' },
  radar: {
    indicator: [
      { name: '销售', max: 100 },
      { name: '管理', max: 100 },
      { name: '技术', max: 100 },
      { name: '客服', max: 100 },
      { name: '研发', max: 100 },
    ],
    radius: '65%',
  },
  series: [{
    type: 'radar',
    data: [{ name: '预算', value: [80, 70, 60, 90, 85] }],
  }],
}
```

### 多系列雷达图

```javascript
{
  tooltip: { trigger: 'item' },
  legend: { bottom: 0 },
  radar: {
    indicator: [
      { name: '销售', max: 100 },
      { name: '管理', max: 100 },
      { name: '技术', max: 100 },
      { name: '客服', max: 100 },
      { name: '研发', max: 100 },
    ],
    radius: '65%',
  },
  series: [{
    type: 'radar',
    data: [
      { name: '预算', value: [80, 70, 60, 90, 85], areaStyle: { opacity: 0.3 } },
      { name: '实际', value: [70, 75, 65, 80, 78], areaStyle: { opacity: 0.3 } },
    ],
  }],
}
```

### 带面积填充的雷达图

```javascript
{
  tooltip: { trigger: 'item' },
  radar: {
    indicator: [
      { name: '攻击力', max: 100 },
      { name: '防御力', max: 100 },
      { name: '速度', max: 100 },
      { name: '体力', max: 100 },
      { name: '技巧', max: 100 },
    ],
    radius: '60%',
    axisName: { fontSize: 12, color: '#333' },
    splitArea: {
      areaStyle: {
        color: ['rgba(84,112,198,0.1)', 'rgba(84,112,198,0.2)', 'rgba(84,112,198,0.3)'],
      },
    },
  },
  series: [{
    type: 'radar',
    data: [{
      name: '角色属性',
      value: [90, 70, 85, 60, 75],
      areaStyle: { opacity: 0.4, color: '#5470c6' },
      lineStyle: { width: 2, color: '#5470c6' },
      itemStyle: { color: '#5470c6' },
    }],
  }],
}
```

### 多雷达图并列（对比评估）

```vue
<template>
  <div class="radar-grid">
    <div class="radar-item">
      <v-chart :option="optionA" autoresize />
    </div>
    <div class="radar-item">
      <v-chart :option="optionB" autoresize />
    </div>
  </div>
</template>

<style scoped>
.radar-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
}
.radar-item .chart {
  width: 100%;
  height: 350px;
}
</style>
```

```javascript
// optionA 和 optionB 使用相同的 indicator 但不同的 series data
const optionA = {
  title: { text: '员工 A 能力评估', left: 'center', textStyle: { fontSize: 14 } },
  radar: { indicator: commonIndicators, radius: '60%' },
  series: [{ type: 'radar', data: [{ name: 'A', value: [90, 80, 70, 85, 75] }] }],
}

const optionB = {
  title: { text: '员工 B 能力评估', left: 'center', textStyle: { fontSize: 14 } },
  radar: { indicator: commonIndicators, radius: '60%' },
  series: [{ type: 'radar', data: [{ name: 'B', value: [70, 85, 90, 60, 80] }] }],
}
```
