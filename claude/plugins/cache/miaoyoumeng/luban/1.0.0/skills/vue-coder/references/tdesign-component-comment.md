# TDesign Comment 评论

评论组件用于展示评论或反馈内容。

## Props

| 属性名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| author | string | - | 作者 |
| avatar | string | - | 头像地址 |
| content | string | - | 评论内容 |
| datetime | string | - | 时间 |
| quote | boolean | false | 是否引用样式 |
| reply | boolean | false | 是否回复状态 |
| actions | array | - | 操作项 |

## Slots

| 插槽名 | 说明 |
|--------|------|
| default | 评论内容 |
| author | 作者 |
| avatar | 头像 |
| datetime | 时间 |
| actions | 操作区 |
| reply | 回复区域 |

## 示例

```vue
<template>
  <Comment
    author="用户名"
    datetime="2026-08-10"
    content="这是一条评论"
  >
    <template #avatar>
      <Avatar>U</Avatar>
    </template>
    <template #actions>
      <Button theme="primary" variant="text">回复</Button>
    </template>
  </Comment>
</template>
<script setup lang="ts" name="CommentDemo">
import { Comment, Avatar, Button } from 'tdesign-vue-next';
</script>
<style scoped>
</style>
```
