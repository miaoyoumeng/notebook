# TDesign Transfer 穿梭框

穿梭框用于在两个面板间移动选项。

## Props

| 属性名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| value/v-model | array | - | 右侧数据值 |
| data | array | - | 数据源 |
| disabled | boolean | false | 是否禁用 |
| titles | array | - | 标题数组 |
| directions | array | - | 方向按钮文本 |
| empty | array | - | 空状态文本 |
| checked | array | - | 选中项 |

## Events

| 事件名 | 参数 | 说明 |
|--------|------|------|
| change | `(value: TransferValue[], context: TransferChangeContext) => void` | 值变化 |
| checked-change | `(options: TransferCheckedChangeContext) => void` | 选中变化 |

## Slots

| 插槽名 | 说明 |
|--------|------|
| default | 自定义列表项 |

## 示例

```vue
<template>
  <Transfer v-model="targetValues" :data="sourceData" />
</template>
<script setup lang="ts" name="TransferDemo">
import { Transfer } from 'tdesign-vue-next';
import { ref } from 'vue';

const sourceData = ref([
  { label: '选项1', value: 1 },
  { label: '选项2', value: 2 },
  { label: '选项3', value: 3 },
]);
const targetValues = ref([]);
</script>
<style scoped>
</style>
```
