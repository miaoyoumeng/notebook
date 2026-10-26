# mysql-ddl-writer

根据业务需求或 PRD 生成符合阿里巴巴规范的 MySQL 8.0 建表语句，输出可直接执行的 DDL。

## 使用场景

- 描述业务模块，需要设计表结构。
- 提供实体字段清单，需要生成 `CREATE TABLE` 语句。
- 按阿里巴巴 MySQL 规范复核现有建表语句。

不适用于已有数据库反向工程、ORM 模型导出、简单的 `ALTER TABLE` 加字段。

## 使用方式

在对话中描述业务需求即可触发，例如：

```text
帮我设计订单系统的表结构，包含订单、订单明细、支付记录，输出到 order.sql
```

未指定输出路径时，默认写入当前目录的 `<table_name>.md`。

## 目录结构

- `SKILL.md` — 技能指令，含流程、验证清单、危险信号。
- `references/alibaba.md` — 阿里巴巴 MySQL 数据库设计规范。
- `references/template.md` — DDL 输出模板，含建表模板、字段定义、数据生命周期、字段值流转。
- `scripts/validater.py` — DDL 校验脚本，用 sqlparse 解析建表语句，检查必填字段与字段类型。
- `evals/evals.json` — 测试用例与断言定义。
- `assets/` — 预留目录，当前为空。

## 校验 DDL

```bash
uv run python scripts/validater.py order.sql
```

脚本检查必填字段、字段类型、禁用类型、命名、注释与表选项。全部通过时退出码为 0，否则退出码为 1 并列出失败项。可一次传入多个文件。

依赖 `sqlparse`，已在 `lijie/pyproject.toml` 中声明。
