# TDesign RangeInput 范围输入框

范围输入框用于输入数值范围。

## Props

| 属性名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| value/v-model | array | - | 范围值：[start, end] |
| disabled | boolean | false | 是否禁用 |
| separator | string | - | 分隔符 |
| placeholder | array | - | 占位符：[start, end] |
| size | string | medium | 尺寸 |

## Events

| 事件名 | 参数 | 说明 |
|--------|------|------|
| change | `(value: RangeInputValue) => void` | 值变化 |

## Slots

| 插槽名 | 说明 |
|--------|------|
| separator | 自定义分隔符 |

## 示例

```vue
<template>
  <Space>
    <RangeInput v-model="range1" />
    <RangeInput v-model="range2" separator="~" />
    <RangeInput v-model="range3" disabled />
  </Space>
</template>
<script setup lang="ts" name="RangeInputDemo">
import { RangeInput, Space } from 'tdesign-vue-next';
import { ref } from 'vue';

const range1 = ref(['', '']);
const range2 = ref(['10', '100']);
const range3 = ref(['', '']);
</script>
<style scoped>
</style>
```
