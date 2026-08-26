# TDesign Select 选择器

下拉选择器组件，支持单选/多选和远程搜索。

## Props

| 属性名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| value/v-model | string/number/array | - | 选中值 |
| options | array | - | 选项列表 |
| placeholder | string | 请选择 | 占位符 |
| disabled | boolean | false | 是否禁用 |
| multiple | boolean | false | 是否多选 |
| clearable | boolean | false | 是否可清空 |
| filterable | boolean | false | 是否可搜索 |
| size | string | medium | 尺寸：`small` / `medium` / `large` |
| max | number | 0 | 多选时最大选中数 |

## Events

| 事件名 | 参数 | 说明 |
|--------|------|------|
| change | `(value: any, context: SelectChangeContext) => void` | 值变化 |
| blur | `(context: { e: FocusEvent }) => void` | 失去焦点 |
| focus | `(context: { e: FocusEvent }) => void` | 获得焦点 |
| search | `(filterText: string, context: SelectSearchContext) => void` | 搜索 |

## Slots

| 插槽名 | 说明 |
|--------|------|
| default | 自定义选项内容 |
| prefixIcon | 前缀图标 |
| empty | 空状态内容 |

## 示例

```vue
<template>
  <Space>
    <Select v-model="value1" :options="options" placeholder="请选择" />
    <Select v-model="value2" :options="options" multiple clearable placeholder="多选" />
    <Select v-model="value3" :options="options" filterable placeholder="可搜索" />
    <Select v-model="value4" :options="options" filterable @search="handleSearch" placeholder="远程搜索" />
    <Select v-model="value5" :options="options" disabled />
  </Space>
</template>
<script setup lang="ts" name="SelectDemo">
import { Select, Space } from 'tdesign-vue-next';
import { ref } from 'vue';

const options = [
  { label: '选项1', value: 1 },
  { label: '选项2', value: 2 },
  { label: '选项3', value: 3 },
];

const value1 = ref(1);
const value2 = ref([1]);
const value3 = ref('');
const value4 = ref('');
const value5 = ref('');

const handleSearch = (keyword: string) => {
  console.log('搜索:', keyword);
};
</script>
<style scoped>
</style>
```
