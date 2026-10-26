# 弹窗与抽屉（Dialog / Drawer）复杂场景

## 适用场景

- 弹窗内表单。
- 关闭前拦截与异步确认。
- 命令式调用。
- 嵌套弹窗。
- 关闭销毁与状态保持。

简单弹窗使用 `Dialog` + `v-model:visible` 即可；侧边面板使用 `Drawer`。

## 基础弹窗

```vue
<template>
  <Button @click="visible = true">打开弹窗</Button>

  <Dialog
    v-model:visible="visible"
    header="弹窗标题"
    :confirm-btn="confirmBtn"
    :cancel-btn="cancelBtn"
    @confirm="onConfirm"
    @cancel="onCancel"
  >
    <p>弹窗内容</p>
  </Dialog>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { Button, Dialog, MessagePlugin } from "tdesign-vue-next";
import type { DialogProps } from "tdesign-vue-next";

const visible = ref(false);

const confirmBtn: DialogProps["confirmBtn"] = { content: "确定", theme: "primary" };
const cancelBtn: DialogProps["cancelBtn"] = { content: "取消", theme: "default" };

const onConfirm = () => {
  MessagePlugin.success("已确认");
  visible.value = false;
};

const onCancel = () => {
  visible.value = false;
};
</script>
```

每个弹窗使用独立的 `visible` 状态，不要多个弹窗共用一个布尔值。

## 关闭拦截

`:on-close` 返回 `false` 或 `Promise<false>` 阻止关闭：

```vue
<template>
  <Button @click="visible = true">打开弹窗</Button>

  <Dialog v-model:visible="visible" header="编辑内容" :on-close="onBeforeClose">
    <Form :data="formData">
      <FormItem label="名称" name="name">
        <Input v-model="formData.name" />
      </FormItem>
    </Form>
  </Dialog>
</template>

<script setup lang="ts">
import { reactive, ref } from "vue";
import { Button, Dialog, DialogPlugin, Form, FormItem, Input } from "tdesign-vue-next";
import type { DialogCloseContext } from "tdesign-vue-next";

const visible = ref(false);
const formData = reactive({ name: "" });
const originalName = ref("");

const hasChanges = () => formData.name !== originalName.value;

const onBeforeClose = (context: DialogCloseContext): boolean | Promise<boolean> => {
  if (context.trigger === "confirm") {
    return true;
  }

  if (!hasChanges()) {
    return true;
  }

  return new Promise((resolve) => {
    const confirmDialog = DialogPlugin.confirm({
      header: "提示",
      body: "有未保存的更改，确定要关闭吗？",
      onConfirm: () => {
        confirmDialog.hide();
        resolve(true);
      },
      onCancel: () => {
        confirmDialog.hide();
        resolve(false);
      },
    });
  });
};
</script>
```

确认按钮触发时直接放行，避免二次确认。

## 弹窗内表单

```vue
<template>
  <Button @click="openDialog">新建用户</Button>

  <Dialog
    v-model:visible="visible"
    header="新建用户"
    :confirm-btn="{ loading: submitting }"
    @confirm="onSubmit"
  >
    <Form ref="formRef" :data="formData" :rules="rules">
      <FormItem label="用户名" name="username">
        <Input v-model="formData.username" />
      </FormItem>
      <FormItem label="邮箱" name="email">
        <Input v-model="formData.email" />
      </FormItem>
    </Form>
  </Dialog>
</template>

<script setup lang="ts">
import { reactive, ref } from "vue";
import { Button, Dialog, Form, FormItem, Input, MessagePlugin } from "tdesign-vue-next";
import type { FormInstanceFunctions, FormRules } from "tdesign-vue-next";

const visible = ref(false);
const submitting = ref(false);
const formRef = ref<FormInstanceFunctions>();
const formData = reactive({ username: "", email: "" });

const rules: FormRules<typeof formData> = {
  username: [{ required: true, message: "用户名必填" }],
  email: [
    { required: true, message: "邮箱必填" },
    { email: true, message: "请输入有效的邮箱" },
  ],
};

const openDialog = () => {
  formData.username = "";
  formData.email = "";
  formRef.value?.clearValidate();
  visible.value = true;
};

const onSubmit = async () => {
  const result = await formRef.value?.validate();
  if (result !== true) return;

  submitting.value = true;
  try {
    await new Promise((resolve) => setTimeout(resolve, 800));
    MessagePlugin.success("创建成功");
    visible.value = false;
  } finally {
    submitting.value = false;
  }
};
</script>
```

每次打开弹窗时重置数据和校验状态，避免上次的残留。

## 命令式调用

```ts
import { h } from "vue";
import { DialogPlugin, MessagePlugin } from "tdesign-vue-next";

const showConfirm = () => {
  const dialog = DialogPlugin.confirm({
    header: "删除确认",
    body: "确定要删除这条记录吗？此操作不可恢复。",
    theme: "danger",
    confirmBtn: { content: "删除", theme: "danger" },
    onConfirm: async () => {
      dialog.update({ confirmBtn: { loading: true } });
      try {
        await new Promise((resolve) => setTimeout(resolve, 800));
        MessagePlugin.success("删除成功");
        dialog.hide();
      } catch {
        MessagePlugin.error("删除失败");
        dialog.update({ confirmBtn: { loading: false } });
      }
    },
    onCancel: () => {
      dialog.hide();
    },
  });
};

const showAlert = () => {
  DialogPlugin.alert({
    header: "提示",
    body: "操作已完成",
  });
};

const showCustom = () => {
  const dialog = DialogPlugin({
    header: "自定义内容",
    body: () =>
      h("div", { style: { padding: "20px" } }, [
        h("p", "这是自定义渲染的内容"),
      ]),
    footer: false,
    onClose: () => {
      dialog.destroy();
    },
  });
};
```

命令式弹窗返回实例，使用 `hide()`、`update()`、`destroy()` 控制。

## 嵌套弹窗

```vue
<template>
  <Button @click="outerVisible = true">打开外层弹窗</Button>

  <Dialog v-model:visible="outerVisible" header="外层弹窗" width="600px">
    <p>外层内容</p>
    <Button @click="innerVisible = true">打开内层弹窗</Button>

    <Dialog
      v-model:visible="innerVisible"
      header="内层弹窗"
      width="400px"
      :attach="false"
    >
      <p>内层内容</p>
    </Dialog>
  </Dialog>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { Button, Dialog } from "tdesign-vue-next";

const outerVisible = ref(false);
const innerVisible = ref(false);
</script>
```

内层弹窗设置 `:attach="false"`，使其挂载在外层弹窗内部，避免层级与销毁顺序混乱。

## 抽屉基础用法

```vue
<template>
  <Button @click="openDrawer('right')">打开右侧抽屉</Button>

  <Drawer
    v-model:visible="visible"
    :header="header"
    :placement="placement"
    :size="size"
  >
    <p>抽屉内容</p>
    <template #footer>
      <Space>
        <Button @click="visible = false">取消</Button>
        <Button theme="primary" @click="onConfirm">确认</Button>
      </Space>
    </template>
  </Drawer>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { Button, Drawer, Space } from "tdesign-vue-next";
import type { DrawerProps } from "tdesign-vue-next";

const visible = ref(false);
const header = ref("抽屉标题");
const placement = ref<DrawerProps["placement"]>("right");
const size = ref("400px");

const openDrawer = (position: DrawerProps["placement"]) => {
  placement.value = position;
  size.value = position === "top" || position === "bottom" ? "300px" : "400px";
  visible.value = true;
};

const onConfirm = () => {
  visible.value = false;
};
</script>
```

抽屉底部按钮放在 `#footer` 插槽，不依赖组件内置按钮。

## 销毁与状态保持

```vue
<template>
  <Space>
    <Button @click="destroyVisible = true">销毁模式</Button>
    <Button @click="keepVisible = true">保持模式</Button>
  </Space>

  <Dialog v-model:visible="destroyVisible" header="销毁模式" :destroy-on-close="true">
    <ExpensivePanel />
  </Dialog>

  <Dialog v-model:visible="keepVisible" header="保持模式" :destroy-on-close="false">
    <FormWithState />
  </Dialog>
</template>
```

- `destroy-on-close="true"`：每次打开重新初始化，适合重组件。
- `destroy-on-close="false"`：关闭后保留状态，适合需要保留输入的草稿表单。

## 常见问题

### 弹窗打开后页面滚动条消失

默认阻止背景滚动。需要允许滚动时设置：

```vue
<Dialog :prevent-scroll-through="false" />
```

### 如何更新命令式弹窗内容

```ts
const dialog = DialogPlugin({ body: "初始内容" });
dialog.update({ body: "更新后的内容" });
```

### 关闭动画结束后执行操作

监听 `closed` 事件，不是 `close`。
