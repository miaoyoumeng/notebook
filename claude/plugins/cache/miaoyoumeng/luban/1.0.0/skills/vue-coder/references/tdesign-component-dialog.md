# TDesign Dialog 对话框

对话框用于模态交互，支持确认、表单、自定义内容。

## Props

| 属性名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| visible | boolean | false | 是否显示 |
| header | string | - | 标题 |
| body | string/VNode | - | 内容 |
| footer | boolean/VNode | true | 底部内容 |
| width | string/number | - | 宽度 |
| mode | string | modeless | 模式：`modal` / `modeless` |
| closeOnEscKeydown | boolean | true | ESC 可关闭 |
| closeOnOverlayClick | boolean | true | 蒙层可关闭 |
| destroyOnClose | boolean | false | 关闭销毁内容 |
| confirmBtn | string/object | - | 确认按钮 |
| cancelBtn | string/object | - | 取消按钮 |

## Events

| 事件名 | 参数 | 说明 |
|--------|------|------|
| visible-change | `(visible: boolean, context: DialogCloseContext) => void` | 显隐变化 |
| confirm | `(context: DialogConfirmContext) => void` | 确认 |
| cancel | `(context: DialogCancelContext) => void` | 取消 |

## Slots

| 插槽名 | 说明 |
|--------|------|
| default | 对话框内容 |
| header | 标题 |
| footer | 底部 |

## 示例

```vue
<template>
  <div>
    <Button @click="visible = true">打开对话框</Button>
    <Dialog v-model:visible="visible" header="对话框标题" :on-confirm="handleConfirm">
      <p>对话框内容</p>
    </Dialog>
  </div>
</template>
<script setup lang="ts" name="DialogDemo">
import { Dialog, Button } from 'tdesign-vue-next';
import { ref } from 'vue';

const visible = ref(false);
const handleConfirm = () => {
  console.log('确认');
  visible.value = false;
};
</script>
<style scoped>
</style>
```
