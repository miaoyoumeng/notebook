# 表格（Table）补充场景

## 适用场景

- 固定列与固定表头。
- 可展开行。
- 合并单元格。
- 表格实例与状态读取。

本文只覆盖固定列、展开行、合并单元格与表格实例。

## 固定列与表头

```vue
<template>
  <Table
    :data="data"
    :columns="columns"
    row-key="id"
    :max-height="400"
    :scroll="{ x: 1500 }"
  />
</template>

<script setup lang="ts">
import { computed, ref } from "vue";

const data = ref([
  { id: 1, name: "张三", age: 25, address: "北京市朝阳区", email: "zhang@example.com", phone: "13800138000" },
  { id: 2, name: "李四", age: 30, address: "上海市浦东新区", email: "li@example.com", phone: "13800138001" },
]);

const columns = computed(() => [
  { colKey: "id", title: "ID", fixed: "left" as const, width: 100 },
  { colKey: "name", title: "姓名", width: 200 },
  { colKey: "age", title: "年龄", width: 150 },
  { colKey: "address", title: "地址", width: 300 },
  { colKey: "email", title: "邮箱", width: 250 },
  { colKey: "phone", title: "电话", width: 200 },
  { colKey: "operate", title: "操作", fixed: "right" as const, width: 150 },
]);
</script>
```

横向滚动时，固定列必须设置 `width`，否则列宽可能抖动。固定表头使用 `max-height`，固定列使用 `scroll.x`。

## 可展开行

```vue
<template>
  <Table
    :data="data"
    :columns="columns"
    row-key="id"
    :expand-on-row-click="true"
    :expanded-row="expandedRowRender"
  />
</template>

<script setup lang="ts">
import { computed, h, ref } from "vue";

const data = ref([
  { id: 1, name: "张三", description: "张三的详细描述" },
  { id: 2, name: "李四", description: "李四的详细描述" },
]);

const columns = computed(() => [
  { colKey: "expand-icon", type: "expand" as const, width: 50 },
  { colKey: "id", title: "ID" },
  { colKey: "name", title: "姓名" },
]);

const expandedRowRender = ({ row }: { row: { description: string } }) => {
  return h("div", { style: { padding: "16px" } }, row.description);
};
</script>
```

展开列使用 `colKey: "expand-icon"` 与 `type: "expand"`。点击整行展开时设置 `expand-on-row-click`。

## 合并单元格

```vue
<template>
  <Table
    :data="data"
    :columns="columns"
    row-key="id"
    :rowspan-and-colspan="rowspanHandler"
  />
</template>

<script setup lang="ts">
import { computed, ref } from "vue";
import type { TableRowspanAndColspanFunc } from "tdesign-vue-next";

const data = ref([
  { id: 1, category: "水果", name: "苹果", price: 5 },
  { id: 2, category: "水果", name: "香蕉", price: 3 },
  { id: 3, category: "蔬菜", name: "白菜", price: 2 },
]);

const columns = computed(() => [
  { colKey: "category", title: "分类" },
  { colKey: "name", title: "名称" },
  { colKey: "price", title: "价格" },
]);

const rowspanHandler: TableRowspanAndColspanFunc<Record<string, unknown>> = ({
  col,
  rowIndex,
}) => {
  if (col.colKey === "category" && rowIndex === 0) {
    return { rowspan: 2 };
  }
  if (col.colKey === "category" && rowIndex === 1) {
    return { rowspan: 0 };
  }
  return {};
};
</script>
```

被合并的行返回 `rowspan: 0`，首行返回合并的行数。合并依赖稳定的 `row-key` 与数据顺序。

## 常见问题

### 虚拟滚动行高不一致

为虚拟滚动设置固定 `rowHeight`，并让内容单行显示或使用固定高度容器。

### 大数据量筛选卡顿

使用服务端筛选，关闭本地筛选。列配置只设置 `filter` 类型，不在前端遍历全量数据。

### 列宽自适应

开启 `resizable` 允许拖拽列宽，或为每列设置合理的初始 `width`。

### 如何获取表格实例

```ts
import { ref } from "vue";
import { Table } from "tdesign-vue-next";

const tableRef = ref<InstanceType<typeof Table>>();
const selected = tableRef.value?.selectedRowKeys;
```

## 必须避免

- 不设置 `row-key`，导致行选择、展开、编辑异常。
- 每次渲染都重建 `columns` 数组。
- 大数据量不启用虚拟滚动，或启用后不设置固定行高。
- 同时维护受控与非受控状态，导致分页或排序不一致。
- 在 `cell` 渲染函数里使用未导入的组件名字符串。
- 回调用参数名覆盖同名 `ref`。
