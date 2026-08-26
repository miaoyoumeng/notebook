# TDesign Input 输入框

输入框组件用于接收用户输入。

## Props

| 属性名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| value/v-model | string | - | 输入值 |
| placeholder | string | - | 占位符 |
| disabled | boolean | false | 是否禁用 |
| readonly | boolean | false | 是否只读 |
| clearable | boolean | false | 是否显示清空按钮 |
| maxlength | number | - | 最大输入长度 |
| prefix | string/VNode | - | 前缀内容 |
| suffix | string/VNode | - | 后缀内容 |
| size | string | medium | 尺寸：`small` / `medium` / `large` |
| showLimitNumber | boolean | false | 是否显示字数限制 |
| type | string | text | 类型：`text` / `password` / `url` / `email` 等 |

## Events

| 事件名 | 参数 | 说明 |
|--------|------|------|
| change | `(value: string) => void` | 值变化 |
| blur | `(value: string, e: FocusEvent) => void` | 失去焦点 |
| focus | `(value: string, e: FocusEvent) => void` | 获得焦点 |
| clear | `() => void` | 点击清空 |
| enter | `(value: string, e: KeyboardEvent) => void` | 回车键 |

## Slots

| 插槽名 | 说明 |
|--------|------|
| prefix | 前缀内容 |
| suffix | 后缀内容 |
| prefixIcon | 前缀图标 |
| suffixIcon | 后缀图标 |

## 示例

```vue
<template>
  <Space>
    <Input v-model="value" placeholder="请输入内容" />
    <Input v-model="password" type="password" placeholder="密码" clearable />
    <Input v-model="text" maxlength="20" :show-limit-number="true" prefix="¥" />
    <Input v-model="searchText" clearable @enter="handleSearch">
      <template #suffixIcon><Icon name="search" @click="handleSearch" /></template>
    </Input>
    <Input disabled placeholder="禁用状态" />
  </Space>
</template>
<script setup lang="ts" name="InputDemo">
import { Input, Space, Icon } from 'tdesign-vue-next';
import { ref } from 'vue';

const value = ref('');
const password = ref('');
const text = ref('');
const searchText = ref('');

const handleSearch = () => {
  console.log('搜索:', searchText.value);
};
</script>
<style scoped>
</style>
```
