# TDesign Avatar 头像

头像组件用于展示用户头像、图标或文字，支持多种尺寸、形状和分组展示。

## Props

| 属性名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| size | string/number | medium | 尺寸：`small` / `medium` / `large` 或具体数值 |
| shape | string | circle | 形状：`circle` / `round` |
| alt | string | - | 图片加载失败时的替代文本 |
| hideOnLoadFailed | boolean | false | 加载失败是否隐藏 |
| src | string | - | 图片地址 |
| icon | RenderFunction | - | 自定义图标渲染函数 |

## Events

| 事件名 | 参数 | 说明 |
|--------|------|------|
| error | `(e: Event) => void` | 图片加载失败时触发 |

## Slots

| 插槽名 | 说明 |
|--------|------|
| default | 头像内容（图标/文字） |
| icon | 自定义图标 |

## AvatarGroup Props

| 属性名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| max | number | - | 最大显示数量 |
| cascading | string | 'right-up' | 重叠方向：`left-up` / `right-up` |
| size | string/number | medium | 统一尺寸 |

## 示例

```vue
<template>
  <Space direction="vertical" :size="16">
    <!-- 基础用法 -->
    <Space>
      <Avatar>U</Avatar>
      <Avatar src="https://tdesign.gtimg.com/site/avatar.jpg" alt="用户头像" />
      <Avatar><Icon name="user" /></Avatar>
    </Space>

    <!-- 不同尺寸 -->
    <Space>
      <Avatar size="small">小</Avatar>
      <Avatar size="medium">中</Avatar>
      <Avatar size="large">大</Avatar>
      <Avatar :size="64">64px</Avatar>
    </Space>

    <!-- 不同形状 -->
    <Space>
      <Avatar shape="circle">圆形</Avatar>
      <Avatar shape="round">圆角</Avatar>
    </Space>

    <!-- 图片加载失败 -->
    <Avatar
      src="invalid-url.jpg"
      alt="加载失败"
      :hideOnLoadFailed="false"
      @error="handleError"
    >
      失败
    </Avatar>

    <!-- 头像分组 -->
    <AvatarGroup max="3" cascading="right-up">
      <Avatar>A</Avatar>
      <Avatar>B</Avatar>
      <Avatar>C</Avatar>
      <Avatar>D</Avatar>
      <Avatar>E</Avatar>
    </AvatarGroup>
  </Space>
</template>
<script setup lang="ts" name="AvatarDemo">
import { Avatar, AvatarGroup, Icon, Space } from 'tdesign-vue-next';

const handleError = (e: Event) => {
  console.log('头像加载失败', e);
};
</script>
<style scoped>
</style>
```
