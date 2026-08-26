# SankeyChart — 桑基图完整参考

本文档包含 SankeyChart 在 Vue 3 环境中的完整代码示例。各步骤详细说明请参见 `../SKILL.md`。

---

## 第 1 步：组件开发

### TypeScript 类型定义

```typescript
import type { EChartsOption } from 'echarts'

interface SankeyNode {
  name: string
  value?: number
  itemStyle?: {
    color?: string
    borderColor?: string
    borderWidth?: number
  }
}

interface SankeyLink {
  source: string
  target: string
  value: number
  lineStyle?: {
    color?: string
    curveness?: number
  }
}

interface SankeyChartProps {
  nodes: SankeyNode[]
  links: SankeyLink[]
  title?: string
  loading?: boolean
  direction?: 'horizontal' | 'vertical'
}
```

### 基础组件模板（TypeScript + Composition API）

```vue
<script setup lang="ts">
import { computed } from 'vue'
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { SankeyChart } from 'echarts/charts'
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
} from 'echarts/components'
import type { SankeyNode, SankeyLink } from './types'

// 按需注册
use([
  CanvasRenderer,
  SankeyChart,
  TitleComponent,
  TooltipComponent,
  LegendComponent,
])

interface Props {
  nodes: SankeyNode[]
  links: SankeyLink[]
  title?: string
  loading?: boolean
  direction?: 'horizontal' | 'vertical'
}

const props = withDefaults(defineProps<Props>(), {
  title: '',
  loading: false,
  direction: 'horizontal',
})

const option = computed<EChartsOption>(() => ({
  title: { text: props.title, left: 'center' },
  tooltip: { trigger: 'item', triggerOn: 'mousemove' },
  series: [
    {
      type: 'sankey',
      layout: 'none',
      focusNodeAdjacency: true,
      data: props.nodes,
      links: props.links,
      orient: props.direction,
      label: { position: 'right', fontSize: 12 },
      lineStyle: { color: 'gradient', curveness: 0.5 },
      itemStyle: { borderWidth: 0 },
      emphasis: { focus: 'adjacency' },
    },
  ],
}))
</script>

<template>
  <v-chart class="chart" :option="option" :loading="loading" autoresize />
</template>

<style scoped>
.chart {
  width: 100%;
  height: 500px;
}
</style>
```

