### Set（集合）

* 集合（set）类型也是用来保存多个的字符串元素，但是不允许重复元素
* 内部编码：intset（整数集合）、hashtable（哈希表）
```shell
SADD,SISMEMBER,SPOP,SRANDMEMBER,SREM,SMOVE,SCARD,SMEMBERS,
SSCAN,SINTER,SINTERSTORE,SUNION,SUNIONSTORE,SDIFF,SDIFFSTORE
```
* **注意点**：smembers和lrange、hgetall都属于比较重的命令，如果元素过多存在阻塞Redis的可能性，可以使用sscan来完成。
* 应用场景：用户标签,生成随机数抽奖、社交需求。

结构图如下：

![alt 图表](/images/redis/redis_set.png)