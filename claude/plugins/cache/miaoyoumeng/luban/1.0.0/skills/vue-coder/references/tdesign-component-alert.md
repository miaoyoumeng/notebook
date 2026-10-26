# TDesign Alert 警告提醒

警告提醒用于展示不同等级的提示信息。

## Props

| 属性名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| theme | string | info | 主题：`info` / `success` / `warning` / `error` |
| title | string | - | 标题 |
| message | string | - | 内容 |
| closable | boolean | false | 是否可关闭 |
| closeAll | boolean | false | 关闭全部可见 |
| maxLine | number | 5 | 最大行数 |
| icon | VNode/boolean | - | 自定义图标 |
| operation | VNode | - | 操作区 |

## Events

| 事件名 | 参数 | 说明 |
|--------|------|------|
| close | `(e: MouseEvent) => void` | 关闭 |

## Slots

| 插槽名 | 说明 |
|--------|------|
| default | 内容 |
| title | 标题 |
| icon | 图标 |
| operation | 操作区 |

## 示例

```vue
<template>
  <Space>
    <Alert title="信息" message="这是一条信息提醒" theme="info" />
    <Alert title="成功" message="操作成功" theme="success" />
    <Alert title="警告" message="需要注意" theme="warning" closable />
    <Alert title="错误" message="操作失败" theme="error" closable />
  </Space>
</template>
<script setup lang="ts" name="AlertDemo">
import { Alert, Space } from 'tdesign-vue-next';
</script>
<style scoped>
</style>
```
