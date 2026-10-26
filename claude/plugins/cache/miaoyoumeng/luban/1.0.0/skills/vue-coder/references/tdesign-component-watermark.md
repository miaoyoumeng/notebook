# TDesign Watermark 水印

水印用于在页面上叠加文字或图片标记。

## Props

| 属性名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| alpha | number | 1 | 透明度 |
| content | string | - | 水印文本 |
| width | number | - | 宽度 |
| height | number | - | 高度 |
| rotate | number | -22 | 旋转角度 |
| x | number | - | X 偏移 |
| y | number | - | Y 偏移 |

## 示例

```vue
<template>
  <Watermark :content="'内部机密'">
    <div style="height: 300px">被水印覆盖的内容</div>
  </Watermark>
</template>
<script setup lang="ts" name="WatermarkDemo">
import { Watermark } from 'tdesign-vue-next';
</script>
<style scoped>
</style>
```
