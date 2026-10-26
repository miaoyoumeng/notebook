# TDesign Icon 图标

图标组件，支持自定义颜色、尺寸和旋转动画。

## Props

| 属性名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| size | string/number | undefined | 图标尺寸 |
| color | string | undefined | 图标颜色 |
| loading | boolean | false | 是否显示旋转动画 |

## Events

| 事件名 | 参数 | 说明 |
|--------|------|------|
| click | `(e: MouseEvent) => void` | 点击事件 |

## Slots

| 插槽名 | 说明 |
|--------|------|
| default | 自定义图标内容 |

## 示例

```vue
<template>
  <Space>
    <Icon name="add" />
    <Icon name="close" size="24px" color="#ff0000" />
    <Icon name="loading" :loading="true" />
    <Icon @click="handleClick"><CheckIcon /></Icon>
  </Space>
</template>
<script setup lang="ts" name="IconDemo">
import { Icon, Space } from 'tdesign-vue-next';
import { CheckIcon } from 'tdesign-icons-vue-next';

const handleClick = () => {
  console.log('图标点击');
};
</script>
<style scoped>
</style>
```
