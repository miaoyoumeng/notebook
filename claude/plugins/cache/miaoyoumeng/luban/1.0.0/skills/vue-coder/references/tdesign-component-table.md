# TDesign Vue Next Table 组件参考文档

TDesign Table（`<t-table>`）是一个功能丰富的数据表格组件，支持排序、筛选、行选中、展开行、列宽调整、虚拟滚动、分页、可编辑单元格等能力。

## Props（属性）

| 属性名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `data` | `Array<T>` | `[]` | 数据源，泛型 T 指表格数据类型 |
| `columns` | `Array<PrimaryTableCol<T>>` | `[]` | 列配置，定义每列的显示行为 |
| `rowKey` | `string` | `'id'` | 唯一标识一行数据的字段名 |
| `pagination` | `PaginationProps` | `-` | 分页配置，值为空则不显示 |
| `loading` | `boolean \| TNode` | `false` | 加载中状态 |
| `bordered` | `boolean` | `false` | 是否显示表格边框 |
| `stripe` | `boolean` | `false` | 是否显示斑马纹 |
| `hover` | `boolean` | `false` | 是否显示鼠标悬浮状态 |
| `resizable` | `boolean` | `false` | 是否允许调整列宽 |
| `height` / `maxHeight` | `string \| number` | `-` | 表格高度/最大高度，超出出现滚动条 |
| `sorted` | `TableSort` | `-` | 排序控制：`sortBy` 排序字段，`descending` 是否降序 |
| `filterValue` | `FilterValue` | `-` | 过滤数据的值 |
| `selectedRowKeys` | `Array<string \| number>` | `[]` | 选中行的 key 列表 |
| `expandedRowKeys` | `Array<string \| number>` | `[]` | 已展开行的 key 列表 |
| `headerAffixedTop` | `boolean \| Partial<AffixProps>` | `false` | 表头吸顶 |

## Events（事件）

| 事件名 | 参数 | 说明 |
|--------|------|------|
| `onChange` | `(data: TableChangeData, context: TableChangeContext)` | 分页、排序、过滤等变化时触发，`currentData` 为变化后的数据 |
| `onSelectChange` | `(selectedRowKeys, options: SelectOptions)` | 选中行变化时触发，含 `type`（check/uncheck）、`currentRowKey` 等信息 |
| `onSortChange` | `(sort: TableSort, options: SortOptions)` | 排序变化时触发，含 `sortBy`、`sortType`、`col` 等信息 |
| `onRowClick` | `(context: RowEventContext)` | 行点击时触发，含 `row`、`rowIndex` 等信息 |

## 使用示例

```vue
<template>
  <t-table
    :data="tableData"
    :columns="columns"
    row-key="id"
    :loading="loading"
    bordered
    hover
    stripe
    :pagination="pagination"
    @select-change="handleSelectChange"
    @sort-change="handleSortChange"
  />
</template>
<script setup lang="ts" name="DataTable">
import { ref } from 'vue'
import type { PrimaryTableCol, TablePaginationProps, SortConfig } from 'tdesign-vue-next'

interface TableRowData {
  id: string
  name: string
  age: number
  address: string
  enable: boolean
}

const columns: PrimaryTableCol<TableRowData>[] = [
  { colKey: 'row-select', type: 'multiple', width: '50px' },
  { colKey: 'serial-number', title: '序号', width: '60px' },
  { title: '姓名', colKey: 'name', width: '120' },
  { title: '年龄', colKey: 'age', width: '80', align: 'center' as const },
  { title: '地址', colKey: 'address', width: '200', ellipsis: true },
  {
    title: '状态', colKey: 'enable', width: '100',
    cell: ({ row }) => (row.enable ? '启用' : '禁用'),
  },
]

const tableData = ref<TableRowData[]>([
  { id: '1', name: '张三', age: 28, address: '北京市朝阳区', enable: true },
  { id: '2', name: '李四', age: 32, address: '上海市浦东新区', enable: false },
  { id: '3', name: '王五', age: 25, address: '广州市天河区', enable: true },
])

const loading = ref(false)
const pagination = ref<TablePaginationProps>({ defaultPageSize: 10, total: 3 })

const handleSelectChange = (selectedRowKeys: (string | number)[], context: any) => {
  console.log('选中行:', selectedRowKeys)
}

const handleSortChange = (sort: SortConfig, context: any) => {
  console.log('排序条件:', sort)
}
</script>
<style scoped>
</style>
```

Sources:
- [TDesign Vue Next Table 官方文档](https://tdesign.tencent.com/vue-next/components/table)
- [Tencent/tdesign-vue-next GitHub](https://github.com/Tencent/tdesign-vue-next/blob/develop/packages/components/table/type.ts)
