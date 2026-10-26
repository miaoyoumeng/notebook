# 树组件（Tree）补充场景

## 适用场景

- 节点增删改。
- 单选树。
- 读取半选、选中与展开节点。
- 滚动定位到指定节点。

本文只覆盖节点编辑、单选与实例状态读取。

## 节点增删改

```vue
<template>
  <Space direction="vertical">
    <Space>
      <Button @click="appendNode">添加根节点</Button>
      <Button @click="appendChildNode">添加子节点</Button>
      <Button theme="danger" @click="removeSelectedNodes">删除选中节点</Button>
    </Space>
    <Tree
      ref="treeRef"
      v-model:expanded="expandedKeys"
      v-model:actived="activedKeys"
      :data="treeData"
      activable
    />
  </Space>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { Button, Space, Tree } from "tdesign-vue-next";
import type { TreeNodeValue, TreeInstanceFunctions } from "tdesign-vue-next";

const treeRef = ref<TreeInstanceFunctions>();
const expandedKeys = ref<TreeNodeValue[]>([]);
const activedKeys = ref<TreeNodeValue[]>([]);

const treeData = ref([
  {
    value: "1",
    label: "节点 1",
    children: [{ value: "1-1", label: "节点 1-1" }],
  },
]);

let nextId = 100;

const appendNode = () => {
  const value = String(nextId++);
  treeRef.value?.appendTo("", { value, label: `新节点 ${value}` });
};

const appendChildNode = () => {
  const parentKey = activedKeys.value[0];
  if (!parentKey) return;

  const value = String(nextId++);
  treeRef.value?.appendTo(parentKey, { value, label: `子节点 ${value}` });

  if (!expandedKeys.value.includes(parentKey)) {
    expandedKeys.value = [...expandedKeys.value, parentKey];
  }
};

const removeSelectedNodes = () => {
  activedKeys.value.forEach((key) => {
    treeRef.value?.remove(key);
  });
  activedKeys.value = [];
};
</script>
```

增删改通过 Tree 实例方法完成，不直接替换整个 `data` 数组。父节点新增子节点后同步展开。

## 单选树

```vue
<template>
  <Tree
    v-model:actived="selectedKeys"
    :data="treeData"
    activable
    :active-multiple="false"
    @active="onActive"
  />
</template>

<script setup lang="ts">
import { ref } from "vue";
import { Tree } from "tdesign-vue-next";
import type { TreeNodeModel, TreeNodeValue } from "tdesign-vue-next";

const selectedKeys = ref<TreeNodeValue[]>([]);

const treeData = ref([
  {
    value: "1",
    label: "选项 1",
    children: [
      { value: "1-1", label: "选项 1-1" },
      { value: "1-2", label: "选项 1-2" },
    ],
  },
  { value: "2", label: "选项 2" },
]);

const onActive = (value: TreeNodeValue[], context: { node: TreeNodeModel }) => {
  console.log("选中", value[0], context.node);
};
</script>
```

`active-multiple="false"` 保证只能激活一个节点。选中值仍以数组形式返回。

## 读取实例状态

```ts
const indeterminateKeys = treeRef.value?.getIndeterminate();
const checkedNodes = treeRef.value?.getChecked({ includeHalfChecked: false });
const expandedKeys = treeRef.value?.getExpanded();
```

`getIndeterminate()` 读取半选节点，`getChecked()` 读取选中节点，`getExpanded()` 读取展开节点。

## 滚动定位

```ts
treeRef.value?.scrollTo("1-2");
```

目标节点必须已渲染；异步加载的节点先展开父节点并等待数据返回，再调用 `scrollTo`。

## 常见问题

### 异步加载后节点展开失败

检查 `load` 返回的数据字段是否与 `keys` 一致；叶子节点不要返回 `children: true`。

## 必须避免

- `keys` 与数据结构不匹配。
- 异步 `load` 返回非 Promise。
- 大数据量不启用虚拟滚动。
- 直接替换整个 `data` 数组来增删节点，改用实例方法。
- 自定义节点中的按钮未阻止冒泡。
