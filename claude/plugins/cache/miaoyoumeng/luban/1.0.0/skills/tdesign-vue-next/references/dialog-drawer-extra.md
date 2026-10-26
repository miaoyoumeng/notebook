# 弹窗与抽屉（Dialog / Drawer）补充场景

## 适用场景

- 抽屉内展示表格详情。
- 全屏弹窗。
- 可拖拽弹窗。
- 层级冲突与命令式弹窗更新。

本文只覆盖抽屉详情、全屏/拖拽与层级问题。

## 抽屉详情

```vue
<template>
  <Table :data="tableData" :columns="columns" row-key="id">
    <template #operation="{ row }">
      <Button variant="text" @click="showDetail(row)">查看详情</Button>
    </template>
  </Table>

  <Drawer
    v-model:visible="drawerVisible"
    :header="`${currentRow?.name ?? ''} 的详情`"
    size="500px"
    :destroy-on-close="true"
  >
    <Descriptions v-if="currentRow" :items="detailItems" :column="1" />
  </Drawer>
</template>

<script setup lang="ts">
import { computed, ref } from "vue";
import { Button, Descriptions, Drawer, Table } from "tdesign-vue-next";
import type { DescriptionsProps } from "tdesign-vue-next";

interface RowData {
  id: number;
  name: string;
  email: string;
  phone: string;
  address: string;
}

const tableData = ref<RowData[]>([
  {
    id: 1,
    name: "张三",
    email: "zhang@example.com",
    phone: "13800138000",
    address: "北京市朝阳区",
  },
]);

const columns = computed(() => [
  { colKey: "name", title: "姓名" },
  { colKey: "email", title: "邮箱" },
  { colKey: "operation", title: "操作", width: 120 },
]);

const drawerVisible = ref(false);
const currentRow = ref<RowData | null>(null);

const detailItems = computed<DescriptionsProps["items"]>(() => {
  if (!currentRow.value) return [];
  return [
    { label: "姓名", content: currentRow.value.name },
    { label: "邮箱", content: currentRow.value.email },
    { label: "电话", content: currentRow.value.phone },
    { label: "地址", content: currentRow.value.address },
  ];
});

const showDetail = (row: RowData) => {
  currentRow.value = row;
  drawerVisible.value = true;
};
</script>
```

抽屉设置 `destroy-on-close`，避免切换行时保留上一条详情。

## 全屏与拖拽

```vue
<template>
  <Space>
    <Button @click="visible = true">可拖拽弹窗</Button>
    <Button @click="fullscreenVisible = true">全屏弹窗</Button>
  </Space>

  <Dialog v-model:visible="visible" header="可拖拽弹窗" draggable :modal="false">
    <p>拖拽标题栏移动弹窗</p>
  </Dialog>

  <Dialog v-model:visible="fullscreenVisible" header="全屏弹窗" :fullscreen="isFullscreen">
    <template #header>
      <div class="custom-header">
        <span>全屏弹窗</span>
        <Button variant="text" @click="isFullscreen = !isFullscreen">
          {{ isFullscreen ? "退出全屏" : "全屏" }}
        </Button>
      </div>
    </template>
    <p>点击标题栏按钮切换全屏</p>
  </Dialog>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { Button, Dialog, Space } from "tdesign-vue-next";

const visible = ref(false);
const fullscreenVisible = ref(false);
const isFullscreen = ref(false);
</script>

<style scoped>
.custom-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
}
</style>
```

拖拽弹窗设置 `draggable` 与 `:modal="false"`，否则遮罩层会拦截拖拽。

## 层级与更新

命令式弹窗的 `z-index` 冲突时，为弹窗设置 `z-index`，或在 `ConfigProvider` 中统一配置层级。

```ts
const dialog = DialogPlugin({ body: "初始内容" });
dialog.update({ body: "更新后的内容" });
```

命令式弹窗使用返回实例的 `update()` 更新内容，使用 `hide()` 关闭，使用 `destroy()` 释放。

## 常见问题

### 内层弹窗被外层遮挡

内层弹窗设置 `:attach="false"`，挂载到外层弹窗内部；或为内层设置更高的 `z-index`。

### 抽屉关闭后数据仍保留

设置 `destroy-on-close`，或在关闭回调中清空当前行数据。
