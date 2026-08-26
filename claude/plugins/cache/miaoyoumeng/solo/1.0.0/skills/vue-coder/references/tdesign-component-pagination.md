# TDesign Pagination 分页

分页组件用于数据列表的分页导航，支持页码跳转、每页条数切换、总数显示等功能。

## Props

| 属性名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| current | number | 1 | 当前页码（v-model） |
| default-current | number | 1 | 默认当前页 |
| default-page-size | number | 10 | 默认每页条数 |
| disabled | boolean | false | 是否禁用 |
| folded-max-page-btn | number | 5 | 折叠时的最大页码按钮数 |
| jump | boolean | false | 是否显示跳转输入框 |
| page-size | number | 10 | 每页条数（v-model） |
| page-size-options | number[] | [10, 20, 50, 100] | 每页条数选项 |
| show-page-size | boolean | false | 是否显示每页条数选择器 |
| show-sizer | boolean | false | 是否显示条数选择器（旧版，已废弃） |
| simple | boolean | false | 是否使用简洁模式 |
| size | string | medium | 尺寸：`small` / `medium` / `large` |
| theme | string | page | 分页主题 |
| total | number | 0 | 数据总条数 |
| total-content | boolean | true | 是否显示总数内容 |
| show-jumper | boolean | false | 是否显示跳转 |
| show-size | boolean | false | 是否显示条数选择器 |

## Events

| 事件名 | 参数 | 说明 |
|--------|------|------|
| change | `(pageInfo: { current, previous, pageSize }) => void` | 页码或条数变化时触发 |
| current-change | `(current: number) => void` | 当前页码变化时触发 |
| page-size-change | `(pageSize: number) => void` | 每页条数变化时触发 |

## Slots

| 插槽名 | 说明 |
|--------|------|
| default | 自定义分页内容 |

## 示例

```vue
<template>
  <Space direction="vertical" :size="16">
    <!-- 基础用法 -->
    <Pagination :total="100" :current="1" />

    <!-- 显示总数 -->
    <Pagination :total="250" :current="1" :total-content="true" />

    <!-- 带页码跳转 -->
    <Pagination :total="500" :current="current1" show-jumper />

    <!-- 带每页条数选择 -->
    <Pagination
      :total="500"
      :current="current2"
      :page-size="pageSize2"
      show-size
      :page-size-options="[10, 20, 50, 100]"
    />

    <!-- 完整功能 -->
    <Pagination
      v-model:current="current3"
      v-model:page-size="pageSize3"
      :total="1000"
      show-jumper
      show-size
      :page-size-options="[10, 20, 50, 100]"
      @change="handleChange"
    />

    <!-- 简洁模式 -->
    <Pagination :total="200" :current="current4" simple />

    <!-- 受控模式 -->
    <Pagination
      :total="300"
      :current="controlledCurrent"
      :page-size="controlledPageSize"
      @current-change="handleCurrentChange"
      @page-size-change="handlePageSizeChange"
    />

    <!-- 禁用状态 -->
    <Pagination :total="100" :current="1" disabled />

    <!-- 自定义总内容 -->
    <Pagination :total="88" :total-content="true">
      <template #default>
        <span>共 {{ total }} 条</span>
      </template>
    </Pagination>
  </Space>
</template>
<script setup lang="ts" name="PaginationDemo">
import { ref } from 'vue';
import { Pagination, Space } from 'tdesign-vue-next';

const current1 = ref(1);
const current2 = ref(1);
const pageSize2 = ref(10);
const current3 = ref(1);
const pageSize3 = ref(20);
const current4 = ref(1);
const controlledCurrent = ref(3);
const controlledPageSize = ref(20);
const total = ref(88);

const handleChange = (pageInfo: { current: number; previous: number; pageSize: number }) => {
  console.log('分页变化:', pageInfo);
};

const handleCurrentChange = (current: number) => {
  controlledCurrent.value = current;
  console.log('当前页:', current);
};

const handlePageSizeChange = (pageSize: number) => {
  controlledPageSize.value = pageSize;
  controlledCurrent.value = 1; // 切换条数时回到第一页
  console.log('每页条数:', pageSize);
};
</script>
<style scoped>
</style>
```
