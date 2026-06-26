# 领域事件时间线工作流

本文件提供从 PRD 中提取领域事件时间线和领域模型的详细执行步骤。

## Step 1：领域事件提取 — "从 PRD 中提取所有领域事件"

### 执行指令

从 PRD 文档的功能描述、用户故事、业务流程中提取所有会发生的领域事件。

**规则：**
- 使用"主语+过去式"命名（OrderCreated ✓ / Create Order ✗）
- 只关注业务语义，不关注技术实现
- 正常流程和异常流程（取消、退款、超时）都要提取
- 外部系统回调产生的领域事件也要包含

### 检查点

- [ ] 领域事件是否全部用过去式命名？
- [ ] 是否包含异常流程领域事件（取消/退款/超时）？
- [ ] 是否遗漏外部系统领域事件（支付回调、短信通知、物流更新）？

### 产出示例

```
领域事件清单：
  OrderCreated      PaymentCompleted    OrderShipped
  OrderCancelled    RefundRequested     RefundCompleted
  InventoryDeducted PointsAccumulated   NotificationSent
```

## Step 2：时间线排序 — "按发生顺序排列"

### 执行指令

将 Step 1 提取的领域事件按发生先后排列，区分主流程和异常流程。

1. 主流程领域事件排顶部，异常流程排底部
2. 按时间先后从左到右排列
3. 识别分支点（如"支付成功" vs "支付超时"），用线条连接

### 检查点

- [ ] 主线和分支清晰可区分
- [ ] 异常流程没有遗漏
- [ ] 时间约束领域事件明确标记（如 ⏱ 30min 未支付自动取消）

### 产出示例

```
时间线：
  OrderCreated → InventoryDeducted → PaymentCompleted → PointsAccumulated → OrderShipped
                                                ↳ PaymentTimeout → OrderCancelled（⏱ 30min）
```

## Step 3：关键领域事件标记 — "找转折点"

### 执行指令

从时间线中标记关键领域事件（状态转折点），并标注时间约束。

### 关键领域事件判断标准

| 领域事件类型 | 是否关键 | 原因 |
|---------|:------:|------|
| OrderCreated | ★ | 业务流程起点 |
| InventoryDeducted | ★ | 影响能否下单 |
| PaymentCompleted | ★ | 核心状态变更 |
| NotificationSent | | 辅助领域事件，不影响主干 |

### 产出示例

```
★ 关键领域事件列表：
  1. OrderCreated（触发：用户点击"下单"）
  2. InventoryDeducted（触发：订单创建成功后）
  3. PaymentCompleted（触发：用户支付 / 超时自动取消 ⏱ 30min）
  4. OrderShipped（触发：仓库确认发货）
  5. RefundCompleted（触发：退货审核通过）
```

## Step 4：命令与角色 — "谁触发的"

### 执行指令

为每个领域事件标注触发命令、触发角色、外部系统。

### 分类模板

| 领域事件（橙） | 命令（蓝） | 角色（黄） | 外部系统（粉） |
|-----------|-----------|-----------|--------------|
| OrderCreated | SubmitOrder | 买家 | [无] |
| PaymentCompleted | PayOrder | 买家 | 微信支付 |
| InventoryDeducted | DeductInventory | 系统（自动） | [无] |
| OrderShipped | ConfirmShipping | 仓库管理员 | WMS 仓库系统 |

### 检查点

- [ ] 每个领域事件都有对应的命令？
- [ ] 系统自动触发的领域事件也标了角色（系统/定时器/消息）？
- [ ] 外部系统（支付/短信/物流）都标注了？

## Step 5：聚合发现 — "分组+边界"

### 执行指令

将相关的领域事件+命令+实体归组，每组选定一个聚合根。

### 聚合根选择决策

```
对于每个候选实体，回答：
  1. 是否有独立的生命周期？（创建→修改→删除）
  2. 是否有全局唯一 ID？
  3. 业务流程中是否作为"主语"出现？

  如果 3 个问题都回答"是" → 聚合根
  如果 < 3 个"是" → 挂到其他聚合根下
```

### 聚合设计检查清单

- [ ] 每个聚合 ≤ 5 个实体
- [ ] 聚合间只有 ID 引用，无对象引用
- [ ] 每个聚合有明确的"一事务一聚合"边界
- [ ] 没有共享实体在多个聚合中出现

### 检查点

- [ ] 每个聚合根是否都有独立的全局唯一 ID？
- [ ] 聚合内的实体是否都通过聚合根访问？
- [ ] 聚合间是否只通过 ID 引用，没有直接对象引用？
- [ ] 每个聚合是否都能在一个事务内完成修改？
- [ ] 是否所有领域事件都归属到对应的聚合？
- [ ] 聚合命名是否使用业务含义清晰的名词？

### 产出示例

```
聚合 1：订单聚合
  聚合根：Order
  实体：OrderItem（内嵌）
  领域事件：OrderCreated、OrderPaid、OrderCancelled
  命令：SubmitOrder、PayOrder、CancelOrder

聚合 2：库存聚合
  聚合根：Inventory
  实体：InventoryLog
  领域事件：InventoryDeducted、InventoryReleased
  命令：DeductInventory、ReleaseInventory

聚合间关系：
  Order → Inventory（通过 inventoryId 引用）
```

## Step 6：限界上下文划分 — "划清边界"

### 执行指令

按聚合间耦合度分组，形成限界上下文（BC）。

### BC 划分决策树

```
两个聚合是否需要放在同一 BC？

├── 它们是否有紧密的同步事务需求？
│   ├── 是 → 同一 BC
│   └── 否 → 继续判断
│
├── 它们是否共享相同的领域概念含义？
│   ├── 是（如：Order 的 Product 和 Inventory 的 Product 含义相同）→ 可能同一 BC
│   └── 否（如：Order 的 Customer 是购买者，CRM 的 Customer 是潜在客户）→ 不同 BC
│
└── 它们是否由同一团队维护？
    ├── 是 → 可能同一 BC
    └── 否 → 不同 BC
```

### 检查点

- [ ] 每个限界上下文是否有明确的业务职责？
- [ ] 上下文内的聚合是否具有高内聚性？
- [ ] 上下文之间是否通过领域事件或 API 通信，没有直接数据库共享？
- [ ] 每个上下文是否都标注了类型（核心域/支撑域/通用域）？
- [ ] 上下文之间的映射关系是否明确（Partnership/Customer-Supplier/ACL 等）？
- [ ] 外部系统是否都通过 ACL 或 OHS 模式集成？
- [ ] 是否识别了跨上下文的集成领域事件？

### 产出示例

```
限界上下文：
  BC-1: 订单上下文（核心域）
    聚合：Order、Payment
    集成：发布 OrderPlacedIntegrationEvent → BC-2

  BC-2: 库存上下文（支撑域）
    聚合：Inventory
    集成：监听 OrderPlacedIntegrationEvent

上下文映射：
  Order BC ──Customer-Supplier──→ Inventory BC
  Order BC ──ACL──→ 微信支付（外部系统）
```
