# TDesign Tree 树形控件

树形控件用于展示层级数据。

## Props

| 属性名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| data | array | - | 树数据 |
| activable | boolean | false | 是否可激活 |
| checkable | boolean | false | 是否可勾选 |
| expandAll | boolean | false | 是否展开所有 |
| hover | boolean | false | 是否高亮悬停 |
| checkStrictly | boolean | false | 父子不关联 |
| filter | function | - | 过滤函数 |

## Events

| 事件名 | 参数 | 说明 |
|--------|------|------|
| expand | `(context: TreeNodeExpandContext) => void` | 展开变化 |
| click | `(context: TreeNodeContext) => void` | 节点点击 |
| check | `(context: TreeCheckContext) => void` | 勾选变化 |

## Slots

| 插槽名 | 说明 |
|--------|------|
| default | 自定义节点内容 |

## 示例

```vue
<template>
  <Tree :data="treeData" :expand-all="true" :checkable="true" />
</template>
<script setup lang="ts" name="TreeDemo">
import { Tree } from 'tdesign-vue-next';

const treeData = [
  { label: '根节点', value: 0, children: [
    { label: '子节点1', value: 1, children: [
      { label: '孙节点1', value: 11 },
    ]},
    { label: '子节点2', value: 2 },
  ]},
];
</script>
<style scoped>
</style>
```
