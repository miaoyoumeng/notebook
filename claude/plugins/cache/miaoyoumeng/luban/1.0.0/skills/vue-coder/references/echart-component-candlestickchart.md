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

