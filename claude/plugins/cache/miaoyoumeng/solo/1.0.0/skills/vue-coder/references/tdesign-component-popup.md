# TDesign Popup 弹出层

弹出层是其他弹出组件的基础组件。

## Props

| 属性名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| visible | boolean | false | 是否显示 |
| content | string/VNode | - | 内容 |
| placement | string | top | 位置 |
| trigger | string | hover | 触发方式：`hover` / `click` / `focus` / `context-menu` |
| showArrow | boolean | true | 是否显示箭头 |
| overlayStyle | object | - | 遮罩样式 |
| zIndex | number | 1600 | 层级 |
| destroyOnClose | boolean | false | 关闭销毁内容 |

## Events

| 事件名 | 参数 | 说明 |
|--------|------|------|
| visible-change | `(visible: boolean, context: PopupVisibleContext) => void` | 显隐变化 |

## Slots

| 插槽名 | 说明 |
|--------|------|
| default | 触发元素 |
| content | 弹出内容 |

## 示例

```vue
<template>
  <Popup content="弹出内容" placement="bottom">
    <Button>触发弹出</Button>
  </Popup>
</template>
<script setup lang="ts" name="PopupDemo">
import { Popup, Button } from 'tdesign-vue-next';
</script>
<style scoped>
</style>
```
