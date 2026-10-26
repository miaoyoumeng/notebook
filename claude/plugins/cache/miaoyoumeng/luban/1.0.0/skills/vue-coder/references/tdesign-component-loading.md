# TDesign Loading 加载

加载组件用于展示加载状态。

## Props

| 属性名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| loading | boolean | true | 是否加载中 |
| text | string | - | 加载文本 |
| size | string | medium | 尺寸：`small` / `medium` / `large` |
| fullscreen | boolean | false | 是否全屏 |
| indicator | VNode | - | 自定义加载指示器 |
| preventScrollThrough | boolean | false | 是否阻止滚动 |
| showOverlay | boolean | true | 是否显示遮罩 |

## Slots

| 插槽名 | 说明 |
|--------|------|
| default | 被包裹的内容 |
| indicator | 自定义指示器 |

## 示例

```vue
<template>
  <Loading :loading="isLoading" text="加载中...">
    <div>被加载的内容</div>
  </Loading>
</template>
<script setup lang="ts" name="LoadingDemo">
import { Loading } from 'tdesign-vue-next';
import { ref } from 'vue';

const isLoading = ref(true);
</script>
<style scoped>
</style>
```
