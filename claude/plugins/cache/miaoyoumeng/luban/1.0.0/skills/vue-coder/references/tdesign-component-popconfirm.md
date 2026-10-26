# TDesign Popconfirm 气泡确认框

气泡确认框用于轻量级操作确认。

## Props

| 属性名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| content | string | - | 确认内容 |
| confirmBtn | string/object | - | 确认按钮 |
| cancelBtn | string/object | - | 取消按钮 |
| theme | string | warning | 主题 |
| placement | string | top | 位置 |
| showArrow | boolean | true | 是否显示箭头 |
| trigger | string | click | 触发方式：`click` / `hover` / `focus` |

## Events

| 事件名 | 参数 | 说明 |
|--------|------|------|
| confirm | `(context: { e: MouseEvent }) => void` | 确认 |
| cancel | `(context: { e: MouseEvent }) => void` | 取消 |
| visible-change | `(visible: boolean, context: PopupVisibleContext) => void` | 显隐变化 |

## Slots

| 插槽名 | 说明 |
|--------|------|
| default | 触发元素 |
| content | 确认内容 |

## 示例

```vue
<template>
  <Popconfirm content="确定删除吗？" @confirm="handleConfirm">
    <Button theme="danger">删除</Button>
  </Popconfirm>
</template>
<script setup lang="ts" name="PopconfirmDemo">
import { Popconfirm, Button } from 'tdesign-vue-next';

const handleConfirm = () => {
  console.log('已确认删除');
};
</script>
<style scoped>
</style>
```
