# TDesign Layout 布局

Layout 布局组件提供 Header/Sider/Content/Footer 结构。

## Props

| 属性名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| direction | string | vertical | 布局方向：`vertical` / `horizontal` |

## 组件

| 组件名 | 说明 |
|--------|------|
| Layout | 布局容器 |
| LayoutHeader | 头部区域 |
| LayoutSider | 侧边栏区域 |
| LayoutContent | 内容区域 |
| LayoutFooter | 底部区域 |

## 示例

```vue
<template>
  <Layout>
    <LayoutHeader>Header</LayoutHeader>
    <Layout direction="horizontal">
      <LayoutSider>
        <Menu :options="menuOptions" />
      </LayoutSider>
      <LayoutContent>Content</LayoutContent>
    </Layout>
    <LayoutFooter>Footer</LayoutFooter>
  </Layout>
</template>
<script setup lang="ts" name="LayoutDemo">
import { Layout, Menu } from 'tdesign-vue-next';
import { ref } from 'vue';

const menuOptions = ref([]);
</script>
<style scoped>
</style>
```
