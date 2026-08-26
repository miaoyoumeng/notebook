# TDesign Rate 评分

评分组件用于打分评价。

## Props

| 属性名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| value/v-model | number | 0 | 评分值 |
| count | number | 5 | 评分总数 |
| size | string/number | medium | 尺寸 |
| disabled | boolean | false | 是否禁用 |
| allowHalf | boolean | false | 是否允许半星 |
| allowClear | boolean | true | 是否允许清除 |
| showText | boolean | false | 是否显示辅助文字 |
| texts | array | - | 辅助文字数组 |

## Events

| 事件名 | 参数 | 说明 |
|--------|------|------|
| change | `(value: number) => void` | 值变化 |

## 示例

```vue
<template>
  <Space>
    <Rate v-model="rate1" />
    <Rate v-model="rate2" allow-half />
    <Rate v-model="rate3" :show-text="true" :texts="['很差','差','一般','好','很好']" />
    <Rate v-model="rate4" disabled />
  </Space>
</template>
<script setup lang="ts" name="RateDemo">
import { Rate, Space } from 'tdesign-vue-next';
import { ref } from 'vue';

const rate1 = ref(4);
const rate2 = ref(3.5);
const rate3 = ref(4);
const rate4 = ref(3);
</script>
<style scoped>
</style>
```
