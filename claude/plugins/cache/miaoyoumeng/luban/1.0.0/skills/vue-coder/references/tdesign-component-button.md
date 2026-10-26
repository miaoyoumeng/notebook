# TDesign Button 按钮

按钮用于触发操作，支持多种类型、尺寸和状态。

## Props

| 属性名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| theme | string | default | 类型：`default` / `primary` / `danger` / `warning` / `success` |
| size | string | medium | 尺寸：`small` / `medium` / `large` |
| variant | string | base | 变体：`base` / `outline` / `dashed` / `text` |
| shape | string | rectangle | 形状：`rectangle` / `square` / `round` / `circle` |
| disabled | boolean | false | 是否禁用 |
| loading | boolean | false | 是否加载中 |
| block | boolean | false | 是否块级按钮 |

## Events

| 事件名 | 参数 | 说明 |
|--------|------|------|
| click | `(e: MouseEvent) => void` | 点击事件 |

## Slots

| 插槽名 | 说明 |
|--------|------|
| default | 按钮内容 |
| icon | 图标 |

## 示例

```vue
<template>
  <Space>
    <TButton theme="primary" @click="handleClick">主要按钮</TButton>
    <TButton>默认按钮</TButton>
    <TButton variant="outline" theme="primary">描边按钮</TButton>
    <TButton variant="text">文本按钮</TButton>
    <TButton loading>加载中</TButton>
    <TButton disabled>禁用</TButton>
  </Space>
</template>
<script setup lang="ts" name="ButtonDemo">
import { Button as TButton, Space } from 'tdesign-vue-next';

const handleClick = () => {
  console.log('按钮被点击');
};
</script>
<style scoped>
</style>
```
