# TDesign QRCode 二维码

二维码生成组件。

## Props

| 属性名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| content | string | - | 二维码内容 |
| color | string | #000000 | 前景色 |
| backgroundColor | string | #ffffff | 背景色 |
| size | number | 160 | 尺寸 |
| nodeSize | number | 4 | 节点大小 |

## 示例

```vue
<template>
  <QRCode content="https://example.com" :size="200" />
</template>
<script setup lang="ts" name="QRCodeDemo">
import { QRCode } from 'tdesign-vue-next';
</script>
<style scoped>
</style>
```
