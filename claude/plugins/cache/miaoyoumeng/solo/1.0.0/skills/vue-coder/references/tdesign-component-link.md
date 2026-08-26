# TDesign Link 链接

文本超链接组件，支持多种主题和状态。

## Props

| 属性名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| theme | string | default | 主题：`default` / `primary` / `danger` / `warning` / `success` |
| size | string | medium | 尺寸：`small` / `medium` / `large` |
| disabled | boolean | false | 是否禁用 |
| hover | string | underline | 悬停效果：`underline` / `color` / `none` |
| download | boolean/string | false | 是否下载或下载文件名 |
| href | string | - | 链接地址 |
| target | string | _self | 跳转目标 |

## Events

| 事件名 | 参数 | 说明 |
|--------|------|------|
| click | `(e: MouseEvent) => void` | 点击事件 |

## Slots

| 插槽名 | 说明 |
|--------|------|
| default | 链接内容 |
| prefixIcon | 前缀图标 |
| suffixIcon | 后缀图标 |

## 示例

```vue
<template>
  <Space>
    <Link href="https://example.com" target="_blank">默认链接</Link>
    <Link theme="primary">主要链接</Link>
    <Link disabled>禁用链接</Link>
    <Link hover="color">悬停变色</Link>
    <Link><template #prefixIcon><Icon name="link" /></template>带图标链接</Link>
  </Space>
</template>
<script setup lang="ts" name="LinkDemo">
import { Link, Icon, Space } from 'tdesign-vue-next';
</script>
<style scoped>
</style>
```
