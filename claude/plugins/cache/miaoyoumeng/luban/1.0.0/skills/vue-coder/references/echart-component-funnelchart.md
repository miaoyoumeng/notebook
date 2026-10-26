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

