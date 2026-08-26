# TDesign SelectInput 筛选器输入框

带下拉面板的输入框，可作为 Select 的基础组件。

## Props

| 属性名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| value/v-model | string | - | 输入值 |
| disabled | boolean | false | 是否禁用 |
| clearable | boolean | false | 是否可清空 |
| placeholder | string | - | 占位符 |
| popupProps | object | - | 弹窗配置 |
| panel | VNode | - | 自定义下拉面板 |

## Events

| 事件名 | 参数 | 说明 |
|--------|------|------|
| change | `(value: string, context: SelectInputChangeContext) => void` | 值变化 |
| popupVisibleChange | `(visible: boolean) => void` | 弹窗显隐 |

## Slots

| 插槽名 | 说明 |
|--------|------|
| default | 自定义输入内容 |
| panel | 下拉面板 |
| prefixIcon | 前缀图标 |

## 示例

```vue
<template>
  <Space>
    <SelectInput v-model="value1" placeholder="基础输入" />
    <SelectInput v-model="value2" :popup-props="{ visible: showPanel }">
      <template #panel>
        <div style="padding: 16px">自定义面板</div>
      </template>
    </SelectInput>
    <SelectInput v-model="value3" clearable placeholder="可清除" />
  </Space>
</template>
<script setup lang="ts" name="SelectInputDemo">
import { SelectInput, Space } from 'tdesign-vue-next';
import { ref } from 'vue';

const value1 = ref('');
const value2 = ref('');
const value3 = ref('');
const showPanel = ref(false);
</script>
<style scoped>
</style>
```
