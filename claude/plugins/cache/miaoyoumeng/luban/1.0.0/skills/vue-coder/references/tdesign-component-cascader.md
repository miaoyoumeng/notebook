# TDesign Cascader 级联选择器

级联选择器用于多级联动选择。

## Props

| 属性名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| value/v-model | string/number/array | - | 选中值 |
| options | array | - | 选项列表 |
| placeholder | string | 请选择 | 占位符 |
| disabled | boolean | false | 是否禁用 |
| clearable | boolean | false | 是否可清空 |
| filterable | boolean | false | 是否可搜索 |
| multiple | boolean | false | 是否多选 |
| checkStrictly | boolean | false | 父子节点不关联 |
| size | string | medium | 尺寸：`small` / `medium` / `large` |

## Events

| 事件名 | 参数 | 说明 |
|--------|------|------|
| change | `(value: any, context: CascaderChangeContext) => void` | 值变化 |

## 示例

```vue
<template>
  <Space>
    <Cascader v-model="value1" :options="options" placeholder="请选择地区" />
    <Cascader v-model="value2" :options="options" filterable placeholder="可搜索" />
    <Cascader v-model="value3" :options="options" multiple placeholder="多选" />
    <Cascader v-model="value4" :options="options" :check-strictly="true" placeholder="任意级别" />
  </Space>
</template>
<script setup lang="ts" name="CascaderDemo">
import { Cascader, Space } from 'tdesign-vue-next';
import { ref } from 'vue';

const options = [
  {
    label: '广东',
    value: 'guangdong',
    children: [
      { label: '广州', value: 'guangzhou' },
      { label: '深圳', value: 'shenzhen' },
    ],
  },
  {
    label: '浙江',
    value: 'zhejiang',
    children: [
      { label: '杭州', value: 'hangzhou' },
      { label: '宁波', value: 'ningbo' },
    ],
  },
];

const value1 = ref('');
const value2 = ref('');
const value3 = ref([]);
const value4 = ref('');
</script>
<style scoped>
</style>
```
