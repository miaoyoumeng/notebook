# TDesign Space 间距

Space 组件用于设置组件之间的间距。

## Props

| 属性名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| direction | string | horizontal | 方向：`horizontal` / `vertical` |
| size | number/string/array | medium | 间距：`small`/`medium`/`large` 或具体数值 |
| align | string | center | 对齐：`start` / `end` / `center` / `baseline` |
| breakLine | boolean | false | 是否自动换行 |
| separator | VNode | - | 分隔符 |

## 示例

```vue
<template>
  <Space>
    <Button>按钮1</Button>
    <Button>按钮2</Button>
    <Button>按钮3</Button>
  </Space>
  <Space direction="vertical">
    <Button block>垂直按钮1</Button>
    <Button block>垂直按钮2</Button>
  </Space>
  <Space :size="24">
    <Button>间距24px</Button>
    <Button>间距24px</Button>
  </Space>
  <Space break-line>
    <Tag v-for="i in 10" :key="i">标签{{ i }}</Tag>
  </Space>
</template>
<script setup lang="ts" name="SpaceDemo">
import { Space, Button, Tag } from 'tdesign-vue-next';
</script>
<style scoped>
</style>
```
