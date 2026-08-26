# <table_name>

描述这张表对应的<系统业务领域>

## DDL 文件头部

```sql
-- ============================================================
-- PRD DDL: <PRD 文件名>
-- 生成时间: <YYYY-MM-DD>
-- 设计规范: 阿里巴巴 MySQL 数据库设计规范
-- ============================================================
```

## CREATE TABLE 模板

```sql
-- 表名：xxx
-- 描述：xxx
CREATE TABLE IF NOT EXISTS `table_name` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `field_name` VARCHAR(64) NOT NULL DEFAULT '' COMMENT '字段说明',
  `status` TINYINT NOT NULL DEFAULT 0 COMMENT '状态: 0-默认, 1-启用, 2-禁用',
  `is_deleted` TINYINT NOT NULL DEFAULT 0 COMMENT '软删除: 0-未删除, 1-已删除',
  `gmt_create` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `gmt_modified` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_field_name` (`field_name`),
  KEY `idx_status_created` (`status`, `gmt_create`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='表说明';
```

## 字段定义规范

与 CREATE TABLE 模板中的字段一一对应，顺序一致：

| 字段名 | 字段类型 | 长度 | 允许为空 | 是否主键 | 说明 |
|--------|---------|------|---------|---------|------|
| id | BIGINT UNSIGNED | 20 | NO | 是 | 统一自增主键 |
| field_name | VARCHAR | 64 | NO | 否 | 通用业务字段示例 |
| status | TINYINT | 1 | NO | 否 | 状态/枚举字段，COMMENT 说明各枚举值含义 |
| is_deleted | TINYINT | 1 | NO | 否 | 软删除标志：0-未删除，1-已删除 |
| gmt_create | DATETIME | - | NO | 否 | 创建时间，默认 CURRENT_TIMESTAMP |
| gmt_modified | DATETIME | - | NO | 否 | 更新时间，默认 CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP |

**索引命名规范**（索引命名与字段定义同样重要，必须严格遵守）：

- 唯一索引：`uk_字段名`，如 `uk_<field name>`
- 普通索引：`idx_字段名`，如 `idx_<field name>`
- 联合索引：`idx_字段1_字段2`，如 `idx_<field name 1>_<field name 2>`

## 数据生命周期

> 在生成 DDL 时，根据业务需求补充以下三个维度的说明。

| 维度 | 角色 |说明内容 | 示例 |
|------|------|---------|------|
| **创建场景** | xx 用户|数据在什么业务操作下被插入 | 用户下单、管理员手动创建、系统定时任务生成 |
| **修改场景** | xx 用户|大部分字段在什么操作下被更新 | 用户支付后更新状态和金额、管理员审核后更新审批字段 |
| **删除场景** | xx 用户| 数据在什么条件下被软删除 | 用户注销账号、订单超时取消、数据过期归档 |

角色：如管理员，游客，c端用户，运营人员等，具体看 prd 内容。

## 字段值流转

> 仅针对取值有限（不超过 10 种状态）的枚举字段，如 `status`、`state` 、`type`等。
> 无法限制取值数量的字段（如 `name`、`content`）无需在此处说明。

### `<field_name>` — <字段业务描述>

| 枚举值 | 业务含义 | 触发条件 | 可流转至哪些状态 | 不可流转至哪些状态 |
|--------|---------|---------|----------------|------------------|
| 0 | <状态说明> | <何时进入此状态> | <可流转的目标状态值> | <禁止流转的目标状态值> |
| 1 | <状态说明> | <何时进入此状态> | <可流转的目标状态值> | <禁止流转的目标状态值> |
| ... | ... | ... | ... | ... |

### 示例：order 表 status 字段

| 枚举值 | 业务含义 | 触发条件 | 可流转至哪些状态 | 不可流转至哪些状态 |
|--------|---------|---------|----------------|------------------|
| 0 | 待支付 | 用户下单创建订单 | 1, 2 | - |
| 1 | 已支付/待发货 | 用户完成支付回调 | 3, 5 | 0, 2 |
| 2 | 已取消 | 用户主动取消或超时未支付 | - | 0, 1 |
| 3 | 已发货/待收货 | 商家发货操作 | 4, 5 | 0, 2 |
| 4 | 已完成/已签收 | 用户确认收货 | - | 0, 1, 2, 3 |
| 5 | 已退款/售后 | 售后退款流程 | - | 0, 1, 2, 3 |





