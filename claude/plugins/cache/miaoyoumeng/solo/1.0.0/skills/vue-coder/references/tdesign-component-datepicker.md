# TDesign DatePicker 日期选择器

日期选择器用于日期/日期范围选择。

## Props

| 属性名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| value/v-model | string/array | - | 选中值 |
| mode | string | date | 模式：`year` / `quarter` / `month` / `week` / `date` |
| range | boolean | false | 是否范围选择 |
| disabled | boolean | false | 是否禁用 |
| clearable | boolean | true | 是否可清空 |
| format | string | YYYY-MM-DD | 格式 |
| placeholder | string/array | - | 占位符 |
| firstDayOfWeek | number | 1 | 周起始日 |
| disableDate | function | - | 禁用日期函数 |

## Events

| 事件名 | 参数 | 说明 |
|--------|------|------|
| change | `(value: string, context: DatePickerChangeContext) => void` | 值变化 |
| confirm | `(value: string, context: DatePickerChangeContext) => void` | 确认 |
| blur | `(context: { e: FocusEvent }) => void` | 失去焦点 |

## Slots

| 插槽名 | 说明 |
|--------|------|
| prefixIcon | 前缀图标 |
| suffixIcon | 后缀图标 |

## 示例

```vue
<template>
  <Space>
    <DatePicker v-model="date1" />
    <DatePicker v-model="date2" :range="true" />
    <DatePicker v-model="month" mode="month" />
    <DatePicker v-model="datetime" :disable-date="disableDate" />
  </Space>
</template>
<script setup lang="ts" name="DatePickerDemo">
import { DatePicker, Space } from 'tdesign-vue-next';
import { ref } from 'vue';

const date1 = ref('');
const date2 = ref([]);
const month = ref('');
const datetime = ref('');

const disableDate = (date: Date) => {
  return date.getTime() > Date.now();
};
</script>
<style scoped>
</style>
```
