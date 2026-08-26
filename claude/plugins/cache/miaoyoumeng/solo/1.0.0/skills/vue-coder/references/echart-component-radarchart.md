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

