### 锁


####  锁的类型

InnoDB存储引擎有两种行级锁

* 共享锁（<font color="red">S</font>hare Locks，记为S锁），允许事务读取一行数据。
* 排他锁（e<font color="red">X</font>clusive Locks，记为X锁），修改数据时加X锁，允许事务修改一行数据。

当前锁\请求锁|X|S
:-:|:-:|:-:
None|兼容|兼容
X|不兼容|不兼容
S|不兼容|兼容


可以看到，一旦写数据的任务没有完成，数据是不能被其他任务读取的，这对并发度有较大的影响。
对应到数据库，可以理解为，写事务没有提交，读相关数据的select也会被阻塞。


有没有可能，进一步提高并发呢？
即使写任务没有完成，其他读任务也可能并发，这就引出了数据多版本（MVCC)。

InnoDB还有一种表级别锁，意向锁|

* 意向共享锁 IS，表示事务想要获取表中某几行的共享锁。
* 意向排他锁 IX，表示事务想要获取表中某几行的排他锁。

InnoDB的意向锁主要用户多粒度的锁并存的情况。比如事务A要在一个表上加S锁，如果表中的一行已被事务B加了X锁，那么该锁的申请也应被阻塞。如果表中的数据很多，逐行检查锁标志的开销将很大，系统的性能将会受到影响。为了解决这个问题，可以在表级上引入新的锁类型来表示其所属行的加锁情况，这就引出了“意向锁”的概念。举个例子，如果表中记录1亿，事务A把其中有几条记录上了行锁了，这时事务B需要给这个表加表级锁，如果没有意向锁的话，那就要去表中查找这一亿条记录是否上锁了。如果存在意向锁，那么假如事务Ａ在更新一条记录之前，先加意向锁，再加Ｘ锁，事务B先检查该表上是否存在意向锁，存在的意向锁是否与自己准备加的锁冲突，如果有冲突，则等待直到事务Ａ释放，而无须逐条记录去检测。事务Ｂ更新表时，其实无须知道到底哪一行被锁了，它只要知道反正有一行被锁了就行了。

说白了意向锁的主要作用是处理行锁和表锁之间的矛盾，能够显示“某个事务正在某一行上持有了锁，或者准备去持有锁”。



当前锁\请求锁|X|IX|S|IS
:-:|:-:|:-:|:-:|:-:
X|不兼容|不兼容|不兼容|不兼容
IX|不兼容|兼容|不兼容|兼容
S|不兼容|不兼容|兼容|兼容
IS|不兼容|兼容|兼容|兼容




	Lock wait timeout exceeded; try restarting transaction的异常

**innodb_trx表结构**

	trx_id：唯一事务id号，只读事务和非锁事务是不会创建id的。
	trx_weight：事务的权重，代表修改的行数（不一定准确）和被事务锁住的行数。为了解决死锁，innodb会选择一个权重最小的事务来当做牺牲品进行回滚。已经被更改的非交易型表的事务权重比其他事务高，即使改变的行和锁住的行比其他事务低。
	trx_state：事务的执行状态，值一般分为：RUNNING, LOCK WAIT, ROLLING BACK, and COMMITTING.
	trx_started：事务的开始时间
	trx_requested_lock_id:如果trx_state是lockwait,显示事务当前等待锁的id，不是则为空。想要获取锁的信息，根据该lock_id，以innodb_locks表中lock_id列匹配条件进行查询，获取相关信息。
	trx_wait_started：如果trx_state是lockwait,该值代表事务开始等待锁的时间；否则为空。
	trx_mysql_thread_id：mysql线程id。想要获取该线程的信息，根据该thread_id，以INFORMATION_SCHEMA.PROCESSLIST表的id列为匹配条件进行查询。
	trx_query：事务正在执行的sql语句。
	trx_operation_state：事务当前的操作状态，没有则为空。
	trx_tables_in_use：事务在处理当前sql语句使用innodb引擎表的数量。
	trx_tables_locked：当前sql语句有行锁的innodb表的数量。（因为只是行锁，不是表锁，表仍然可以被多个事务读和写）
	trx_lock_structs：事务保留锁的数量。
	trx_lock_memory_bytes：在内存中事务索结构占得空间大小。
	trx_rows_locked：事务行锁最准确的数量。这个值可能包括对于事务在物理上存在，实际不可见的删除标记的行。
	trx_rows_modified：事务修改和插入的行数
	trx_concurrency_tickets：该值代表当前事务在被清掉之前可以多少工作，由 innodb_concurrency_tickets系统变量值指定。
	trx_isolation_level：事务隔离等级。
	trx_unique_checks：当前事务唯一性检查启用还是禁用。当批量数据导入时，这个参数是关闭的。
	trx_foreign_key_checks：当前事务的外键坚持是启用还是禁用。当批量数据导入时，这个参数是关闭的。
	trx_last_foreign_key_error：最新一个外键错误信息，没有则为空。
	trx_adaptive_hash_latched：自适应哈希索引是否被当前事务阻塞。当自适应哈希索引查找系统分区，一个单独的事务不会阻塞全部的自适应hash索引。自适应hash索引分区通过 innodb_adaptive_hash_index_parts参数控制，默认值为8。
	trx_adaptive_hash_timeout：是否为了自适应hash索引立即放弃查询锁，或者通过调用mysql函数保留它。当没有自适应hash索引冲突，该值为0并且语句保持锁直到结束。在冲突过程中，该值被计数为0，每句查询完之后立即释放门闩。当自适应hash索引查询系统被分区（由 innodb_adaptive_hash_index_parts参数控制），值保持为0。
	trx_is_read_only：值为1表示事务是read only。
	trx_autocommit_non_locking：值为1表示事务是一个select语句，该语句没有使用for update或者shared mode锁，并且执行开启了autocommit，因此事务只包含一个语句。当TRX_AUTOCOMMIT_NON_LOCKING和TRX_IS_READ_ONLY同时为1，innodb通过降低事务开销和改变表数据库来优化事务。

**innodb_locks表结构**
	lock_id: 锁Id
	lock_trx_id: 事务id
	lock_mode: 锁模式
	lock_type: 锁类型，表锁还是行锁
	lock_table: 要加锁的表
	lock_index: 要加锁的索引
	lock_space: 锁对象的space id
	lock_page: 若是表锁，那么该值为null
	lock_rec: 事务锁定行的数量，若是表锁，那么该值为null
	lock_data: 事务锁住的记录主键值，若是表锁，那么该值为null

**innodb_lock_waits**

	requesting_trx_id: 请求事务id
	requested_lock_id: 请求锁id
	blocking_trx_id: 阻塞事务id
	blocking_lock_id: 阻塞锁id

```sql
select trx_id,trx_state,trx_started,trx_requested_lock_id,trx_tables_in_use, trx_tables_locked, trx_isolation_level,trx_operation_state from information_schema.innodb_trx;

select lock_id, lock_trx_id, lock_mode,lock_type,lock_table, lock_index,lock_data from information_schema.innodb_locks;

select * from information_schema.innodb_lock_waits;
```



