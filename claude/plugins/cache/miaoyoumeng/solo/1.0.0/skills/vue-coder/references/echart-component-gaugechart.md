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

