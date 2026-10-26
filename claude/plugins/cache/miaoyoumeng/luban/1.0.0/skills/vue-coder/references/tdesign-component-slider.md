# TDesign Slider 滑块

滑块组件用于数值范围选择。

## Props

| 属性名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| value/v-model | number/array | 0 | 选中值 |
| min | number | 0 | 最小值 |
| max | number | 100 | 最大值 |
| step | number | 1 | 步长 |
| disabled | boolean | false | 是否禁用 |
| range | boolean | false | 是否范围选择 |
| showExtremeValue | boolean | false | 是否显示最大值最小值 |
| vertical | boolean | false | 是否垂直方向 |
| marks | object | - | 刻度标记 |

## Events

| 事件名 | 参数 | 说明 |
|--------|------|------|
| change | `(value: number/array) => void` | 值变化 |
| changeEnd | `(value: number/array) => void` | 拖拽结束 |

## 示例

```vue
<template>
  <Space>
    <Slider v-model="value1" :max="100" />
    <Slider v-model="value2" range :max="100" />
    <Slider v-model="value3" :marks="marks" :max="50" />
    <Slider v-model="value4" disabled />
    <Slider v-model="value5" :step="10" show-extreme-value />
  </Space>
</template>
<script setup lang="ts" name="SliderDemo">
import { Slider, Space } from 'tdesign-vue-next';
import { ref } from 'vue';

const value1 = ref(30);
const value2 = ref([20, 80]);
const value3 = ref(25);
const value4 = ref(50);
const value5 = ref(0);
const marks = { 0: '0%', 25: '25%', 50: '50%', 75: '75%', 100: '100%' };
</script>
<style scoped>
</style>
```
