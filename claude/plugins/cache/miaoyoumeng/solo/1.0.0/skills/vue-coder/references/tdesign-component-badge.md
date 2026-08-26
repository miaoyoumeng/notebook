# TDesign Badge 徽标

徽标用于显示未读消息数或状态提示。

## Props

| 属性名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| count | number | 0 | 徽标数量 |
| dot | boolean | false | 是否点状徽标 |
| maxCount | number | 99 | 最大值（超过显示 N+） |
| offset | array | - | 偏移：[x, y] |
| size | string | medium | 尺寸：`small` / `medium` |

## Slots

| 插槽名 | 说明 |
|--------|------|
| default | 触发徽标的内容 |

## 示例

```vue
<template>
  <Space>
    <Badge :count="5">
      <Button>消息</Button>
    </Badge>
    <Badge :count="100" :max-count="99">
      <Button>通知</Button>
    </Badge>
    <Badge dot>
      <Icon name="bell" />
    </Badge>
    <Badge :count="3" :offset="[5, -5]">
      <Avatar>U</Avatar>
    </Badge>
  </Space>
</template>
<script setup lang="ts" name="BadgeDemo">
import { Badge, Button, Icon, Avatar, Space } from 'tdesign-vue-next';
</script>
<style scoped>
</style>
```
