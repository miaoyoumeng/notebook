# 树组件（Tree）复杂场景

## 适用场景

- 异步加载节点。
- 父子节点选中不关联。
- 大数据量虚拟滚动。
- 拖拽排序。
- 节点搜索过滤。
- 自定义节点渲染。

简单树形展示使用 `Tree` + `data` + `keys` 即可。

## 字段映射

数据结构字段与组件默认字段不一致时，通过 `keys` 映射：

```vue
<template>
  <Tree
    :data="treeData"
    :keys="{ value: 'id', label: 'name', children: 'children' }"
  />
</template>
```

`keys` 与实际字段不一致会导致节点无法渲染或选中失效。

## 异步加载节点

`load` 必须返回 Promise。父节点用 `children: true` 标记存在未加载的子节点：

```vue
<template>
  <Tree
    :data="treeData"
    :keys="keys"
    :load="loadChildren"
    :expand-on-click-node="false"
    @expand="onExpand"
  />
</template>

<script setup lang="ts">
import { ref } from "vue";
import { Tree } from "tdesign-vue-next";
import type { TreeProps } from "tdesign-vue-next";

const keys = { value: "id", label: "name", children: "children" };

const treeData = ref([
  { id: "1", name: "节点 1", children: true },
  { id: "2", name: "节点 2", children: true },
]);

const loadChildren: TreeProps["load"] = async (node) => {
  const parentId = String(node.value);
  const response = await fetch(`/api/tree/children?parent=${encodeURIComponent(parentId)}`);
  const data = await response.json();

  return data.map((item: { id: string; name: string; hasChildren: boolean }) => ({
    id: item.id,
    name: item.name,
    children: item.hasChildren ? true : undefined,
  }));
};

const onExpand = () => {
  // 展开后可按需记录状态
};
</script>
```

叶子节点不要设置 `children: true`，否则会一直显示加载状态。

## 父子选中不关联

```vue
<template>
  <Tree
    v-model="checkedValues"
    :data="treeData"
    checkable
    :check-strictly="true"
    @check="onCheck"
  />
</template>

<script setup lang="ts">
import { ref } from "vue";
import { Tree } from "tdesign-vue-next";
import type { TreeNodeValue } from "tdesign-vue-next";

const checkedValues = ref<TreeNodeValue[]>([]);

const treeData = ref([
  {
    value: "1",
    label: "父节点",
    children: [
      { value: "1-1", label: "子节点 1" },
      { value: "1-2", label: "子节点 2" },
    ],
  },
]);

const onCheck = (value: TreeNodeValue[]) => {
  console.log("选中值", value);
};
</script>
```

`check-strictly` 为 `true` 时，选中父节点不会自动选中子节点。

## 虚拟滚动

```vue
<template>
  <Tree
    :data="largeTreeData"
    :scroll="{ type: 'virtual' }"
    :height="400"
    checkable
  />
</template>

<script setup lang="ts">
import { computed } from "vue";

const generateTree = (level: number, parentKey = ""): Array<Record<string, unknown>> => {
  if (level === 0) return [];

  return Array.from({ length: 10 }, (_, index) => {
    const key = parentKey ? `${parentKey}-${index}` : String(index);
    return {
      value: key,
      label: `节点 ${key}`,
      children: generateTree(level - 1, key),
    };
  });
};

const largeTreeData = computed(() => generateTree(4));
</script>
```

节点超过 1000 个时启用虚拟滚动，并设置固定高度。

## 拖拽排序

```vue
<template>
  <Tree
    :data="treeData"
    draggable
    @drag-start="onDragStart"
    @drag-end="onDragEnd"
    @drop="onDrop"
  />
</template>

<script setup lang="ts">
import { ref } from "vue";
import { MessagePlugin, Tree } from "tdesign-vue-next";
import type { DropContext, TreeNodeModel } from "tdesign-vue-next";

const treeData = ref([
  {
    value: "1",
    label: "节点 1",
    children: [
      { value: "1-1", label: "节点 1-1" },
      { value: "1-2", label: "节点 1-2" },
    ],
  },
  { value: "2", label: "节点 2" },
]);

const onDragStart = (context: { node: TreeNodeModel }) => {
  console.log("开始拖拽", context.node.label);
};

const onDragEnd = (context: { node: TreeNodeModel }) => {
  console.log("结束拖拽", context.node.label);
};

const onDrop = (context: DropContext<Record<string, unknown>>) => {
  const { dragNode, dropNode, dropPosition } = context;
  console.log(`将 ${dragNode?.label} 拖到 ${dropNode?.label} 的 ${dropPosition} 位置`);
  MessagePlugin.success("拖拽完成");
};
</script>
```

拖拽完成后调用接口保存顺序，不要只修改本地数据。

## 搜索过滤

```vue
<template>
  <Space direction="vertical" style="width: 100%">
    <Input v-model="keyword" placeholder="搜索节点" @change="onSearch" />
    <Tree
      ref="treeRef"
      :data="treeData"
      :filter="filterNode"
      :expand-all="Boolean(keyword)"
    />
  </Space>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { Input, Space, Tree } from "tdesign-vue-next";
import type { TreeInstanceFunctions, TreeProps } from "tdesign-vue-next";

const keyword = ref("");
const treeRef = ref<TreeInstanceFunctions>();

const treeData = ref([
  {
    value: "1",
    label: "北京",
    children: [
      { value: "1-1", label: "海淀区" },
      { value: "1-2", label: "朝阳区" },
    ],
  },
  {
    value: "2",
    label: "上海",
    children: [
      { value: "2-1", label: "浦东新区" },
      { value: "2-2", label: "黄浦区" },
    ],
  },
]);

const filterNode: TreeProps["filter"] = (node) => {
  if (!keyword.value) return true;
  return String(node.label ?? "").toLowerCase().includes(keyword.value.toLowerCase());
};

const onSearch = () => {
  treeRef.value?.filter(keyword.value);
};
</script>
```

搜索时展开全部匹配路径，否则父节点收起后看不到结果。

## 自定义节点

```vue
<template>
  <Tree :data="treeData">
    <template #label="{ node }">
      <div class="custom-node">
        <FolderIcon v-if="node.children?.length" />
        <FileIcon v-else />
        <span class="node-label">{{ node.label }}</span>
        <Space class="node-actions" size="small">
          <Button size="small" variant="text" @click.stop="onEdit(node)">
            <EditIcon />
          </Button>
          <Button size="small" variant="text" @click.stop="onDelete(node)">
            <DeleteIcon />
          </Button>
        </Space>
      </div>
    </template>
  </Tree>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { Button, Space, Tree } from "tdesign-vue-next";
import { DeleteIcon, EditIcon, FileIcon, FolderIcon } from "tdesign-icons-vue-next";
import type { TreeNodeModel } from "tdesign-vue-next";

const treeData = ref([
  {
    value: "1",
    label: "文件夹 1",
    children: [
      { value: "1-1", label: "文件 1.txt" },
      { value: "1-2", label: "文件 2.txt" },
    ],
  },
]);

const onEdit = (node: TreeNodeModel) => {
  console.log("编辑节点", node);
};

const onDelete = (node: TreeNodeModel) => {
  console.log("删除节点", node);
};
</script>

<style scoped>
.custom-node {
  display: flex;
  align-items: center;
  gap: 4px;
  width: 100%;
}

.node-label {
  flex: 1;
}

.node-actions {
  opacity: 0;
  transition: opacity 0.2s;
}

.custom-node:hover .node-actions {
  opacity: 1;
}
</style>
```

操作按钮使用 `@click.stop`，避免触发节点选中。
