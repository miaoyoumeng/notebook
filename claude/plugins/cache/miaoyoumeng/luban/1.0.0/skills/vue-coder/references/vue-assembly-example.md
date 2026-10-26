# 页面组装与事件绑定示例

## 示例：用户列表页面

展示如何完成页面组装、事件绑定和业务逻辑调用。

```vue
<template>
  <t-card title="用户列表" :bordered="false">
    <!-- 搜索表单 -->
    <t-form :data="searchForm" layout="inline" class="search-form">
      <t-form-item label="用户名">
        <t-input v-model="searchForm.keyword" placeholder="请输入用户名" clearable />
      </t-form-item>
      <t-form-item label="状态">
        <t-select v-model="searchForm.status" placeholder="请选择" clearable>
          <t-option v-for="opt in statusOptions" :key="opt.value" :label="opt.label" :value="opt.value" />
        </t-select>
      </t-form-item>
      <t-form-item>
        <t-button theme="primary" @click="handleSearch">查询</t-button>
        <t-button variant="base" @click="handleReset">重置</t-button>
      </t-form-item>
    </t-form>

    <!-- 数据表格 -->
    <t-table
      row-key="id"
      :data="tableData"
      :columns="columns"
      :loading="loading"
      :pagination="pagination"
      @page-change="handlePageChange"
    >
      <template #status="{ row }">
        <t-tag :theme="row.status === 1 ? 'success' : 'danger'">
          {{ row.status === 1 ? '启用' : '禁用' }}
        </t-tag>
      </template>
      <template #op="{ row }">
        <t-button theme="primary" variant="text" size="small" @click="handleEdit(row)">编辑</t-button>
        <t-button theme="danger" variant="text" size="small" @click="handleDelete(row)">删除</t-button>
      </template>
    </t-table>
  </t-card>
</template>

<script setup lang="ts" name="UserList">
import { ref, reactive, onMounted } from 'vue'
import { MessagePlugin } from 'tdesign-vue-next'
import { fetchUserList, deleteUser, getUserStatusOptions } from './components/types/userLogic'
import type { IUserSearchParams, IUserItem } from './components/types/models'

// 搜索表单
const searchForm = reactive<IUserSearchParams>({
  keyword: '',
  status: undefined,
  page: 1,
  pageSize: 10,
})

// 表格数据与加载状态
const tableData = ref<IUserItem[]>([])
const loading = ref(false)

// 分页配置
const pagination = reactive({
  current: 1,
  pageSize: 10,
  total: 0,
})

// 状态选项
const statusOptions = ref<{ label: string; value: number }[]>([])

// 表格列定义
const columns = [
  { colKey: 'id', title: 'ID', width: 80 },
  { colKey: 'username', title: '用户名', ellipsis: true },
  { colKey: 'email', title: '邮箱', ellipsis: true },
  { colKey: 'status', title: '状态', width: 100 },
  { colKey: 'createTime', title: '创建时间', width: 180 },
  { colKey: 'op', title: '操作', width: 160, fixed: 'right' },
]

// 加载表格数据
const loadTableData = async () => {
  loading.value = true
  try {
    const res = await fetchUserList(searchForm)
    tableData.value = res.data.list
    pagination.total = res.data.total
  } finally {
    loading.value = false
  }
}

// 查询
const handleSearch = () => {
  pagination.current = 1
  loadTableData()
}

// 重置
const handleReset = () => {
  searchForm.keyword = ''
  searchForm.status = undefined
  handleSearch()
}

// 分页切换
const handlePageChange = (pageInfo: { current: number; pageSize: number }) => {
  pagination.current = pageInfo.current
  pagination.pageSize = pageInfo.pageSize
  searchForm.page = pageInfo.current
  searchForm.pageSize = pageInfo.pageSize
  loadTableData()
}

// 编辑
const handleEdit = (row: IUserItem) => {
  // 打开编辑弹窗或跳转编辑页
  console.log('edit user:', row.id)
}

// 删除
const handleDelete = async (row: IUserItem) => {
  try {
    await deleteUser(row.id)
    MessagePlugin.success('删除成功')
    loadTableData()
  } catch {
    MessagePlugin.error('删除失败')
  }
}

// 初始化
onMounted(async () => {
  statusOptions.value = getUserStatusOptions()
  await loadTableData()
})
</script>

<style scoped>
.search-form {
  margin-bottom: 16px;
}
</style>
```

## 关键要点

- **数据类型** 从 `components/types/models.ts` 导入，保持类型安全
- **业务逻辑函数** 从 `components/types/useXxx.ts` 导入，不在组件内直接写 API 调用
- **事件处理函数** 统一使用 `handle` 前缀命名
