## Introduction

#### 常用命令


###### 1. 创建数据库

```sql
CREATE DATABASE  IF NOT EXISTS `${database_name}`  DEFAULT CHARACTER SET utf8mb4;
```

###### 2. 导出

* 如果只需要导出表结构而不包括数据，可以使用--no-data选项。命令如下：

```sql
mysqldump -u root -p  --no-data db_sso > /tmp/db_sso.sql
```