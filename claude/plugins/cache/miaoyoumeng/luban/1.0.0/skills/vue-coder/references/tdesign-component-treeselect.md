# TDesign TreeSelect 树选择器

树形结构下拉选择器。

## Props

| 属性名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| value/v-model | string/number/array | - | 选中值 |
| data | array | - | 树数据 |
| placeholder | string | 请选择 | 占位符 |
| disabled | boolean | false | 是否禁用 |
| clearable | boolean | false | 是否可清空 |
| filterable | boolean | false | 是否可搜索 |
| multiple | boolean | false | 是否多选 |
| checkStrictly | boolean | false | 父子不关联 |
| size | string | medium | 尺寸 |

## Events

| 事件名 | 参数 | 说明 |
|--------|------|------|
| change | `(value: any, context: TreeSelectChangeContext) => void` | 值变化 |

## 示例

```vue
<template>
  <Space>
    <TreeSelect v-model="value1" :data="treeData" placeholder="选择节点" />
    <TreeSelect v-model="value2" :data="treeData" filterable placeholder="可搜索" />
    <TreeSelect v-model="value3" :data="treeData" multiple placeholder="多选" />
  </Space>
</template>
<script setup lang="ts" name="TreeSelectDemo">
import { TreeSelect, Space } from 'tdesign-vue-next';
import { ref } from 'vue';

const treeData = [
  { label: '根节点', value: 0, children: [
    { label: '子节点1', value: 1 },
    { label: '子节点2', value: 2 },
  ]},
];

const value1 = ref('');
const value2 = ref('');
const value3 = ref([]);
</script>
<style scoped>
</style>
```
