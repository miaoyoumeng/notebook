# TDesign Descriptions 描述

描述列表用于展示信息键值对。

## Props

| 属性名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| data | array | - | 描述数据数组 |
| column | number | 2 | 每行列数 |
| bordered | boolean | false | 是否显示边框 |
| size | string | medium | 尺寸：`small` / `medium` / `large` |
| layout | string | horizontal | 布局：`horizontal` / `vertical` |

## Slots

| 插槽名 | 说明 |
|--------|------|
| default | 自定义描述项 |
| label | 标签内容 |
| content | 内容 |

## 示例

```vue
<template>
  <Descriptions title="基本信息" :column="2" bordered>
    <DescriptionsItem label="姓名">张三</DescriptionsItem>
    <DescriptionsItem label="年龄">28</DescriptionsItem>
    <DescriptionsItem label="手机号">138****0000</DescriptionsItem>
    <DescriptionsItem label="邮箱">test@example.com</DescriptionsItem>
  </Descriptions>
</template>
<script setup lang="ts" name="DescriptionsDemo">
import { Descriptions, DescriptionsItem } from 'tdesign-vue-next';
</script>
<style scoped>
</style>
```
