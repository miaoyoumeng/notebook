# PRD 分析示例

## 愿景墙示例

```
FOR [在线购物的消费者]
WHO [希望在一个平台完成商品浏览、下单、支付、售后全流程]
THE PRODUCT IS [一站式电商订单管理系统]
THAT [提供商品搜索、购物车、多支付方式、物流跟踪、退款售后等完整功能]
UNLIKE [分散在不同平台完成购买、支付、售后的割裂体验]
OUR SOLUTION [整合全链路流程，让用户在一个闭环内完成所有操作]
```

## 领域事件时间线

请参考通用模板：[references/template-event.md](template-event.md)

领域事件时间线中使用以下颜色约定：
- 🟠 橙色 = 领域事件（Domain Event），如 OrderCreated、PaymentCompleted
- 🔵 蓝色 = 命令（Command），如 提交订单、确认支付
- 🟡 黄色 = 角色/参与者（Actor），如 买家、商家、系统

## 聚合清单示例

```
### 订单聚合
- 聚合根：Order
- 实体：OrderItem、OrderAddress
- 值对象：OrderStatus、PaymentMethod、ShippingInfo
- 不变约束：订单金额 = 各订单项金额之和；订单状态流转不可逆

### 用户聚合
- 聚合根：User
- 实体：Address
- 值对象：UserRole、UserStatus
- 不变约束：每个用户最多 20 个收货地址

### 支付聚合
- 聚合根：Payment
- 实体：PaymentRecord
- 值对象：PaymentStatus、PaymentChannel
- 不变约束：支付金额必须等于订单应付金额
```

## 限界上下文划分示例

```
### 商品上下文
- 职责：商品信息管理、库存管理、分类与搜索
- 包含聚合：Product、Category、Inventory

### 订单上下文
- 职责：订单生命周期管理、购物车、售后
- 包含聚合：Order、Cart、Refund

### 支付上下文
- 职责：支付流程、支付渠道对接、对账
- 包含聚合：Payment、PaymentChannel

### 用户上下文
- 职责：用户身份、权限、个人资料
- 包含聚合：User、Role、Permission

### 物流上下文
- 职责：配送方式、物流跟踪、签收
- 包含聚合：Shipping、Tracking
```

## 领域间关系示例

```
用户上下文 ──→ 订单上下文     (数据依赖：订单归属用户)
订单上下文 ──→ 商品上下文     (数据依赖：订单引用商品和库存)
订单上下文 ──→ 支付上下文     (流程依赖：订单创建后触发支付)
支付上下文 ──→ 物流上下文     (事件驱动：支付成功后通知发货)
订单上下文 ──→ 物流上下文     (数据依赖：订单关联物流信息)
```

## 领域对象清单示例

| 领域模型 | 聚合 | 领域对象 | 领域类型 |
|---------|------|---------|---------|
| 订单模型 | 订单聚合 | Order | 聚合根 |
| 订单模型 | 订单聚合 | OrderItem | 实体 |
| 订单模型 | 订单聚合 | OrderAddress | 实体 |
| 订单模型 | 订单聚合 | OrderStatus | 值对象 |
| 订单模型 | 订单聚合 | PaymentMethod | 值对象 |
| 订单模型 | 订单聚合 | OrderCreated | 领域事件 |
| 订单模型 | 订单聚合 | OrderPaid | 领域事件 |
| 订单模型 | 订单聚合 | OrderCancelled | 领域事件 |
| 订单模型 | 订单聚合 | SubmitOrder | 命令 |
| 订单模型 | 订单聚合 | PayOrder | 命令 |
| 订单模型 | 订单聚合 | CancelOrder | 命令 |
| 用户模型 | 用户聚合 | User | 聚合根 |
| 用户模型 | 用户聚合 | Address | 实体 |
| 用户模型 | 用户聚合 | UserRole | 值对象 |
| 用户模型 | 用户聚合 | UserRegistered | 领域事件 |
| 用户模型 | 用户聚合 | RegisterUser | 命令 |

## 领域上下文边界示例

| 限界上下文 | 类型 | 包含聚合 | 职责描述 | 集成方式 |
|-----------|------|---------|---------|---------|
| 订单上下文 | 核心域 | Order, Cart, Refund | 订单生命周期管理、购物车、售后退款 | 发布 OrderCreated 领域事件、监听 PaymentCompleted |
| 商品上下文 | 核心域 | Product, Category, Inventory | 商品信息管理、库存管理、分类搜索 | 提供商品查询 API、监听 InventoryDeducted |
| 支付上下文 | 支撑域 | Payment, PaymentChannel | 支付流程、支付渠道对接、对账 | 监听 OrderCreated、发布 PaymentCompleted |
| 用户上下文 | 通用域 | User, Role, Permission | 用户身份、权限、个人资料 | 提供用户认证 API |
| 物流上下文 | 支撑域 | Shipping, Tracking | 配送方式、物流跟踪、签收 | 监听 PaymentCompleted、发布 ShipmentDelivered |

### 上下文映射关系示例

```
订单上下文 ──Customer-Supplier──→ 商品上下文
  说明：订单上下文作为 Customer，依赖商品上下文提供商品和库存信息

订单上下文 ──Customer-Supplier──→ 支付上下文
  说明：订单创建后触发支付流程，支付上下文按订单需求提供支付服务

支付上下文 ──ACL──→ 微信支付（外部系统）
  说明：通过防腐层隔离微信支付的 API 差异

订单上下文 ──Published Language──→ 物流上下文
  说明：通过 OrderPlacedIntegrationEvent 标准消息格式通知物流
```

## 领域状态机示例

### Order（订单）状态机

```
[Created] ──PayOrder──→ [Paid] ──ConfirmShipping──→ [Shipped] ──ConfirmReceipt──→ [Completed]
    │                      │
    │ CancelOrder          │ RequestRefund
    ▼                      ▼
[Cancelled]           [Refunding] ──ApproveRefund──→ [Refunded]
```

### 状态转换表

| 当前状态 | 触发命令 | 目标状态 | 守卫条件 | 产生领域事件 |
|---------|---------|---------|---------|------------|
| Created | PayOrder | Paid | 支付金额正确 | OrderPaid |
| Created | CancelOrder | Cancelled | 订单未发货 | OrderCancelled |
| Paid | RequestRefund | Refunding | 订单未发货或已签收 | RefundRequested |
| Paid | ConfirmShipping | Shipped | 仓库已备货 | OrderShipped |
| Shipped | ConfirmReceipt | Completed | 用户确认签收 | OrderCompleted |
| Refunding | ApproveRefund | Refunded | 审核通过 | RefundCompleted |

### 状态说明

| 状态 | 类型 | 说明 | 允许的操作 |
|-----|------|------|----------|
| Created | 初始状态 | 订单已创建，等待支付 | PayOrder, CancelOrder |
| Paid | 中间状态 | 订单已支付，等待发货 | ConfirmShipping, RequestRefund |
| Shipped | 中间状态 | 订单已发货，等待签收 | ConfirmReceipt |
| Completed | 终态 | 订单已完成 | RequestRefund（7天内） |
| Cancelled | 终态 | 订单已取消 | 无 |
| Refunding | 中间状态 | 退款审核中 | ApproveRefund, RejectRefund |
| Refunded | 终态 | 退款已完成 | 无 |
