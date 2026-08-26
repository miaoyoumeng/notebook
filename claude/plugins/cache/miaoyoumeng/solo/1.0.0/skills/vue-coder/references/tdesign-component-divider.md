# TDesign Divider 分割线

分割线用于区隔内容区域。

## Props

| 属性名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| layout | string | horizontal | 布局方向：`horizontal` / `vertical` |
| dashed | boolean | false | 是否虚线 |
| align | string | center | 文本对齐：`left` / `right` / `center` |

## Slots

| 插槽名 | 说明 |
|--------|------|
| default | 分割线文本（仅水平分割线） |

## 示例

```vue
<template>
  <div>
    <p>上方内容</p>
    <Divider />
    <Divider dashed>虚线分割</Divider>
    <Divider align="left">居左标题</Divider>
    <Divider layout="vertical" />
    <p>下方内容</p>
  </div>
</template>
<script setup lang="ts" name="DividerDemo">
import { Divider } from 'tdesign-vue-next';
</script>
<style scoped>
</style>
```
