# TDesign Calendar 日历

日历组件用于展示日期和日程。

## Props

| 属性名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| value/v-model | string | - | 当前日期 |
| mode | string | month | 模式：`month` / `range` |
| firstDayOfWeek | number | 1 | 周起始 |
| isShowWeekend | boolean | true | 是否显示周末 |
| minDate | string | - | 最小日期 |
| maxDate | string | - | 最大日期 |

## Events

| 事件名 | 参数 | 说明 |
|--------|------|------|
| change | `(value: string) => void` | 日期变化 |
| cellClick | `(context: CalendarCellContext) => void` | 单元格点击 |

## Slots

| 插槽名 | 说明 |
|--------|------|
| default | 单元格内容 |
| headCell | 头部单元格 |

## 示例

```vue
<template>
  <div>
    <Calendar v-model="currentDate" />
    <Calendar v-model="currentDate" :first-day-of-week="7" />
  </div>
</template>
<script setup lang="ts" name="CalendarDemo">
import { Calendar } from 'tdesign-vue-next';
import { ref } from 'vue';

const currentDate = ref('2026-08-10');
</script>
<style scoped>
</style>
```
