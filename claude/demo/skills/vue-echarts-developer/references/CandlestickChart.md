# CandlestickChart — K线图完整参考

本文档包含 CandlestickChart 在 Vue 3 环境中的完整代码示例。各步骤详细说明请参见 `../SKILL.md`。

---

## 第 1 步：组件开发

### TypeScript 类型定义

```typescript
import type { EChartsOption } from 'echarts'

// OHLCV 数据格式：[日期, 开盘价, 收盘价, 最低价, 最高, 成交量]
interface CandlestickDataItem {
  date: string
  open: number
  close: number
  low: number
  high: number
  volume?: number
}

interface CandlestickProps {
  data: CandlestickDataItem[]
  title: string
  loading?: boolean
  showVolume?: boolean
}
```

### 基础组件模板（TypeScript + Composition API）

```vue
<script setup>
import { ref, computed, watch } from 'vue'
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { CandlestickChart, BarChart } from 'echarts/charts'
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
  DataZoomComponent,
  MarkLineComponent,
} from 'echarts/components'

// 按需注册
use([
  CanvasRenderer,
  CandlestickChart,
  BarChart,
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
  DataZoomComponent,
  MarkLineComponent,
])

const props = defineProps({
  data: { type: Array, default: () => [] },
  title: { type: String, default: '' },
  showVolume: { type: Boolean, default: true },
})

// K线数据格式: [open, close, low, high]
const candleData = computed(() =>
  props.data.map((d) => [d.open, d.close, d.low, d.high])
)
const volumeData = computed(() => props.data.map((d) => d.volume ?? 0))
const dates = computed(() => props.data.map((d) => d.date))

// 颜色约定：阳线（涨）红，阴线（跌）绿
const bullColor = '#ee6666'
const bearColor = '#91cc75'

const option = computed(() => {
  const grids = [
    { left: '5%', right: '5%', top: '10%', height: props.showVolume ? '55%' : '75%' },
  ]
  const series = [
    {
      name: 'K线',
      type: 'candlestick',
      data: candleData.value,
      xAxisIndex: 0,
      yAxisIndex: 0,
      itemStyle: {
        color: bullColor,
        color0: bearColor,
        borderColor: bullColor,
        borderColor0: bearColor,
      },
    },
  ]
  const yAxes = [{ type: 'value', scale: true, gridIndex: 0 }]

  if (props.showVolume) {
    grids.push({ left: '5%', right: '5%', top: '70%', height: '20%' })
    series.push({
      name: '成交量',
      type: 'bar',
      data: volumeData.value,
      xAxisIndex: 1,
      yAxisIndex: 1,
      itemStyle: (params) => ({
        color: params.dataIndex >= candleData.value.length
          ? bullColor
          : candleData.value[params.dataIndex][1] > candleData.value[params.dataIndex][0]
            ? bullColor
            : bearColor,
      }),
    })
    yAxes.push({ type: 'value', scale: true, gridIndex: 1, show: false })
  }

  return {
    title: { text: props.title, left: 'center' },
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'cross', link: { xAxisIndex: [0, 1] } },
    },
    legend: { bottom: 0, data: ['K线', '成交量'] },
    grid: grids,
    xAxis: [
      { type: 'category', data: dates.value, gridIndex: 0, axisLabel: { show: false } },
      { type: 'category', data: dates.value, gridIndex: 1, axisLabel: { show: true } },
    ],
    yAxis: yAxes,
    series,
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

@media (max-width: 768px) {
  .chart {
    height: 350px;
  }
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
const chartData = ref([])

const option = computed(() => ({
  tooltip: { trigger: 'axis' },
  grid: { left: '5%', right: '5%', top: '10%', bottom: '15%' },
  xAxis: {
    type: 'category',
    data: chartData.value.map((d) => d.date),
  },
  yAxis: { type: 'value', scale: true },
  series: [{
    name: 'K线',
    type: 'candlestick',
    data: chartData.value.map((d) => [d.open, d.close, d.low, d.high]),
    itemStyle: {
      color: '#ee6666',
      color0: '#91cc75',
      borderColor: '#ee6666',
      borderColor0: '#91cc75',
    },
  }],
}))

onMounted(async () => {
  try {
    const res = await axios.get('/api/stock/kline', {
      params: { symbol: 'SH000001', period: 'daily' },
    })
    chartData.value = res.data
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
.chart { width: 100%; height: 500px; }
.chart-error { color: #ee6666; padding: 20px; text-align: center; }
</style>
```

### Dataset 共享数据

```javascript
const option = {
  dataset: {
    source: [
      ['日期', '开盘', '收盘', '最低', '最高', '成交量'],
      ['2024-01-02', 3050, 3080, 3040, 3090, 120000],
      ['2024-01-03', 3080, 3060, 3050, 3095, 110000],
      ['2024-01-04', 3060, 3100, 3055, 3110, 135000],
      ['2024-01-05', 3100, 3070, 3060, 3105, 98000],
    ],
  },
  xAxis: { type: 'category' },
  yAxis: { type: 'value', scale: true },
  series: [
    {
      type: 'candlestick',
      name: 'K线',
      encode: { x: '日期', y: ['开盘', '收盘', '最低', '最高'] },
    },
    {
      type: 'bar',
      name: '成交量',
      yAxisIndex: 1,
      encode: { x: '日期', y: '成交量' },
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

K线图需要更高的垂直空间：

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

### 大数据量渲染（5000+ K线）

```javascript
const option = {
  xAxis: { type: 'category', data: dateArray },
  yAxis: { type: 'value', scale: true },
  dataZoom: [
    { type: 'slider', start: 80, end: 100, xAxisIndex: [0, 1] },
    { type: 'inside', start: 80, end: 100, xAxisIndex: [0, 1] },
  ],
  series: [{
    type: 'candlestick',
    data: candleArray,
    sampling: 'average',
    animation: false,
  }],
}
```

### 懒更新（避免全量重绘）

```javascript
chart.setOption(
  { series: [{ data: newCandleData }] },
  { replaceMerge: ['series'] }
)
```

---

## 第 4 步：主题适配

### 内置主题

```vue
<v-chart class="chart" :option="option" theme="dark" autoresize />
```

### K线自定义主题

```javascript
import * as echarts from 'echarts'

echarts.registerTheme('kline-theme', {
  color: ['#ee6666', '#91cc75', '#fac858', '#5470c6'],
  backgroundColor: 'transparent',
  textStyle: { fontFamily: 'monospace', fontSize: 11 },
  categoryAxis: { axisLine: { lineStyle: { color: '#555' } } },
  valueAxis: {
    scale: true,
    axisLine: { lineStyle: { color: '#555' } },
    splitLine: { lineStyle: { color: '#333' } },
  },
})
```

### A 股/美股颜色风格切换

```vue
<script setup>
import { computed } from 'vue'

const props = defineProps({
  market: { type: String, default: 'A' }, // 'A' | 'US'
})

// A股: 红涨绿跌 | 美股: 绿涨红跌
const candleStyle = computed(() =>
  props.market === 'A'
    ? { color: '#ee6666', color0: '#91cc75', borderColor: '#ee6666', borderColor0: '#91cc75' }
    : { color: '#91cc75', color0: '#ee6666', borderColor: '#91cc75', borderColor0: '#ee6666' }
)

const option = computed(() => ({
  // ...
  series: [{
    type: 'candlestick',
    data: candleData.value,
    itemStyle: candleStyle.value,
  }],
}))
</script>
```

---

## 第 5 步：交互增强

### Tooltip 自定义（OHLCV 信息展示）

```javascript
tooltip: {
  trigger: 'axis',
  axisPointer: { type: 'cross' },
  formatter: (params) => {
    const kline = params.find((p) => p.seriesName === 'K线')
    const vol = params.find((p) => p.seriesName === '成交量')
    if (!kline || !kline.value) return ''
    const [open, close, low, high] = kline.value
    const change = ((close - open) / open * 100).toFixed(2)
    const changeText = change >= 0 ? `+${change}%` : `${change}%`
    return `
      ${kline.name}<br/>
      开盘: ${open}<br/>
      收盘: ${close}<br/>
      最低: ${low}<br/>
      最高: ${high}<br/>
      涨跌: ${changeText}<br/>
      ${vol ? `成交量: ${vol.value?.toLocaleString()}` : ''}
    `
  },
}
```

### DataZoom 数据缩放

K线图必配 dataZoom，默认展示最近 60 个交易日：

```javascript
dataZoom: [
  {
    type: 'slider',
    start: 80,
    end: 100,
    xAxisIndex: [0, 1],
    bottom: 20,
  },
  {
    type: 'inside',
    start: 80,
    end: 100,
    xAxisIndex: [0, 1],
    zoomOnMouseWheel: true,
    moveOnMouseMove: true,
  },
]
```

### 标记线（均线/支撑/阻力）

```javascript
series: [{
  type: 'candlestick',
  data: candleData.value,
  markLine: {
    data: [
      { type: 'average', name: '均价', yAxis: 3080, label: { formatter: '3080' } },
      { yAxis: 3000, name: '支撑位', lineStyle: { type: 'dashed', color: '#fac858' } },
      { yAxis: 3200, name: '阻力位', lineStyle: { type: 'dashed', color: '#5470c6' } },
    ],
  },
}]
```

### 均线叠加（MA5/MA10/MA20）

```javascript
// 计算均线
function calcMA(data, period) {
  const result = []
  for (let i = 0; i < data.length; i++) {
    if (i < period - 1) {
      result.push('-')
      continue
    }
    let sum = 0
    for (let j = 0; j < period; j++) {
      sum += data[i - j][1] // 收盘价
    }
    result.push((sum / period).toFixed(2))
  }
  return result
}

const option = {
  // ...
  legend: { bottom: 0, data: ['K线', 'MA5', 'MA10', 'MA20'] },
  series: [
    { type: 'candlestick', name: 'K线', data: candleData },
    { type: 'line', name: 'MA5', data: calcMA(candleData, 5), smooth: true, showSymbol: false },
    { type: 'line', name: 'MA10', data: calcMA(candleData, 10), smooth: true, showSymbol: false },
    { type: 'line', name: 'MA20', data: calcMA(candleData, 20), smooth: true, showSymbol: false },
  ],
}
```

### 图表联动（K线 + 技术指标）

```javascript
// K线图与 MACD 副图联动
const klineOption = { groupId: 'stock' }
const macdOption = { groupId: 'stock' }

klineChart.on('highlight', (params) => {
  macdChart.dispatchAction({
    type: 'highlight',
    seriesIndex: 0,
    dataIndex: params.dataIndex,
  })
})
```

---

## 常用 K线图配置速查

### 基础 K线图

```javascript
{
  tooltip: { trigger: 'axis' },
  xAxis: { type: 'category', data: ['01-01', '01-02', '01-03', '01-04'] },
  yAxis: { type: 'value', scale: true },
  series: [{
    type: 'candlestick',
    data: [
      [3000, 3050, 2990, 3060],
      [3050, 3020, 3010, 3070],
      [3020, 3100, 3015, 3110],
      [3100, 3080, 3070, 3120],
    ],
    itemStyle: {
      color: '#ee6666',
      color0: '#91cc75',
      borderColor: '#ee6666',
      borderColor0: '#91cc75',
    },
  }],
}
```

### K线 + 成交量（双图联动）

```javascript
{
  tooltip: { trigger: 'axis' },
  grid: [
    { left: '5%', right: '5%', top: '10%', height: '55%' },
    { left: '5%', right: '5%', top: '70%', height: '20%' },
  ],
  xAxis: [
    { type: 'category', data: dates, gridIndex: 0, axisLabel: { show: false } },
    { type: 'category', data: dates, gridIndex: 1 },
  ],
  yAxis: [
    { type: 'value', scale: true, gridIndex: 0 },
    { type: 'value', scale: true, gridIndex: 1, show: false },
  ],
  series: [
    { type: 'candlestick', data: candleData, itemStyle: { color: '#ee6666', color0: '#91cc75' } },
    { type: 'bar', data: volumeData, xAxisIndex: 1, yAxisIndex: 1 },
  ],
}
```

### K线 + 均线叠加

```javascript
{
  tooltip: { trigger: 'axis' },
  legend: { bottom: 0, data: ['K线', 'MA5', 'MA10', 'MA20'] },
  xAxis: { type: 'category', data: dates },
  yAxis: { type: 'value', scale: true },
  series: [
    { type: 'candlestick', name: 'K线', data: candleData },
    { type: 'line', name: 'MA5', data: ma5Data, smooth: true, showSymbol: false },
    { type: 'line', name: 'MA10', data: ma10Data, smooth: true, showSymbol: false },
    { type: 'line', name: 'MA20', data: ma20Data, smooth: true, showSymbol: false },
  ],
}
```

### K线 + 数据缩放

```javascript
{
  tooltip: { trigger: 'axis' },
  xAxis: { type: 'category', data: longDateArray },
  yAxis: { type: 'value', scale: true },
  dataZoom: [
    { type: 'slider', start: 80, end: 100, xAxisIndex: [0, 1] },
    { type: 'inside', start: 80, end: 100, xAxisIndex: [0, 1] },
  ],
  series: [{
    type: 'candlestick',
    data: longCandleArray,
    itemStyle: { color: '#ee6666', color0: '#91cc75' },
  }],
}
```

### K线 + MACD 副图

```javascript
{
  grid: [
    { left: '5%', right: '5%', top: '10%', height: '50%' },
    { left: '5%', right: '5%', top: '65%', height: '20%' },
  ],
  xAxis: [
    { type: 'category', data: dates, gridIndex: 0, axisLabel: { show: false } },
    { type: 'category', data: dates, gridIndex: 1 },
  ],
  yAxis: [
    { type: 'value', scale: true, gridIndex: 0 },
    { type: 'value', gridIndex: 1, show: false },
  ],
  series: [
    { type: 'candlestick', data: candleData, xAxisIndex: 0, yAxisIndex: 0 },
    { type: 'bar', name: 'MACD', data: macdData, xAxisIndex: 1, yAxisIndex: 1,
      itemStyle: (params) => ({
        color: params.value > 0 ? '#ee6666' : '#91cc75',
      }),
    },
  ],
}
```
