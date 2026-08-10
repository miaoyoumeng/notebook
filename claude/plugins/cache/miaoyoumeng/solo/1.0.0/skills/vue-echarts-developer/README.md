# vue-echarts-developer

在 Vue 3 环境中使用 Apache ECharts 开发图表功能，支持按需引入、主题适配和性能优化。

## 支持的图表类型

| 图表 | 场景 |
|------|------|
| 折线图/面积图 | 趋势变化、时间序列 |
| 柱状图 | 分类对比、堆叠/横向 |
| 饼图/环形图 | 占比关系 |
| 散点图/气泡图 | 相关性、分布 |
| 雷达图 | 多维评分对比 |
| 仪表盘 | 单指标 vs 目标 |
| 热力图 | 矩阵密度、活跃度 |
| 漏斗图 | 流程转化、流失率 |
| 树形图 | 层级占比、下钻分析 |
| 桑基图 | 流向关系、路径转化 |
| K线图 | 金融行情走势 |

## 安装

```bash
pnpm add echarts vue-echarts
```

## 快速开始

```vue
<script setup lang="ts">
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { LineChart } from 'echarts/charts'
import { TitleComponent, TooltipComponent, LegendComponent, GridComponent } from 'echarts/components'
import VChart, { type EChartsOption } from 'vue-echarts'

use([CanvasRenderer, LineChart, TitleComponent, TooltipComponent, LegendComponent, GridComponent])

const option: EChartsOption = {
  xAxis: { type: 'category', data: ['周一', '周二', '周三'] },
  yAxis: { type: 'value' },
  series: [{ type: 'line', data: [120, 200, 150] }],
}
</script>

<template>
  <v-chart class="chart" :option="option" autoresize />
</template>

<style scoped>
.chart { height: 400px; }
</style>
```

## 目录结构

```
vue-echarts-developer/
├── SKILL.md              # 核心工作流与配置指南
├── README.md             # 说明文档
├── evals/
│   └── evals.json        # 测试用例
└── references/           # 各图表类型的完整代码示例
    ├── LineChart.md
    ├── BarChart.md
    ├── PieChart.md
    └── ...
```

## 常见坑

- **容器尺寸为 0**：必须给 `<v-chart>` 父容器明确 height
- **tooltip 不显示**：检查是否注册了 `TooltipComponent`
- **大数据量卡顿**：启用 `sampling`、关闭 `animation`
- **响应式不生效**：使用 `autoresize` 属性
- **体积过大**：按需引入可减少约 60%
