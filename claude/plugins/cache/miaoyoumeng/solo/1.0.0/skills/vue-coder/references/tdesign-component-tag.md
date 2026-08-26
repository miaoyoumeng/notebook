# TDesign Tag 标签

标签用于标记分类或状态。

## Props

| 属性名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| theme | string | default | 主题：`default` / `primary` / `danger` / `warning` / `success` |
| size | string | medium | 尺寸：`small` / `medium` / `large` |
| closable | boolean | false | 是否可关闭 |
| disabled | boolean | false | 是否禁用 |
| maxWidth | number/string | - | 最大宽度 |
| shape | string | rectangle | 形状：`rectangle` / `round` / `mark` / `circle` |

## Events

| 事件名 | 参数 | 说明 |
|--------|------|------|
| close | `(e: MouseEvent) => void` | 关闭 |
| click | `(e: MouseEvent) => void` | 点击 |

## Slots

| 插槽名 | 说明 |
|--------|------|
| default | 标签内容 |
| icon | 图标 |

## 示例

```vue
<template>
  <Space>
    <Tag>默认标签</Tag>
    <Tag theme="primary">主要标签</Tag>
    <Tag theme="success">成功</Tag>
    <Tag theme="warning">警告</Tag>
    <Tag theme="danger" closable>可关闭</Tag>
    <Tag shape="round">圆角标签</Tag>
    <Tag disabled>禁用状态</Tag>
  </Space>
</template>
<script setup lang="ts" name="TagDemo">
import { Tag, Space } from 'tdesign-vue-next';
</script>
<style scoped>
</style>
```
