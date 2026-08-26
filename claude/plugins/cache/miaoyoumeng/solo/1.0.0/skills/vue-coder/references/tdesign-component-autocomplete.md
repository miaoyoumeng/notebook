# TDesign AutoComplete 自动补全

输入时提供自动补全建议。

## Props

| 属性名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| value/v-model | string | - | 输入值 |
| options | array | - | 补全选项列表 |
| placeholder | string | - | 占位符 |
| disabled | boolean | false | 是否禁用 |
| highlightKeyword | boolean | true | 是否高亮匹配关键词 |

## Events

| 事件名 | 参数 | 说明 |
|--------|------|------|
| change | `(value: string) => void` | 值变化 |
| select | `(value: string, context: AutoCompleteSelectContext) => void` | 选择补全 |

## Slots

| 插槽名 | 说明 |
|--------|------|
| default | 自定义补全选项 |
| suffix | 后缀内容 |

## 示例

```vue
<template>
  <Space>
    <AutoComplete v-model="value1" :options="options" placeholder="输入关键词" />
    <AutoComplete v-model="value2" :options="remoteOptions" placeholder="远程补全" />
  </Space>
</template>
<script setup lang="ts" name="AutoCompleteDemo">
import { AutoComplete, Space } from 'tdesign-vue-next';
import { ref } from 'vue';

const value1 = ref('');
const value2 = ref('');
const options = ref(['Vue', 'React', 'Angular', 'Svelte']);
const remoteOptions = ref([]);
</script>
<style scoped>
</style>
```
