# TDesign Empty 空状态

空状态用于无数据或无内容时展示。

## Props

| 属性名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| action | VNode | - | 操作区 |
| description | string | - | 描述文本 |
| image | string | - | 自定义图片 |

## Slots

| 插槽名 | 说明 |
|--------|------|
| default | 操作区内容 |
| action | 操作区 |
| description | 描述文本 |

## 示例

```vue
<template>
  <Empty description="暂无数据">
    <template #action>
      <Button theme="primary" @click="handleRefresh">刷新</Button>
    </template>
  </Empty>
</template>
<script setup lang="ts" name="EmptyDemo">
import { Empty, Button } from 'tdesign-vue-next';

const handleRefresh = () => {
  console.log('刷新');
};
</script>
<style scoped>
</style>
```
