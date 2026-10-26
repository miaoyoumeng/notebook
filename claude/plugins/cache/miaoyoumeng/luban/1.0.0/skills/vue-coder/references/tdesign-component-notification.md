# TDesign Notification 消息通知

消息通知用于展示系统通知和重要信息。

## Props (Command API)

通过 `NotificationPlugin` 调用：

```ts
import { NotificationPlugin } from 'tdesign-vue-next';

NotificationPlugin.info({ title: '通知标题', content: '通知内容' });
```

| 配置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| title | string | - | 标题 |
| content | string | - | 内容 |
| theme | string | info | 主题：`info` / `success` / `warning` / `error` |
| duration | number | 3000 | 显示时长(ms) |
| placement | string | top-right | 位置 |
| closeBtn | boolean | true | 是否显示关闭按钮 |

## 示例

```vue
<template>
  <Space>
    <Button @click="showInfo">信息通知</Button>
    <Button @click="showSuccess">成功通知</Button>
    <Button @click="showWarning">警告通知</Button>
  </Space>
</template>
<script setup lang="ts" name="NotificationDemo">
import { NotificationPlugin, Button, Space } from 'tdesign-vue-next';

const showInfo = () => NotificationPlugin.info({ title: '通知', content: '这是一条通知' });
const showSuccess = () => NotificationPlugin.success({ title: '成功', content: '操作已完成' });
const showWarning = () => NotificationPlugin.warning({ title: '警告', content: '请注意' });
</script>
<style scoped>
</style>
```
