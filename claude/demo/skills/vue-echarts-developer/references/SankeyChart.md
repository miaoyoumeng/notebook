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

---

## 第 2 步：数据接入

### API 数据接入（含 Loading 和 Error 状态）

```vue
<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import VChart from 'vue-echarts'
import axios from 'axios'
import type { EChartsOption } from 'echarts'

const loading = ref(true)
const error = ref('')
const nodes = ref<any[]>([])
const links = ref<any[]>([])

const option = computed<EChartsOption>(() => ({
  tooltip: { trigger: 'item', triggerOn: 'mousemove' },
  series: [
    {
      type: 'sankey',
      layoutIterations: 32,
      data: nodes.value,
      links: links.value,
      label: { position: 'right' },
      lineStyle: { color: 'gradient', curveness: 0.5 },
    },
  ],
}))

onMounted(async () => {
  try {
    const res = await axios.get('/api/sankey-data')
    nodes.value = res.data.nodes
    links.value = res.data.links
  } catch (e: any) {
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

### 静态数据格式（nodes + links）

```javascript
const sankeyData = {
  nodes: [
    { name: '煤炭' },
    { name: '石油' },
    { name: '天然气' },
    { name: '电力' },
    { name: '工业' },
    { name: '交通' },
    { name: '居民' },
  ],
  links: [
    { source: '煤炭', target: '电力', value: 80 },
    { source: '石油', target: '交通', value: 60 },
    { source: '天然气', target: '居民', value: 30 },
    { source: '电力', target: '工业', value: 50 },
    { source: '电力', target: '居民', value: 30 },
  ],
}

const option = {
  tooltip: { trigger: 'item' },
  series: [{
    type: 'sankey',
    data: sankeyData.nodes,
    links: sankeyData.links,
    label: { position: 'right' },
    lineStyle: { color: 'gradient', curveness: 0.5 },
  }],
}
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
  height: 500px;
}

@media (max-width: 768px) {
  .chart {
    height: 350px;
  }
}
</style>
```

### 大数据量渲染（多节点多链路）

```javascript
const option = {
  series: [{
    type: 'sankey',
    data: manyNodes,
    links: manyLinks,
    layoutIterations: 0,
    animation: false,
    nodeWidth: 10,
    nodeGap: 8,
    label: { show: true, fontSize: 10 },
    lineStyle: { curveness: 0.5, opacity: 0.3 },
  }],
}
```

### 布局优化参数

```javascript
const option = {
  series: [{
    type: 'sankey',
    layoutIterations: 32,     // 布局迭代次数，越高越优但越慢
    nodeWidth: 20,            // 节点矩形宽度
    nodeGap: 8,               // 节点间垂直间距
    layout: 'none',           // 或 'vertical' 垂直布局
    dragble: true,            // 节点可拖拽调整位置
    emphasis: {
      focus: 'adjacency',     // 高亮相邻节点和链路
    },
  }],
}
```

---

## 第 4 步：主题适配

### 内置主题

```vue
<v-chart class="chart" :option="option" theme="dark" autoresize />
```

### 自定义主题（桑基图专属配色）

```javascript
import * as echarts from 'echarts'

echarts.registerTheme('sankey-theme', {
  color: [
    '#5470c6', '#91cc75', '#fac858',
    '#ee6666', '#73c0de', '#3ba272',
    '#fc8452', '#9a60b4', '#ea7ccc',
  ],
  backgroundColor: 'transparent',
  textStyle: { fontFamily: 'inherit', fontSize: 12 },
  series: {
    itemStyle: { borderColor: '#fff', borderWidth: 1 },
    lineStyle: { opacity: 0.3 },
  },
})
```

### 暗色模式切换

```vue
<script setup lang="ts">
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

### Tooltip 自定义（显示流量值）

```javascript
tooltip: {
  trigger: 'item',
  triggerOn: 'mousemove',
  formatter: (params) => {
    if (params.dataType === 'node') {
      return `${params.name}<br/>总量: ${params.value?.toLocaleString()}`
    }
    if (params.dataType === 'edge') {
      return `${params.data.source} → ${params.data.target}<br/>流量: ${params.data.value?.toLocaleString()}`
    }
    return ''
  },
}
```

### 高亮相邻节点和链路

```javascript
series: [{
  type: 'sankey',
  emphasis: {
    focus: 'adjacency',
    itemStyle: { borderWidth: 2, borderColor: '#333' },
    label: { show: true, fontWeight: 'bold' },
  },
  blur: {
    itemStyle: { opacity: 0.3 },
    lineStyle: { opacity: 0.1 },
  },
}]
```

### 节点可拖拽

```javascript
series: [{
  type: 'sankey',
  draggable: true,
  layout: 'none',
  emphasis: { focus: 'adjacency' },
}]
```

### 图表联动

```javascript
const sankeyOption = { groupId: 'energy-flow' }

chart1.on('highlight', (params) => {
  chart2.dispatchAction({
    type: 'highlight',
    seriesIndex: 0,
    dataIndex: params.dataIndex,
  })
})
```

---

## 常用桑基图配置速查

### 基础桑基图

```javascript
{
  tooltip: { trigger: 'item' },
  series: [{
    type: 'sankey',
    data: [
      { name: 'A' }, { name: 'B' }, { name: 'C' },
    ],
    links: [
      { source: 'A', target: 'B', value: 10 },
      { source: 'B', target: 'C', value: 8 },
    ],
    label: { position: 'right' },
    lineStyle: { color: 'gradient', curveness: 0.5 },
  }],
}
```

### 垂直布局桑基图

```javascript
{
  tooltip: { trigger: 'item' },
  series: [{
    type: 'sankey',
    orient: 'vertical',
    data: [
      { name: 'Source1' }, { name: 'Source2' },
      { name: 'Target1' }, { name: 'Target2' },
    ],
    links: [
      { source: 'Source1', target: 'Target1', value: 5 },
      { source: 'Source1', target: 'Target2', value: 3 },
      { source: 'Source2', target: 'Target1', value: 2 },
      { source: 'Source2', target: 'Target2', value: 7 },
    ],
    label: { position: 'bottom' },
    nodeWidth: 20,
    nodeGap: 12,
  }],
}
```

### 多层级桑基图

```javascript
{
  tooltip: { trigger: 'item' },
  series: [{
    type: 'sankey',
    layoutIterations: 32,
    data: [
      { name: '煤炭' }, { name: '石油' }, { name: '天然气' },
      { name: '电力' }, { name: '热力' },
      { name: '工业' }, { name: '交通' }, { name: '居民' },
    ],
    links: [
      { source: '煤炭', target: '电力', value: 80 },
      { source: '煤炭', target: '热力', value: 20 },
      { source: '石油', target: '交通', value: 60 },
      { source: '石油', target: '工业', value: 15 },
      { source: '天然气', target: '居民', value: 30 },
      { source: '天然气', target: '工业', value: 10 },
      { source: '电力', target: '工业', value: 50 },
      { source: '电力', target: '居民', value: 30 },
      { source: '热力', target: '居民', value: 15 },
    ],
    label: { fontSize: 11 },
    lineStyle: { color: 'gradient', curveness: 0.5 },
  }],
}
```

### 自定义节点颜色桑基图

```javascript
{
  tooltip: { trigger: 'item' },
  series: [{
    type: 'sankey',
    data: [
      { name: '直接访问', itemStyle: { color: '#5470c6' } },
      { name: '邮件营销', itemStyle: { color: '#91cc75' } },
      { name: '联盟广告', itemStyle: { color: '#fac858' } },
      { name: '视频广告', itemStyle: { color: '#ee6666' } },
      { name: '搜索引擎', itemStyle: { color: '#73c0de' } },
    ],
    links: [
      { source: '直接访问', target: '落地页', value: 300 },
      { source: '邮件营销', target: '落地页', value: 200 },
      { source: '联盟广告', target: '注册', value: 150 },
      { source: '视频广告', target: '注册', value: 100 },
      { source: '搜索引擎', target: '落地页', value: 500 },
    ],
    label: { position: 'right' },
    lineStyle: { color: 'source', curveness: 0.5 },
  }],
}
```
