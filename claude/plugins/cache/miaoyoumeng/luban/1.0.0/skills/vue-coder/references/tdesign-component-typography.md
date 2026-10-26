# TDesign Typography 排版

排版组件用于统一文本样式，支持标题、段落、引用等。

## Props

| 属性名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| tag | string | span | HTML 标签：`h1`~`h6` / `p` / `span` / `div` |
| theme | string | default | 主题：`default` / `secondary` / `success` / `danger` / `warning` |
| variant | string | none | 变体：`none` / `h1`~`h6` / `body` / `small` / `mark` / `code` / `del` |
| ellipsis | boolean/object | false | 省略配置：`{ row?: number, suffix?: string }` |
| copyable | boolean/object | false | 可复制配置 |

## Events

| 事件名 | 参数 | 说明 |
|--------|------|------|
| copy | `(text: string, e: ClipboardEvent) => void` | 复制成功 |
| error | `(text: string, e: ClipboardEvent) => void` | 复制失败 |

## Slots

| 插槽名 | 说明 |
|--------|------|
| default | 文本内容 |
| suffix | 省略后缀 |

## 示例

```vue
<template>
  <div>
    <Typography variant="h1">一级标题</Typography>
    <Typography variant="h2">二级标题</Typography>
    <Typography theme="secondary">次要文本</Typography>
    <Typography ellipsis :row="2">{{ longText }}</Typography>
    <Typography copyable>可复制文本</Typography>
  </div>
</template>
<script setup lang="ts" name="TypographyDemo">
import { Typography } from 'tdesign-vue-next';
import { ref } from 'vue';

const longText = ref('这是一段很长的文本，用于演示省略号效果。'.repeat(10));
</script>
<style scoped>
</style>
```
