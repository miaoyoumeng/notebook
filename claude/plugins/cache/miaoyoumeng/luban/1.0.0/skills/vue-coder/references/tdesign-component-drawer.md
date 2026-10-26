# TDesign Drawer 抽屉

抽屉是从屏幕边缘滑出的面板。

## Props

| 属性名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| visible | boolean | false | 是否显示 |
| header | string | - | 标题 |
| body | string/VNode | - | 内容 |
| placement | string | right | 位置：`left` / `right` / `top` / `bottom` |
| size | string/number | small | 尺寸 |
| closeOnEscKeydown | boolean | true | ESC 可关闭 |
| closeOnOverlayClick | boolean | true | 蒙层可关闭 |
| destroyOnClose | boolean | false | 关闭销毁内容 |
| showOverlay | boolean | true | 是否显示遮罩 |

## Events

| 事件名 | 参数 | 说明 |
|--------|------|------|
| visible-change | `(visible: boolean, context: DrawerCloseContext) => void` | 显隐变化 |
| close | `(context: DrawerCloseContext) => void` | 关闭 |

## Slots

| 插槽名 | 说明 |
|--------|------|
| default | 抽屉内容 |
| header | 标题 |
| footer | 底部 |

## 示例

```vue
<template>
  <div>
    <Button @click="visible = true">打开抽屉</Button>
    <Drawer v-model:visible="visible" header="抽屉标题" size="large">
      <p>抽屉内容</p>
    </Drawer>
  </div>
</template>
<script setup lang="ts" name="DrawerDemo">
import { Drawer, Button } from 'tdesign-vue-next';
import { ref } from 'vue';

const visible = ref(false);
</script>
<style scoped>
</style>
```
