# TDesign Grid 栅格

栅格系统提供 Row/Col 布局组件，基于 24 列栅格。

## Row Props

| 属性名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| gutter | number/array | 0 | 栅格间距 |
| justify | string | start | 对齐方式：`start` / `end` / `center` / `space-around` / `space-between` |
| align | string | top | 垂直对齐：`top` / `middle` / `bottom` |

## Col Props

| 属性名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| span | number | - | 栅格占位格数 |
| offset | number | 0 | 栅格左侧间隔格数 |
| order | number | 0 | 栅格排序顺序 |
| xs/sm/md/lg/xl | number/object | - | 响应式栅格 |

## 示例

```vue
<template>
  <Row :gutter="16">
    <Col :span="8">左列 (8/24)</Col>
    <Col :span="12">中列 (12/24)</Col>
    <Col :span="4">右列 (4/24)</Col>
  </Row>
  <Row justify="center">
    <Col :span="12">居中内容</Col>
  </Row>
  <Row :gutter="[16, 16]">
    <Col :xs="24" :md="12" :lg="8">响应式列</Col>
    <Col :xs="24" :md="12" :lg="8">响应式列</Col>
    <Col :xs="24" :md="12" :lg="8">响应式列</Col>
  </Row>
</template>
<script setup lang="ts" name="GridDemo">
import { Row, Col } from 'tdesign-vue-next';
</script>
<style scoped>
</style>
```
