## Redis ZSET（有序集合）

> Redis 有序集合和集合一样也是 string 类型元素的集合,且不允许重复的成员。不同的是每个元素都会关联一个 double 类型的分数。redis正是通过分数来为集合中的成员进行从小到大的排序。

* 已排序的字符串集合，同时元素不能重复
* 底层内部编码：ziplist（压缩列表）、skiplist（跳跃表）

#### 数据结构

有序集合的成员是唯一的, 但分数(score)却可以重复。有序集合是通过两种数据结构实现：

1. **压缩列表(ziplist)** : ziplist是为了提高存储效率而设计的一种特殊编码的双向链表。它可以存储字符串或者整数，存储整数时是采用整数的二进制而不是字符串形式存储。它能在O(1)的时间复杂度下完成list两端的push和pop操作。但是因为每次操作都需要重新分配ziplist的内存，所以实际复杂度和ziplist的内存使用量相关
2. **跳跃表（zSkiplist)** : 跳跃表的性能可以保证在查找，删除，添加等操作的时候在对数期望时间内完成，这个性能是可以和平衡树来相比较的，而且在实现方面比平衡树要优雅，这是采用跳跃表的主要原因。跳跃表的复杂度是O(log(n))。

#### 命令使用

命令| 简述| 使用  
---|---|---  
ZADD| 向有序集合添加一个或多个成员，或者更新已存在成员的分数| ZADD zset-key 178 member1  
ZRANGE| 根据元素在有序集合中所处的位置，从有序集合中获取多个元素| ZRANGE zset-key 0-1 withccores  
ZREM| 如果给定元素成员存在于有序集合中，那么就移除这个元素| ZREM zset-key member1 
ZCARD | 获取有序集合的成员数 | ZCARD zset-key
ZCOUNT | 计算在有序集合中指定区间分数的成员数 | ZCOUNT key min max
ZINCRBY | 有序集合中对指定成员的分数加上增量 increment | ZINCRBY key increment member
ZINTERSTORE | 计算给定的一个或多个有序集的交集并将结果集存储在新的有序集合 key 中 | ZINTERSTORE destination numkeys key [key ...] [WEIGHTS weight [weight ...]] [AGGREGATE SUM|MIN|MAX]
ZLEXCOUNT | 在有序集合中计算指定字典区间内成员数量 | ZLEXCOUNT key min max
ZRANGEBYLEX | 通过字典区间返回有序集合的成员 | ZRANGEBYLEX key min max [LIMIT offset count]
ZRANGEBYSCORE | 通过分数返回有序集合指定区间内的成员 | ZRANGEBYSCORE key min max [WITHSCORES] [LIMIT offset count]
ZRANK | 返回有序集合中指定成员的索引 | ZRANK key member
ZREMRANGEBYLEX | 移除有序集合中给定的字典区间的所有成员 | ZREMRANGEBYLEX key min max
ZREMRANGEBYRANK | 移除有序集合中给定的排名区间的所有成员 | ZREMRANGEBYRANK key start stop
ZREMRANGEBYSCORE | 移除有序集合中给定的分数区间的所有成员 | ZREMRANGEBYSCORE key min max
ZREVRANGE | 返回有序集中指定区间内的成员，通过索引，分数从高到底 | ZREVRANGE key start stop [WITHSCORES]
ZREVRANGEBYSCORE | 返回有序集中指定分数区间内的成员，分数从高到低排序 | ZREVRANGEBYSCORE key max min [WITHSCORES] [LIMIT offset count]
ZREVRANK | 返回有序集合中指定成员的排名，有序集成员按分数值递减(从大到小)排序 | ZREVRANK key member
ZSCORE | 返回有序集中，成员的分数值 | ZSCORE key member
ZUNIONSTORE | 计算一个或多个有序集的并集，并存储在新的 key 中 | ZUNIONSTORE destination numkeys key [key ...] [WEIGHTS weight [weight ...]] [AGGREGATE SUM|MIN|MAX]
ZSCAN | 迭代有序集合中的元素（包括元素成员和元素分值）|ZSCAN key cursor [MATCH pattern] [COUNT count]


#### 应用场景

* 应用场景：排行榜，社交需求（如用户点赞）。





