# TDesign Radio 单选框

单选框组件，支持分组和按钮样式。

## Props

| 属性名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| value/v-model | string/number/boolean | - | 选中值 |
| label | string | - | 标签文本 |
| disabled | boolean | false | 是否禁用 |
| name | string | - | 原生 name 属性 |
| allowUncheck | boolean | false | 是否允许取消选中 |

## Events

| 事件名 | 参数 | 说明 |
|--------|------|------|
| change | `(checked: boolean, context: RadioChangeEvent) => void` | 状态变化 |

## Slots

| 插槽名 | 说明 |
|--------|------|
| default | 自定义内容 |

## 示例

```vue
<template>
  <Space>
    <Radio v-model="radio1" :value="true">单个选项</Radio>
    <RadioGroup v-model="radio2" :options="options" />
    <RadioGroup v-model="radio3" type="button">
      <Radio :value="1">选项A</Radio>
      <Radio :value="2">选项B</Radio>
      <Radio :value="3">选项C</Radio>
    </RadioGroup>
    <Radio disabled>禁用选项</Radio>
  </Space>
</template>
<script setup lang="ts" name="RadioDemo">
import { Radio, RadioGroup, Space } from 'tdesign-vue-next';
import { ref } from 'vue';

const radio1 = ref(false);
const radio2 = ref(1);
const radio3 = ref(1);
const options = [
  { label: '选项A', value: 1 },
  { label: '选项B', value: 2 },
];
</script>
<style scoped>
</style>
```
