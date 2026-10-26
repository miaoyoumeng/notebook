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

