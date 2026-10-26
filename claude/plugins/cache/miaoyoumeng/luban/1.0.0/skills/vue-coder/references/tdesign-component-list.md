# TDesign List 列表

列表组件用于展示数据集合。

## Props

| 属性名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| split | boolean | true | 是否显示分割线 |
| header | string | - | 列表头部 |
| footer | string | - | 列表尾部 |
| loading | boolean | false | 是否加载中 |
| layout | string | horizontal | 布局：`horizontal` / `vertical` |
| size | string | medium | 尺寸：`small` / `medium` / `large` |
| striped | boolean | false | 是否斑马纹 |
| asyncLoading | string | none | 异步加载状态 |

## Slots

| 插槽名 | 说明 |
|--------|------|
| default | 列表项内容 |
| header | 自定义头部 |
| footer | 自定义尾部 |
| scroll | 滚动区域内容 |

## 示例

```vue
<template>
  <List header="列表标题" footer="列表尾部">
    <ListItem v-for="item in list" :key="item.id">
      <ListItemMeta :image="item.avatar" :title="item.title" :description="item.desc" />
    </ListItem>
  </List>
</template>
<script setup lang="ts" name="ListDemo">
import { List, ListItem, ListItemMeta } from 'tdesign-vue-next';
import { ref } from 'vue';

const list = ref([
  { id: 1, avatar: '', title: '列表项1', desc: '描述1' },
  { id: 2, avatar: '', title: '列表项2', desc: '描述2' },
  { id: 3, avatar: '', title: '列表项3', desc: '描述3' },
]);
</script>
<style scoped>
</style>
```
