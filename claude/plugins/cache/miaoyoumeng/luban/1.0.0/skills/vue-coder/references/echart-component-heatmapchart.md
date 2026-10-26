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

