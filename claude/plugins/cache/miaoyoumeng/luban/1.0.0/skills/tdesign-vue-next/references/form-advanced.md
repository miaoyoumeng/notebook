# 表单（Form）复杂场景

## 适用场景

- 动态增删表单项。
- 跨字段联动校验。
- 异步校验，例如用户名唯一性。
- 嵌套数据结构。
- 条件显示字段。
- 分步表单。

简单表单使用 `Form` + `FormItem` + `rules` 即可，不必读取本文档。

## 数据源

Form 通过 `data` 绑定表单数据，不使用 `model`：

```vue
<template>
  <Form ref="formRef" :data="formData" :rules="rules" @submit="onSubmit">
    <FormItem label="用户名" name="username">
      <Input v-model="formData.username" />
    </FormItem>
  </Form>
</template>

<script setup lang="ts">
import { reactive, ref } from "vue";
import { Form, FormItem, Input } from "tdesign-vue-next";
import type { FormInstanceFunctions, FormRules, SubmitContext } from "tdesign-vue-next";

const formRef = ref<FormInstanceFunctions>();
const formData = reactive({ username: "" });

const rules: FormRules<typeof formData> = {
  username: [{ required: true, message: "用户名必填" }],
};

const onSubmit = ({ validateResult }: SubmitContext) => {
  if (validateResult === true) {
    console.log("提交", formData);
  }
};
</script>
```

嵌套字段使用数组形式的 `name`：

```vue
<FormItem label="省份" :name="['address', 'province']">
  <Input v-model="formData.address.province" />
</FormItem>
```

## 动态表单项

每项使用稳定唯一的 `id` 作为 key，`name` 使用数组路径：

```vue
<template>
  <Form :data="formData" :rules="rules">
    <FormItem
      v-for="(item, index) in formData.users"
      :key="item.id"
      :label="`用户 ${index + 1}`"
      :name="['users', index, 'name']"
      :rules="[{ required: true, message: '用户名必填' }]"
    >
      <Space>
        <Input v-model="item.name" />
        <Button theme="danger" @click="removeUser(index)">删除</Button>
      </Space>
    </FormItem>
    <FormItem>
      <Button @click="addUser">添加用户</Button>
    </FormItem>
  </Form>
</template>

<script setup lang="ts">
import { reactive } from "vue";
import { Button, Form, FormItem, Input, Space } from "tdesign-vue-next";

const formData = reactive({
  users: [{ id: 1, name: "" }],
});

const rules = {};

let nextId = 2;

const addUser = () => {
  formData.users.push({ id: nextId++, name: "" });
};

const removeUser = (index: number) => {
  formData.users.splice(index, 1);
};
</script>
```

不要用数组下标作为 `key`，删除中间项时会导致输入框复用到错误的数据。

## 跨字段校验

确认密码依赖密码字段：

```vue
<template>
  <Form ref="formRef" :data="formData" :rules="rules">
    <FormItem label="密码" name="password">
      <Input v-model="formData.password" type="password" />
    </FormItem>
    <FormItem label="确认密码" name="confirmPassword">
      <Input v-model="formData.confirmPassword" type="password" />
    </FormItem>
  </Form>
</template>

<script setup lang="ts">
import { reactive, ref } from "vue";
import { Form, FormItem, Input } from "tdesign-vue-next";
import type { FormInstanceFunctions, FormRule, FormRules } from "tdesign-vue-next";

const formRef = ref<FormInstanceFunctions>();
const formData = reactive({ password: "", confirmPassword: "" });

const confirmPasswordValidator: FormRule["validator"] = (value) => {
  if (value !== formData.password) {
    return { result: false, message: "两次输入的密码不一致" };
  }
  return { result: true };
};

const rules: FormRules<typeof formData> = {
  password: [
    { required: true, message: "请输入密码" },
    { min: 6, message: "密码长度不能少于 6 位" },
  ],
  confirmPassword: [
    { required: true, message: "请确认密码" },
    { validator: confirmPasswordValidator },
  ],
};
</script>
```

校验函数只读取数据并返回结果，不执行请求或修改状态。

## 异步校验

```vue
<script setup lang="ts">
import type { FormRule } from "tdesign-vue-next";

const checkUsernameUnique: FormRule["validator"] = async (value) => {
  const response = await fetch(`/api/check-username?name=${encodeURIComponent(String(value))}`);
  const { available } = await response.json();

  if (!available) {
    return { result: false, message: "用户名已存在" };
  }
  return { result: true };
};

const rules = {
  username: [
    { required: true, message: "用户名必填" },
    { validator: checkUsernameUnique, trigger: "blur" },
  ],
};
</script>
```

提交时使用 `await formRef.value?.validate()`，等待异步校验完成后再发送请求。

## 表单实例方法

```ts
import { ref } from "vue";
import type { FormInstanceFunctions } from "tdesign-vue-next";

const formRef = ref<FormInstanceFunctions>();

const validateAll = async () => {
  const result = await formRef.value?.validate();
  return result === true;
};

const validateFields = async (names: string[]) => {
  return formRef.value?.validateOnly(names);
};

const resetForm = () => {
  formRef.value?.reset();
};

const clearValidate = (names?: string[]) => {
  formRef.value?.clearValidate(names);
};

const setFieldsValue = (values: Record<string, unknown>) => {
  formRef.value?.setFieldsValue(values);
};

const getFieldValue = (name: string) => {
  return formRef.value?.getFieldValue(name);
};
```

`reset()` 同时重置值与校验状态；只清除校验状态时使用 `clearValidate()`。

## 条件显示字段

```vue
<template>
  <Form :data="formData" :rules="rules">
    <FormItem label="用户类型" name="userType">
      <RadioGroup v-model="formData.userType">
        <Radio value="personal">个人</Radio>
        <Radio value="enterprise">企业</Radio>
      </RadioGroup>
    </FormItem>

    <FormItem
      v-if="formData.userType === 'enterprise'"
      label="公司名称"
      name="companyName"
      :rules="[{ required: true, message: '公司名称必填' }]"
    >
      <Input v-model="formData.companyName" />
    </FormItem>
  </Form>
</template>

<script setup lang="ts">
import { reactive } from "vue";
import { Form, FormItem, Input, Radio, RadioGroup } from "tdesign-vue-next";

const formData = reactive({
  userType: "personal",
  companyName: "",
});

const rules = {};
</script>
```

切换类型时清空隐藏字段，避免提交残留值：

```ts
const onUserTypeChange = () => {
  if (formData.userType === "personal") {
    formData.companyName = "";
  }
};
```

## 分步表单

```vue
<template>
  <Steps :current="currentStep">
    <StepItem title="基本信息" />
    <StepItem title="详细信息" />
    <StepItem title="完成" />
  </Steps>

  <Form ref="formRef" :data="formData" :rules="currentRules">
    <template v-if="currentStep === 0">
      <FormItem label="姓名" name="name">
        <Input v-model="formData.name" />
      </FormItem>
    </template>

    <template v-if="currentStep === 1">
      <FormItem label="邮箱" name="email">
        <Input v-model="formData.email" />
      </FormItem>
    </template>

    <Space>
      <Button v-if="currentStep > 0" @click="prevStep">上一步</Button>
      <Button v-if="currentStep < 2" theme="primary" @click="nextStep">下一步</Button>
      <Button v-if="currentStep === 2" theme="primary" @click="submit">提交</Button>
    </Space>
  </Form>
</template>

<script setup lang="ts">
import { computed, reactive, ref } from "vue";
import { Button, Form, FormItem, Input, Space, StepItem, Steps } from "tdesign-vue-next";
import type { FormInstanceFunctions, FormRules } from "tdesign-vue-next";

const formRef = ref<FormInstanceFunctions>();
const currentStep = ref(0);
const formData = reactive({ name: "", email: "" });

const stepRules: FormRules<typeof formData>[] = [
  { name: [{ required: true, message: "姓名必填" }] },
  { email: [{ required: true, message: "邮箱必填" }, { email: true }] },
  {},
];

const currentRules = computed(() => stepRules[currentStep.value]);

const nextStep = async () => {
  const result = await formRef.value?.validate();
  if (result === true) {
    currentStep.value += 1;
  }
};

const prevStep = () => {
  currentStep.value -= 1;
};

const submit = () => {
  console.log("提交", formData);
};
</script>
```

## 常见问题

### 动态表单项校验不生效

检查 `name` 是否为数组路径，例如 `['users', 0, 'name']`；检查每项是否有唯一 `key`。

### 重置后校验状态未清除

`reset()` 会同时重置值与校验状态。只清校验状态使用 `clearValidate()`。

### 异步校验未完成就提交

使用 `await formRef.value?.validate()`，不要使用同步的 `validateOnly` 结果判断提交时机。

### 如何获取完整表单数据

```ts
const allValues = formRef.value?.getAllFieldsValue();
```

## 必须避免

- 在输入组件上同时使用 `v-model` 和 Form 的初始化数据，造成状态不一致。
- 在运行时替换 `rules` 对象引用，导致校验规则丢失；需要动态规则时使用 `computed`。
- 在校验函数中发送请求之外的副作用。
- 动态表单项缺少唯一 `name`。
- 用数组下标作为动态项的 `key`。
