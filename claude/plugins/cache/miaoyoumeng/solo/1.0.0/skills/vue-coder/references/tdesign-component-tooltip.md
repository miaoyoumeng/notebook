# TDesign Tooltip 文字提示

文字提示用于鼠标悬停时展示说明文字。

## Props

| 属性名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| content | string | - | 提示内容 |
| placement | string | top | 位置 |
| showArrow | boolean | true | 是否显示箭头 |
| theme | string | default | 主题：`default` / `success` / `warning` / `danger` |

## Slots

| 插槽名 | 说明 |
|--------|------|
| default | 触发元素 |
| content | 提示内容 |

## 示例

```vue
<template>
  <Space>
    <Tooltip content="这是一个提示">
      <Button>悬停查看提示</Button>
    </Tooltip>
    <Tooltip content="底部提示" placement="bottom">
      <Button>底部弹出</Button>
    </Tooltip>
  </Space>
</template>
<script setup lang="ts" name="TooltipDemo">
import { Tooltip, Button, Space } from 'tdesign-vue-next';
</script>
<style scoped>
</style>
```
