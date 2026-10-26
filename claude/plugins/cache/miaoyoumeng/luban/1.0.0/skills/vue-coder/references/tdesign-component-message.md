# TDesign Message 全局提示

全局提示用于轻量级操作反馈。

## Props (Command API)

通过 `MessagePlugin` 调用：

```ts
import { MessagePlugin } from 'tdesign-vue-next';

MessagePlugin.info('信息提示');
MessagePlugin.success('操作成功');
MessagePlugin.warning('警告提示');
MessagePlugin.error('操作失败');
```

| 配置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| content | string | - | 内容 |
| duration | number | 3000 | 显示时长(ms) |
| offset | array | - | 偏移：[x, y] |
| zIndex | number | 5000 | 层级 |
| closeAll | boolean | false | 关闭全部 |

## 示例

```vue
<template>
  <Space>
    <Button @click="showInfo">信息</Button>
    <Button @click="showSuccess">成功</Button>
    <Button @click="showWarning">警告</Button>
    <Button @click="showError">错误</Button>
    <Button @click="closeAll">关闭全部</Button>
  </Space>
</template>
<script setup lang="ts" name="MessageDemo">
import { MessagePlugin, Button, Space } from 'tdesign-vue-next';

const showInfo = () => MessagePlugin.info('这是一条信息');
const showSuccess = () => MessagePlugin.success('操作成功');
const showWarning = () => MessagePlugin.warning('需要注意');
const showError = () => MessagePlugin.error('操作失败');
const closeAll = () => MessagePlugin.closeAll();
</script>
<style scoped>
</style>
```
