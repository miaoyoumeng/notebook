# TDesign TimePicker 时间选择器

时间选择器用于选择具体时间。

## Props

| 属性名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| value/v-model | string | - | 选中值 |
| format | string | HH:mm:ss | 时间格式 |
| disabled | boolean | false | 是否禁用 |
| clearable | boolean | true | 是否可清空 |
| placeholder | string | 请选择时间 | 占位符 |
| steps | array | - | 步长：[时, 分, 秒] |
| disableTime | function | - | 禁用时间函数 |
| size | string | medium | 尺寸 |

## Events

| 事件名 | 参数 | 说明 |
|--------|------|------|
| change | `(value: string) => void` | 值变化 |
| blur | `(context: { e: FocusEvent }) => void` | 失去焦点 |

## 示例

```vue
<template>
  <Space>
    <TimePicker v-model="time1" />
    <TimePicker v-model="time2" format="HH:mm" />
    <TimePicker v-model="time3" :steps="[1, 10, 0]" />
    <TimePicker v-model="time4" disabled />
  </Space>
</template>
<script setup lang="ts" name="TimePickerDemo">
import { TimePicker, Space } from 'tdesign-vue-next';
import { ref } from 'vue';

const time1 = ref('');
const time2 = ref('');
const time3 = ref('');
const time4 = ref('');
</script>
<style scoped>
</style>
```
