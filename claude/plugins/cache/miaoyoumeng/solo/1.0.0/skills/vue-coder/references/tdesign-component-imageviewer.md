# TDesign ImageViewer 图片预览

图片预览组件支持放大、旋转、切换。

## Props

| 属性名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| visible | boolean | false | 是否显示 |
| images | array | - | 图片列表 |
| index | number | 0 | 当前预览索引 |

## Events

| 事件名 | 参数 | 说明 |
|--------|------|------|
| visible-change | `(visible: boolean) => void` | 显隐变化 |
| index-change | `(index: number) => void` | 索引变化 |

## Slots

| 插槽名 | 说明 |
|--------|------|
| trigger | 触发器 |

## 示例

```vue
<template>
  <div>
    <ImageViewer :images="images" :index="currentIndex">
      <template #trigger>
        <Image v-for="img in images" :key="img" :src="img" style="width: 100px; margin: 4px" />
      </template>
    </ImageViewer>
  </div>
</template>
<script setup lang="ts" name="ImageViewerDemo">
import { ImageViewer, Image } from 'tdesign-vue-next';
import { ref } from 'vue';

const images = ref([
  'https://example.com/img1.png',
  'https://example.com/img2.png',
  'https://example.com/img3.png',
]);
const currentIndex = ref(0);
</script>
<style scoped>
</style>
```
