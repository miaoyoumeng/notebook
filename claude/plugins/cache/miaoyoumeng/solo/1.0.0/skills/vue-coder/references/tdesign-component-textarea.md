# TDesign Textarea 多行文本框

多行文本输入组件。

## Props

| 属性名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| value/v-model | string | - | 文本值 |
| placeholder | string | - | 占位符 |
| disabled | boolean | false | 是否禁用 |
| readonly | boolean | false | 是否只读 |
| maxlength | number | - | 最大字符数 |
| autosize | boolean/object | false | 自适应高度 |
| showLimitNumber | boolean | false | 显示字数限制 |
| indicator | VNode | - | 自定义字数提示 |
| tips | string | - | 底部提示文本 |
| label | string | - | 标签文本 |

## Events

| 事件名 | 参数 | 说明 |
|--------|------|------|
| change | `(value: string) => void` | 值变化 |
| blur | `(value: string, e: FocusEvent) => void` | 失去焦点 |
| focus | `(value: string, e: FocusEvent) => void` | 获得焦点 |
| compositionend | `(value: string, e: CompositionEvent) => void` | 输入法输入完成 |

## 示例

```vue
<template>
  <Space>
    <Textarea v-model="content" placeholder="请输入多行文本" />
    <Textarea v-model="desc" :maxlength="200" :show-limit-number="true" :autosize="{ minRows: 3, maxRows: 6 }" />
    <Textarea v-model="fixed" :rows="4" placeholder="固定4行" />
    <Textarea v-model="tips" tips="请输入详细描述" placeholder="带提示文本" />
  </Space>
</template>
<script setup lang="ts" name="TextareaDemo">
import { Textarea, Space } from 'tdesign-vue-next';
import { ref } from 'vue';

const content = ref('');
const desc = ref('');
const fixed = ref('');
const tips = ref('');
</script>
<style scoped>
</style>
```
