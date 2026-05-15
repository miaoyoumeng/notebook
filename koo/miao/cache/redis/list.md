### List（列表）

* 列表（list）类型是用来存储多个有序的字符串，一个列表最多可以存储2^32-1个元素。
* 内部编码：ziplist（压缩列表）、linkedlist（链表）
* 应用场景：消息队列，文章列表,
* 简单命令

```shell
LPUSH,LPUSHX,RPUSH,RPUSHX,LPOP,RPOP,RPOPLPUSH,LREM,LLEN,LINDEX,
LINSERT,LSET,LRANGE,LTRIM,BLPOP,BRPOP,BRPOPLPUSH
```

***list应用场景参考以下***：

* lpush+lpop=Stack（栈）
* lpush+rpop=Queue（队列）
* lpsh+ltrim=Capped Collection（有限集合）
* lpush+brpop=Message Queue（消息队列）

结构图如下：

![alt 图表](/images/redis/redis_list.png)