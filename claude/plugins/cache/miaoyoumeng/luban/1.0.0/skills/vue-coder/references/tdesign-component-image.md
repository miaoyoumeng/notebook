# TDesign Image 图片

图片组件支持懒加载和错误处理。

## Props

| 属性名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| src | string | - | 图片地址 |
| alt | string | - | 替代文本 |
| fit | string | fill | 填充方式：`fill` / `contain` / `cover` / `none` / `scale-down` |
| lazy | boolean | false | 是否懒加载 |
| loading | VNode | - | 加载态内容 |
| error | VNode | - | 错误态内容 |
| shape | string | square | 形状：`square` / `circle` / `round` |

## Events

| 事件名 | 参数 | 说明 |
|--------|------|------|
| load | `(e: Event) => void` | 加载成功 |
| error | `(e: Event) => void` | 加载失败 |

## 示例

```vue
<template>
  <Space>
    <Image src="https://example.com/img.png" alt="示例图片" />
    <Image src="https://example.com/img.png" fit="cover" :lazy="true" />
    <Image shape="circle" src="https://example.com/avatar.png" />
    <Image src="invalid-url">
      <template #error><Empty description="加载失败" /></template>
    </Image>
  </Space>
</template>
<script setup lang="ts" name="ImageDemo">
import { Image, Space, Empty } from 'tdesign-vue-next';
</script>
<style scoped>
</style>
```
