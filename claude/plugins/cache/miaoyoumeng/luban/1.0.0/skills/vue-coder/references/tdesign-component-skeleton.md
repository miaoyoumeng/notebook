# TDesign Skeleton 骨架屏

骨架屏用于在内容加载前展示占位。

## Props

| 属性名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| loading | boolean | true | 是否显示骨架 |
| animation | string | gradient | 动画：`gradient` / `flashed` / `none` |
| theme | string | paragraph | 主题：`paragraph` / `avatar` / `text` 等 |
| count | number | 1 | 骨架块数量 |
| rowCol | array | - | 自定义骨架布局 |

## Slots

| 插槽名 | 说明 |
|--------|------|
| default | 实际内容 |
| loading | 自定义骨架内容 |

## 示例

```vue
<template>
  <Skeleton :loading="loading" theme="paragraph">
    <div>实际内容</div>
  </Skeleton>
</template>
<script setup lang="ts" name="SkeletonDemo">
import { Skeleton } from 'tdesign-vue-next';
import { ref } from 'vue';

const loading = ref(true);
</script>
<style scoped>
</style>
```
