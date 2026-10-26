# 表格（Table）复杂场景

## 适用场景

- 服务端分页、排序、筛选。
- 大数据量虚拟滚动。
- 单元格或整行编辑。
- 树形表格。
- 行选择与批量操作。

简单表格使用 `Table` + `columns` + `data` 即可。

## 基础约束

每行数据提供稳定唯一的 `row-key`：

```vue
<Table :data="data" row-key="id" :columns="columns" />
```

列配置使用 `computed` 缓存，避免每次渲染创建新数组：

```ts
import { computed } from "vue";

const columns = computed(() => [
  { colKey: "name", title: "姓名" },
  { colKey: "age", title: "年龄" },
]);
```

## 服务端分页、排序、筛选

```vue
<template>
  <Table
    :data="tableData"
    :columns="columns"
    :pagination="pagination"
    :sort="sortInfo"
    :filter-value="filterValue"
    :loading="loading"
    row-key="id"
    @page-change="onPageChange"
    @sort-change="onSortChange"
    @filter-change="onFilterChange"
  />
</template>

<script setup lang="ts">
import { computed, reactive, ref } from "vue";
import { Table } from "tdesign-vue-next";
import type { FilterValue, PageInfo, TableSort } from "tdesign-vue-next";

const tableData = ref([]);
const loading = ref(false);

const pagination = reactive({
  current: 1,
  pageSize: 10,
  total: 0,
});

const sortInfo = ref<TableSort>({ sortBy: "id", descending: false });
const filterValue = ref<FilterValue>({});

const columns = computed(() => [
  { colKey: "id", title: "ID", sortType: "all" as const },
  { colKey: "name", title: "姓名", filter: { type: "input" as const } },
  {
    colKey: "status",
    title: "状态",
    filter: {
      type: "single" as const,
      list: [
        { label: "启用", value: 1 },
        { label: "禁用", value: 0 },
      ],
    },
  },
]);

const fetchData = async () => {
  loading.value = true;
  try {
    const response = await fetch("/api/list", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        page: pagination.current,
        pageSize: pagination.pageSize,
        sortBy: sortInfo.value?.sortBy,
        descending: sortInfo.value?.descending,
        filters: filterValue.value,
      }),
    });
    const { data, total } = await response.json();
    tableData.value = data;
    pagination.total = total;
  } finally {
    loading.value = false;
  }
};

const onPageChange = (pageInfo: PageInfo) => {
  pagination.current = pageInfo.current;
  pagination.pageSize = pageInfo.pageSize;
  fetchData();
};

const onSortChange = (sort: TableSort) => {
  sortInfo.value = sort;
  pagination.current = 1;
  fetchData();
};

const onFilterChange = (filters: FilterValue) => {
  filterValue.value = filters;
  pagination.current = 1;
  fetchData();
};

fetchData();
</script>
```

分页、排序、筛选状态统一由组件事件驱动，不在本地对服务端数据二次排序。

## 行选择与批量操作

```vue
<template>
  <Space direction="vertical" style="width: 100%">
    <Button :disabled="selectedRowKeys.length === 0" @click="batchDelete">
      批量删除（{{ selectedRowKeys.length }}）
    </Button>

    <Table
      :data="data"
      :columns="columns"
      row-key="id"
      :selected-row-keys="selectedRowKeys"
      @select-change="onSelectChange"
    />
  </Space>
</template>

<script setup lang="ts">
import { computed, ref } from "vue";
import { Button, Space, Table } from "tdesign-vue-next";
import type { SelectOptions } from "tdesign-vue-next";

const data = ref([
  { id: 1, name: "张三" },
  { id: 2, name: "李四" },
]);

const selectedRowKeys = ref<(string | number)[]>([]);

const columns = computed(() => [
  { colKey: "row-select", type: "multiple" as const, width: 50 },
  { colKey: "id", title: "ID" },
  { colKey: "name", title: "姓名" },
]);

const onSelectChange = (
  keys: (string | number)[],
  context: SelectOptions<Record<string, unknown>>,
) => {
  selectedRowKeys.value = keys;
  console.log("选中行数据", context.selectedRowData);
};

const batchDelete = () => {
  console.log("删除", selectedRowKeys.value);
};
</script>
```

回调参数不要与 `ref` 同名，否则赋值会覆盖参数而不是更新选中状态。

## 虚拟滚动

```vue
<template>
  <Table
    :data="largeData"
    :columns="columns"
    :scroll="{ type: 'virtual', rowHeight: 48 }"
    :height="500"
    row-key="id"
  />
</template>

<script setup lang="ts">
import { computed, ref } from "vue";

const largeData = ref(
  Array.from({ length: 10000 }, (_, index) => ({
    id: index + 1,
    name: `用户 ${index + 1}`,
    age: 18 + (index % 50),
  })),
);

const columns = computed(() => [
  { colKey: "id", title: "ID", width: 100 },
  { colKey: "name", title: "姓名", width: 200 },
  { colKey: "age", title: "年龄", width: 100 },
]);
</script>
```

行数超过 1000 时启用虚拟滚动。虚拟滚动必须设置固定行高，避免滚动位置计算错误。

## 可编辑单元格

```vue
<template>
  <Table
    :data="data"
    :columns="columns"
    row-key="id"
    :editable-row-keys="editableRowKeys"
    @row-edit="onRowEdit"
    @row-validate="onRowValidate"
  />
</template>

<script setup lang="ts">
import { computed, ref } from "vue";
import { Button, Table } from "tdesign-vue-next";
import type { PrimaryTableCol } from "tdesign-vue-next";

const data = ref([
  { id: 1, name: "张三", age: 25 },
  { id: 2, name: "李四", age: 30 },
]);

const editableRowKeys = ref<(string | number)[]>([]);

const editRow = (id: number) => {
  editableRowKeys.value = [...editableRowKeys.value, id];
};

const cancelEdit = (id: number) => {
  editableRowKeys.value = editableRowKeys.value.filter((key) => key !== id);
};

const saveRow = (id: number) => {
  editableRowKeys.value = editableRowKeys.value.filter((key) => key !== id);
};

const columns = computed<PrimaryTableCol[]>(() => [
  { colKey: "id", title: "ID", width: 100 },
  {
    colKey: "name",
    title: "姓名",
    edit: {
      component: "Input",
      props: { clearable: true },
      rules: [{ required: true, message: "姓名必填" }],
    },
  },
  {
    colKey: "age",
    title: "年龄",
    edit: {
      component: "InputNumber",
      props: { min: 0, max: 120 },
    },
  },
  {
    colKey: "operate",
    title: "操作",
    cell: (h, { row }) => {
      const isEditing = editableRowKeys.value.includes(row.id);
      if (isEditing) {
        return [
          h(Button, { size: "small", onClick: () => saveRow(row.id) }, () => "保存"),
          h(Button, { size: "small", onClick: () => cancelEdit(row.id) }, () => "取消"),
        ];
      }
      return h(Button, { size: "small", onClick: () => editRow(row.id) }, () => "编辑");
    },
  },
]);

const onRowEdit = (context: { row: Record<string, unknown> }) => {
  console.log("行编辑", context.row);
};

const onRowValidate = (context: { result: Record<string, unknown> }) => {
  console.log("行校验", context.result);
};
</script>
```

`edit.component` 使用组件名字符串时，组件必须在应用中注册。

## 树形表格

```vue
<template>
  <Table
    :data="treeData"
    :columns="columns"
    row-key="id"
    :tree="{ childrenKey: 'children', treeNodeColumnIndex: 0 }"
    :expanded-row-keys="expandedRowKeys"
    @expanded-row-keys-change="onExpandedChange"
  />
</template>

<script setup lang="ts">
import { computed, ref } from "vue";

const treeData = ref([
  {
    id: 1,
    name: "部门 A",
    children: [
      { id: 11, name: "小组 A-1" },
      { id: 12, name: "小组 A-2" },
    ],
  },
  {
    id: 2,
    name: "部门 B",
    children: [{ id: 21, name: "小组 B-1" }],
  },
]);

const expandedRowKeys = ref<(string | number)[]>([1]);
const columns = computed(() => [{ colKey: "name", title: "名称" }]);

const onExpandedChange = (keys: (string | number)[]) => {
  expandedRowKeys.value = keys;
};
</script>
```
