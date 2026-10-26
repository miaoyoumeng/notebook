# TDesign Statistic 统计数值

统计数值组件用于展示关键指标。

## Props

| 属性名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| value | number | 0 | 数值 |
| title | string | - | 标题 |
| prefix | VNode | - | 前缀图标 |
| suffix | VNode | - | 后缀 |
| extra | VNode | - | 额外内容 |
| loading | boolean | false | 是否加载中 |
| trend | string | - | 趋势：`increase` / `decrease` |

## 示例

```vue
<template>
  <Space>
    <Statistic title="用户数" :value="123456" />
    <Statistic title="转化率" :value="85" suffix="%" />
    <Statistic title="收入" :value="9999" prefix="¥" trend="increase" />
    <Statistic title="订单" :value="0" loading />
  </Space>
</template>
<script setup lang="ts" name="StatisticDemo">
import { Statistic, Space } from 'tdesign-vue-next';
</script>
<style scoped>
</style>
```
