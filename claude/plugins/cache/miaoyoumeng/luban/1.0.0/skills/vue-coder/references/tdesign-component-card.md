# TDesign Card 卡片

卡片容器用于展示相关内容和操作。

## Props

| 属性名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| title | string | - | 标题 |
| description | string | - | 描述 |
| bordered | boolean | true | 是否显示边框 |
| hoverShadow | boolean | false | 是否悬停显示阴影 |
| loading | boolean | false | 是否加载中 |
| headerBordered | boolean | false | 是否显示头部边框 |
| subtitle | string | - | 副标题 |

## Slots

| 插槽名 | 说明 |
|--------|------|
| default | 卡片内容 |
| title | 标题（自定义） |
| description | 描述（自定义） |
| footer | 底部内容 |
| actions | 操作区域 |

## 示例

```vue
<template>
  <Space>
    <Card title="卡片标题" description="卡片描述">
      <p>卡片内容</p>
      <template #footer>
        <Button theme="primary">操作</Button>
      </template>
    </Card>
    <Card :bordered="false" :hover-shadow="true">
      <p>无边框卡片</p>
    </Card>
    <Card loading>
      <p>加载中的卡片</p>
    </Card>
  </Space>
</template>
<script setup lang="ts" name="CardDemo">
import { Card, Button, Space } from 'tdesign-vue-next';
</script>
<style scoped>
</style>
```
