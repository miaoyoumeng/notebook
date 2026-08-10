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

---

## 第 2 步：数据接入

### API 数据接入（含 Loading 和 Error 状态）

```vue
<script setup>
import { ref, computed, onMounted } from 'vue'
import VChart from 'vue-echarts'
import axios from 'axios'
import type { EChartsOption } from 'echarts'

const loading = ref(true)
const error = ref('')
const treemapData = ref<any[]>([])

const option = computed<EChartsOption>(() => ({
  tooltip: { formatter: '{b}: {c}' },
  series: [{
    type: 'treemap',
    data: treemapData.value,
    roam: false,
    nodeClick: false,
    label: { show: true, formatter: '{b}\n{c}' },
    breadcrumb: { show: true },
    levels: [
      { itemStyle: { borderWidth: 1, gapWidth: 2 } },
      { itemStyle: { borderWidth: 0, gapWidth: 2 } },
    ],
  }],
}))

onMounted(async () => {
  try {
    const res = await axios.get('/api/treemap-data')
    treemapData.value = res.data
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

### 静态树形数据（多层级）

```javascript
const option = {
  tooltip: { formatter: '{b}: {c} ({d}%)' },
  series: [{
    type: 'treemap',
    width: '100%',
    height: '90%',
    top: '10%',
    data: [
      {
        name: '电子产品',
        value: 500,
        children: [
          { name: '手机', value: 200 },
          { name: '笔记本', value: 180 },
          { name: '平板', value: 120 },
        ],
      },
      {
        name: '服装',
        value: 300,
        children: [
          { name: '男装', value: 120 },
          { name: '女装', value: 150 },
          { name: '童装', value: 30 },
        ],
      },
      {
        name: '食品',
        value: 200,
        children: [
          { name: '零食', value: 80 },
          { name: '饮料', value: 70 },
          { name: '生鲜', value: 50 },
        ],
      },
    ],
    levels: [
      {
        itemStyle: { borderWidth: 1, gapWidth: 3 },
        label: { show: true, fontSize: 14, fontWeight: 'bold' },
      },
      {
        itemStyle: { borderWidth: 0, gapWidth: 2 },
        label: { show: true, fontSize: 12 },
      },
      {
        colorSaturation: [0.35, 0.5],
        itemStyle: { borderWidth: 2, gapWidth: 1, borderColorSaturation: 0.6 },
        label: { show: false },
      },
    ],
    breadcrumb: { show: true, top: 30, height: 20 },
  }],
}
```

### Dataset 扁平数据转树形结构

```javascript
// 扁平数据 → 树形结构转换
function flatToTree(flatData, categoryField, subField, valueField) {
  const tree = {}
  for (const item of flatData) {
    const cat = item[categoryField]
    const sub = item[subField]
    if (!tree[cat]) {
      tree[cat] = { name: cat, value: 0, children: [] }
    }
    const child = { name: sub, value: item[valueField] }
    tree[cat].children.push(child)
    tree[cat].value += item[valueField]
  }
  return Object.values(tree)
}

const flatData = [
  { category: '华东', sub: '上海', value: 300 },
  { category: '华东', sub: '杭州', value: 200 },
  { category: '华南', sub: '广州', value: 180 },
  { category: '华南', sub: '深圳', value: 250 },
]

const treeData = flatToTree(flatData, 'category', 'sub', 'value')

const option = {
  series: [{
    type: 'treemap',
    data: treeData,
    roam: false,
    nodeClick: false,
    levels: [
      { itemStyle: { borderWidth: 1, gapWidth: 3 } },
      { itemStyle: { borderWidth: 0, gapWidth: 2 } },
    ],
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

### 大数据量优化（500+ 节点）

```javascript
const option = {
  series: [{
    type: 'treemap',
    data: largeTreeData,
    visibleMin: 10,  // 面积小于 10px 的节点不显示标签
    roam: false,
    nodeClick: 'zoomToNode',
    label: {
      show: true,
      formatter: (params) => {
        // 只显示面积足够的节点标签
        return params.treePathInfo.length <= 2 ? '{b}' : ''
      },
    },
    levels: [
      { itemStyle: { borderWidth: 1, gapWidth: 2 } },
      { itemStyle: { borderWidth: 0, gapWidth: 1 }, label: { show: false } },
    ],
  }],
}
```

### 懒更新（避免全量重绘）

```javascript
chart.setOption({ series: [{ data: newTreeData }] }, { replaceMerge: ['series'] })
```

---

## 第 4 步：主题适配

### 内置主题

```vue
<v-chart class="chart" :option="option" theme="dark" autoresize />
```

### 自定义颜色映射

```javascript
const option = {
  series: [{
    type: 'treemap',
    data: treeData,
    colorMappingBy: 'value',  // 按值映射颜色深浅
    visibleMin: 10,
    colorSaturation: [0.2, 0.6],  // 颜色饱和度范围
    levels: [
      {
        itemStyle: {
          borderColor: '#fff',
          borderWidth: 1,
          gapWidth: 2,
          borderRadius: 4,
        },
      },
      {
        itemStyle: {
          gapWidth: 2,
        },
      },
    ],
  }],
}
```

### 暗色模式适配

```vue
<script setup>
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

### Tooltip 自定义（含层级路径）

```javascript
tooltip: {
  formatter: (params) => {
    const path = params.treePathInfo
      .map((p) => p.name)
      .filter(Boolean)
      .join(' > ')
    return `${path}<br/>数值: ${params.value.toLocaleString()}`
  },
}
```

### 支持下钻交互

```javascript
series: [{
  type: 'treemap',
  data: treeData,
  roam: false,
  nodeClick: 'zoomToNode',  // 点击节点下钻
  breadcrumb: {
    show: true,
    top: 30,
    height: 20,
    itemStyle: {
      color: 'rgba(0,0,0,0.05)',
    },
  },
  levels: [
    { itemStyle: { borderWidth: 1, gapWidth: 3 } },
    { itemStyle: { borderWidth: 0, gapWidth: 2 } },
  ],
}]
```

### 与饼图联动（同一数据集的不同展示）

```javascript
// 共享同一份数据，两种展示方式
const rawData = [
  { name: '类别A', value: 300 },
  { name: '类别B', value: 200 },
  { name: '类别C', value: 150 },
]

// 饼图 option
const pieOption = {
  series: [{
    type: 'pie',
    data: rawData,
    radius: ['40%', '70%'],
  }],
}

// 树形图 option（单层）
const treemapOption = {
  series: [{
    type: 'treemap',
    data: rawData,
    roam: false,
    nodeClick: false,
    label: { show: true, formatter: '{b}: {c}' },
  }],
}
```

---

## 常用树形图配置速查

### 基础树形图

```javascript
{
  tooltip: { formatter: '{b}: {c}' },
  series: [{
    type: 'treemap',
    data: [
      { name: 'A', value: 100 },
      { name: 'B', value: 80 },
      { name: 'C', value: 60 },
    ],
    roam: false,
    nodeClick: false,
    label: { show: true },
  }],
}
```

### 多层级树形图

```javascript
{
  tooltip: { formatter: '{b}: {c}' },
  breadcrumb: { show: true, top: 30 },
  series: [{
    type: 'treemap',
    data: [
      {
        name: '华东',
        value: 500,
        children: [
          { name: '上海', value: 300 },
          { name: '杭州', value: 200 },
        ],
      },
      {
        name: '华南',
        value: 430,
        children: [
          { name: '广州', value: 180 },
          { name: '深圳', value: 250 },
        ],
      },
    ],
    levels: [
      { itemStyle: { borderWidth: 1, gapWidth: 3 }, label: { fontSize: 14 } },
      { itemStyle: { borderWidth: 0, gapWidth: 2 }, label: { fontSize: 12 } },
    ],
  }],
}
```

### 可下钻树形图

```javascript
{
  tooltip: { formatter: '{b}: {c}' },
  series: [{
    type: 'treemap',
    data: multiLevelData,
    roam: false,
    nodeClick: 'zoomToNode',
    breadcrumb: { show: true, top: 30 },
    levels: [
      { itemStyle: { borderWidth: 2, gapWidth: 3, borderRadius: 4 } },
      { itemStyle: { borderWidth: 1, gapWidth: 2 } },
      { itemStyle: { borderWidth: 0, gapWidth: 1 } },
    ],
  }],
}
```

### 带颜色深浅映射的树形图

```javascript
{
  tooltip: { formatter: '{b}: {c}' },
  series: [{
    type: 'treemap',
    data: treeData,
    colorMappingBy: 'value',
    colorSaturation: [0.2, 0.6],
    roam: false,
    nodeClick: false,
    levels: [
      {
        itemStyle: {
          borderColor: '#fff',
          borderWidth: 1,
          gapWidth: 2,
          borderRadius: 4,
        },
      },
      { itemStyle: { gapWidth: 2 } },
    ],
  }],
}
```
