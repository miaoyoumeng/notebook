# TDesign Breadcrumb 面包屑

面包屑组件用于展示当前页面在层次结构中的位置，并提供快速返回上级页面的导航路径。

## Props

### Breadcrumb Props

| 属性名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| max-item-width | number | - | 单项最大宽度（px），超出省略 |
| options | BreadcrumbItem[] | [] | 面包屑选项列表 |
| separator | string / RenderFunction | '/' | 分隔符 |
| theme | string | default | 主题：`default` / `light` |

### BreadcrumbItem Props

| 属性名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| content | string | - | 面包屑内容 |
| disabled | boolean | false | 是否禁用点击 |
| href | string | - | 链接地址 |
| icon | RenderFunction | - | 自定义图标 |
| max-width | string/number | - | 单项最大宽度 |
| replace | boolean | false | 是否使用 replace 路由跳转 |
| router | boolean | false | 是否使用 vue-router |
| to | string / object | - | 路由目标 |

## Events

| 事件名 | 参数 | 说明 |
|--------|------|------|
| change | `(index: number, item: BreadcrumbItem) => void` | 面包屑项点击时触发 |

## Slots

| 插槽名 | 说明 |
|--------|------|
| default | BreadcrumbItem 列表 |
| separator | 自定义分隔符 |

## 示例

```vue
<template>
  <Space direction="vertical" :size="24">
    <!-- 基础用法 -->
    <Breadcrumb>
      <BreadcrumbItem>首页</BreadcrumbItem>
      <BreadcrumbItem>列表页</BreadcrumbItem>
      <BreadcrumbItem>详情页</BreadcrumbItem>
    </Breadcrumb>

    <!-- 带路由跳转 -->
    <Breadcrumb>
      <BreadcrumbItem :to="{ name: 'home' }" :router="true">首页</BreadcrumbItem>
      <BreadcrumbItem :to="{ name: 'list' }" :router="true">列表页</BreadcrumbItem>
      <BreadcrumbItem :disabled="true">当前页</BreadcrumbItem>
    </Breadcrumb>

    <!-- 自定义分隔符 -->
    <Breadcrumb separator=">">
      <BreadcrumbItem>首页</BreadcrumbItem>
      <BreadcrumbItem>分类</BreadcrumbItem>
      <BreadcrumbItem>子分类</BreadcrumbItem>
    </Breadcrumb>

    <!-- 带图标 -->
    <Breadcrumb>
      <BreadcrumbItem><Icon name="home" />首页</BreadcrumbItem>
      <BreadcrumbItem>列表页</BreadcrumbItem>
      <BreadcrumbItem>详情</BreadcrumbItem>
    </Breadcrumb>

    <!-- 下拉菜单模式 -->
    <Breadcrumb :max-item-width="100">
      <BreadcrumbItem>首页</BreadcrumbItem>
      <BreadcrumbItem>超长列表页名称超长列表页名称超长</BreadcrumbItem>
      <BreadcrumbItem>详情页</BreadcrumbItem>
    </Breadcrumb>
  </Space>
</template>
<script setup lang="ts" name="BreadcrumbDemo">
import { Breadcrumb, BreadcrumbItem, Icon, Space } from 'tdesign-vue-next';
</script>
<style scoped>
</style>
```
