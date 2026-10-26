# TDesign Checkbox 多选框

多选框组件，支持分组和全选。

## Props

| 属性名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| value/v-model | boolean/array | - | 选中状态 |
| label | string | - | 标签文本 |
| disabled | boolean | false | 是否禁用 |
| indeterminate | boolean | false | 半选状态 |
| checkAll | boolean | false | 是否全选（CheckboxGroup 中） |
| readonly | boolean | false | 是否只读 |

## Events

| 事件名 | 参数 | 说明 |
|--------|------|------|
| change | `(checked: boolean, context: CheckboxChangeEvent) => void` | 状态变化 |

## Slots

| 插槽名 | 说明 |
|--------|------|
| default | 自定义内容 |

## 示例

```vue
<template>
  <Space>
    <Checkbox v-model="checked">单个选项</Checkbox>
    <Checkbox disabled>禁用选项</Checkbox>
    <CheckboxGroup v-model="groupValue" :options="options" />
    <Checkbox :indeterminate="isIndeterminate" :check-all="isCheckAll" @change="handleToggleAll">
      全选/反选
    </Checkbox>
  </Space>
</template>
<script setup lang="ts" name="CheckboxDemo">
import { Checkbox, CheckboxGroup, Space } from 'tdesign-vue-next';
import { ref, computed } from 'vue';

const checked = ref(false);
const groupValue = ref([1]);
const options = [
  { label: '选项A', value: 1 },
  { label: '选项B', value: 2 },
  { label: '选项C', value: 3 },
];
const isCheckAll = computed(() => groupValue.value.length === options.length);
const isIndeterminate = computed(() => groupValue.value.length > 0 && groupValue.value.length < options.length);

const handleToggleAll = (val: boolean) => {
  groupValue.value = val ? options.map(o => o.value) : [];
};
</script>
<style scoped>
</style>
```
