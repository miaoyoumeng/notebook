# TDesign Form 表单

表单组件用于数据收集和校验。

## Props

| 属性名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| data/v-model | object | - | 表单数据对象 |
| rules | object | - | 校验规则 |
| colon | boolean | false | 标签是否显示冒号 |
| disabled | boolean | false | 是否禁用所有表单元素 |
| layout | string | vertical | 布局：`vertical` / `horizontal` / `inline` |
| labelAlign | string | right | 标签对齐：`left` / `right` |
| labelWidth | number/string | - | 标签宽度 |
| requiredMark | string | - | 必填标记类型：`required` / `optional` |
| resetType | string | initial | 重置方式：`initial` / `clear` |
| showErrorMessage | boolean | true | 是否显示错误信息 |

## Events

| 事件名 | 参数 | 说明 |
|--------|------|------|
| submit | `(context: { validateResult: boolean }) => void` | 提交 |
| reset | `(context: { validateResult: boolean }) => void` | 重置 |
| validate | `(context: ValidateContext) => void` | 校验结果 |

## Slots

| 插槽名 | 说明 |
|--------|------|
| default | 表单项内容 |
| reset | 重置按钮 |
| submit | 提交按钮 |

## 示例

```vue
<template>
  <Form :data="formData" :rules="rules" @submit="onSubmit">
    <FormItem label="用户名" name="name">
      <Input v-model="formData.name" placeholder="请输入用户名" />
    </FormItem>
    <FormItem label="邮箱" name="email">
      <Input v-model="formData.email" placeholder="请输入邮箱" />
    </FormItem>
    <FormItem label="密码" name="password">
      <Input v-model="formData.password" type="password" placeholder="请输入密码" />
    </FormItem>
    <FormItem>
      <Button theme="primary" type="submit">提交</Button>
      <Button type="reset" style="margin-left: 8px">重置</Button>
    </FormItem>
  </Form>
</template>
<script setup lang="ts" name="FormDemo">
import { Form, FormItem, Input, Button } from 'tdesign-vue-next';
import { ref, reactive } from 'vue';

const formData = ref({ name: '', email: '', password: '' });
const rules = {
  name: [{ required: true, message: '请输入用户名', type: 'error' }],
  email: [{ required: true, message: '请输入邮箱', type: 'error' }, { email: true, message: '邮箱格式不正确', type: 'warning' }],
  password: [{ required: true, message: '请输入密码', type: 'error' }, { min: 6, message: '至少6个字符', type: 'error' }],
};

const onSubmit = (ctx: { validateResult: boolean }) => {
  if (ctx.validateResult) console.log('提交:', formData.value);
};
</script>
<style scoped>
</style>
```
