# TDesign Collapse 折叠面板

折叠面板用于分组展示内容，支持展开/收起。

## Props

| 属性名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| value/v-model | string/number/array | - | 展开面板值 |
| bordered | boolean | true | 是否显示边框 |
| expandIconPlacement | string | right | 图标位置：`left` / `right` |
| disabled | boolean | false | 是否禁用 |

## Events

| 事件名 | 参数 | 说明 |
|--------|------|------|
| change | `(value: CollapseValue) => void` | 展开变化 |

## Slots

| 插槽名 | 说明 |
|--------|------|
| default | 折叠面板项 |
| panel | 面板头部（CollapsePanel） |
| content | 面板内容（CollapsePanel） |

## 示例

```vue
<template>
  <Collapse v-model="activeNames">
    <CollapsePanel :header="'面板1'" :value="1">
      <p>面板1内容</p>
    </CollapsePanel>
    <CollapsePanel :header="'面板2'" :value="2">
      <p>面板2内容</p>
    </CollapsePanel>
    <CollapsePanel :header="'面板3'" :value="3" :disabled="true">
      <p>禁用面板</p>
    </CollapsePanel>
  </Collapse>
</template>
<script setup lang="ts" name="CollapseDemo">
import { Collapse, CollapsePanel } from 'tdesign-vue-next';
import { ref } from 'vue';

const activeNames = ref([1]);
</script>
<style scoped>
</style>
```
