# TDesign Timeline 时间轴

时间轴用于展示事件发展脉络。

## Props

| 属性名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| mode | string | alternate | 标签位置：`alternate` / `left` / `right` / `same` |
| pending | boolean | false | 是否存在幽灵节点 |
| reverse | boolean | false | 是否反向排列 |

## Slots

| 插槽名 | 说明 |
|--------|------|
| default | 时间轴节点（TimelineItem） |
| pending | 幽灵节点内容 |

## 示例

```vue
<template>
  <Timeline>
    <TimelineItem label="2026-08-10">事件1</TimelineItem>
    <TimelineItem label="2026-08-11">事件2</TimelineItem>
    <TimelineItem label="2026-08-12">事件3</TimelineItem>
  </Timeline>
</template>
<script setup lang="ts" name="TimelineDemo">
import { Timeline, TimelineItem } from 'tdesign-vue-next';
</script>
<style scoped>
</style>
```
