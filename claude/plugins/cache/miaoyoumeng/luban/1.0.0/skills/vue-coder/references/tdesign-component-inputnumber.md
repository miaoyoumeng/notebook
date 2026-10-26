# TDesign InputNumber 数字输入框

数字输入框组件，支持增减按钮和数值校验。

## Props

| 属性名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| value/v-model | number | - | 当前值 |
| min | number | -Infinity | 最小值 |
| max | number | Infinity | 最大值 |
| step | number | 1 | 步长 |
| decimalPlaces | number | 0 | 小数位数 |
| disabled | boolean | false | 是否禁用 |
| size | string | medium | 尺寸：`small` / `medium` / `large` |
| theme | string | normal | 主题：`normal` / `column` / `row` |

## Events

| 事件名 | 参数 | 说明 |
|--------|------|------|
| change | `(value: number) => void` | 值变化 |
| blur | `(value: number, e: FocusEvent) => void` | 失去焦点 |
| focus | `(value: number, e: FocusEvent) => void` | 获得焦点 |

## 示例

```vue
<template>
  <Space>
    <InputNumber v-model="count" :min="0" :max="100" :step="1" />
    <InputNumber v-model="price" :decimal-places="2" :min="0" prefix="¥" />
    <InputNumber v-model="quantity" theme="column" :min="0" />
    <InputNumber disabled :model-value="0" />
  </Space>
</template>
<script setup lang="ts" name="InputNumberDemo">
import { InputNumber, Space } from 'tdesign-vue-next';
import { ref } from 'vue';

const count = ref(0);
const price = ref(0);
const quantity = ref(1);
</script>
<style scoped>
</style>
```
