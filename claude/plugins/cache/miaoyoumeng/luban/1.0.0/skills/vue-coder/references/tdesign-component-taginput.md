# TDesign TagInput 标签输入框

标签输入组件，支持回车创建标签。

## Props

| 属性名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| value/v-model | array | - | 标签值列表 |
| disabled | boolean | false | 是否禁用 |
| clearable | boolean | false | 是否可清空 |
| maxLabelRow | number | 5 | 最大标签行数 |
| autoWidth | boolean | false | 是否自动宽度 |
| placeholder | string | - | 占位符 |
| minCollapsedNum | number | 0 | 最小折叠显示数 |

## Events

| 事件名 | 参数 | 说明 |
|--------|------|------|
| change | `(value: TagInputValue) => void` | 值变化 |
| add | `(context: TagInputAddContext) => void` | 添加标签 |
| remove | `(context: TagInputRemoveContext) => void` | 移除标签 |

## Slots

| 插槽名 | 说明 |
|--------|------|
| default | 自定义标签内容 |
| prefix | 前缀内容 |
| suffix | 后缀内容 |

## 示例

```vue
<template>
  <Space>
    <TagInput v-model="tags1" placeholder="输入标签后回车" />
    <TagInput v-model="tags2" :auto-width="true" placeholder="可清除" clearable />
    <TagInput v-model="tags3" :disabled="true" />
  </Space>
</template>
<script setup lang="ts" name="TagInputDemo">
import { TagInput, Space } from 'tdesign-vue-next';
import { ref } from 'vue';

const tags1 = ref(['Vue', 'React']);
const tags2 = ref(['Tag1', 'Tag2', 'Tag3']);
const tags3 = ref(['只读标签']);
</script>
<style scoped>
</style>
```
