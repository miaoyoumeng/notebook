# TDesign Steps 步骤条

步骤条组件用于展示业务流程或操作任务的步骤顺序，支持水平/垂直布局、不同状态和点击切换。

## Props

### Steps Props

| 属性名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| current | string/number | - | 当前步骤（v-model） |
| layout | string | horizontal | 布局：`horizontal` / `vertical` |
| readonly | boolean | false | 是否只读（禁止点击切换） |
| separator | string | line | 分隔符类型：`line` / `dashed` / `arrow` |
| status | string | process | 整体状态：`default` / `process` / `finish` / `error` |
| theme | string | default | 主题：`default` / `dot` |

### StepItem Props

| 属性名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| content | string | - | 步骤描述 |
| icon | RenderFunction | - | 自定义图标 |
| status | string | - | 步骤状态：`default` / `process` / `finish` / `error` |
| title | string | - | 步骤标题 |
| value | string/number | - | 步骤唯一标识 |

## Events

| 事件名 | 参数 | 说明 |
|--------|------|------|
| change | `(current: string | number) => void` | 步骤切换时触发 |

## Slots

| 插槽名 | 说明 |
|--------|------|
| default | StepItem 列表 |
| icon | 自定义图标（StepItem 内） |

## 示例

```vue
<template>
  <Space direction="vertical" :size="24">
    <!-- 基础用法（水平） -->
    <Steps v-model="current1" @change="handleChange">
      <StepItem title="步骤一" content="创建订单" />
      <StepItem title="步骤二" content="支付订单" />
      <StepItem title="步骤三" content="完成订单" />
    </Steps>

    <!-- 垂直布局 -->
    <Steps v-model="current2" layout="vertical">
      <StepItem title="注册账号" content="填写基本信息" />
      <StepItem title="完善资料" content="上传头像和简介" />
      <StepItem title="开始使用" content="探索更多功能" />
    </Steps>

    <!-- 不同状态 -->
    <Steps v-model="current3">
      <StepItem title="已完成" status="finish" content="已通过审核" />
      <StepItem title="进行中" status="process" content="正在处理中" />
      <StepItem title="默认" content="等待处理" />
      <StepItem title="异常" status="error" content="处理失败" />
    </Steps>

    <!-- 点状主题 -->
    <Steps v-model="current4" theme="dot">
      <StepItem title="步骤一" content="点状样式" />
      <StepItem title="步骤二" content="简洁展示" />
      <StepItem title="步骤三" content="适合多步" />
    </Steps>

    <!-- 带图标 -->
    <Steps v-model="current5">
      <StepItem title="账号" content="注册账号" :icon="() => '👤'" />
      <StepItem title="验证" content="手机验证" :icon="() => '📱'" />
      <StepItem title="完成" content="注册成功" :icon="() => '✅'" />
    </Steps>

    <!-- 只读模式 -->
    <Steps v-model="current6" readonly>
      <StepItem title="步骤一" status="finish" />
      <StepItem title="步骤二" status="finish" />
      <StepItem title="步骤三" status="process" />
      <StepItem title="步骤四" />
    </Steps>

    <!-- 自定义内容 -->
    <Steps v-model="current7" layout="vertical">
      <StepItem title="下单" status="finish">
        <template #content>
          <div>
            <p>订单号：20260810001</p>
            <p>时间：2026-08-10 10:00</p>
          </div>
        </template>
      </StepItem>
      <StepItem title="支付" status="process">
        <template #content>
          <p>正在等待支付...</p>
        </template>
      </StepItem>
      <StepItem title="发货">
        <template #content>
          <p>支付完成后发货</p>
        </template>
      </StepItem>
    </Steps>
  </Space>
</template>
<script setup lang="ts" name="StepsDemo">
import { ref } from 'vue';
import { Space, StepItem, Steps } from 'tdesign-vue-next';

const current1 = ref(0);
const current2 = ref(0);
const current3 = ref(1);
const current4 = ref(0);
const current5 = ref(0);
const current6 = ref(2);
const current7 = ref(1);

const handleChange = (current: string | number) => {
  console.log('步骤切换到:', current);
};
</script>
<style scoped>
</style>
```
