# TDesign InputAdornment 输入装饰器

为输入框添加前后缀装饰。

## Props

| 属性名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| placement | string | - | 位置：`prefix` / `suffix` / `both` |
| text | string | - | 装饰文本 |

## Slots

| 插槽名 | 说明 |
|--------|------|
| default | 被装饰的输入组件 |
| prefix | 前缀内容 |
| suffix | 后缀内容 |

## 示例

```vue
<template>
  <Space>
    <InputAdornment text="¥">
      <Input placeholder="金额" />
    </InputAdornment>
    <InputAdornment text=".com">
      <Input placeholder="域名" />
    </InputAdornment>
    <InputAdornment>
      <template #prefix><Icon name="search" /></template>
      <Input placeholder="搜索" />
    </InputAdornment>
  </Space>
</template>
<script setup lang="ts" name="InputAdornmentDemo">
import { InputAdornment, Input, Icon, Space } from 'tdesign-vue-next';
</script>
<style scoped>
</style>
```
