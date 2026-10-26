# TreemapChart — 树形图完整参考

本文档包含 TreemapChart 在 Vue 3 环境中的完整代码示例。各步骤详细说明请参见 `../SKILL.md`。

---

## 第 1 步：组件开发

### TypeScript 类型定义

```typescript
import type { EChartsOption } from 'echarts'

interface TreeNode {
  name: string
  value: number
  children?: TreeNode[]
  [key: string]: any
}

interface TreemapProps {
  data: TreeNode[]
  title: string
  loading?: boolean
}
```

### 基础组件模板（TypeScript + Composition API）

```vue
<script setup>
import { ref, computed } from 'vue'
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { TreemapChart } from 'echarts/charts'
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
} from 'echarts/components'

// 按需注册
use([
  CanvasRenderer,
  TreemapChart,
  TitleComponent,
  TooltipComponent,
  LegendComponent,
])

const props = defineProps({
  data: { type: Array, default: () => [] },
  title: { type: String, default: '' },
})

const option = computed(() => ({
  title: { text: props.title, left: 'center' },
  tooltip: {
    formatter: (params) => {
      const { name, value } = params
      return `${name}: ${value.toLocaleString()}`
    },
  },
  series: [
    {
      type: 'treemap',
      data: props.data,
      roam: false,
      nodeClick: false,
      label: {
        show: true,
        formatter: '{b}\n{c}',
        fontSize: 12,
      },
      breadcrumb: { show: true, top: 30 },
      levels: [
        {
          itemStyle: { borderWidth: 1, gapWidth: 2 },
        },
        {
          itemStyle: { borderWidth: 0, gapWidth: 2 },
        },
        {
          colorSaturation: [0.35, 0.5],
          itemStyle: { borderWidth: 2, gapWidth: 2, borderColorSaturation: 0.6 },
        },
      ],
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
  height: 500px;
}
</style>
```

