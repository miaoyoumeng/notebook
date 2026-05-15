### Hash（哈希）

* 哈希类型是指v（值）本身又是一个键值对（k-v）结构
* 内部编码：ziplist（压缩列表） 、hashtable（哈希表）
* **注意点**：如果开发使用hgetall，哈希元素比较多的话，可能导致Redis阻塞，可以使用hscan。而如果只是获取部分field，建议使用hmget。

**字符串和哈希类型对比如下图**：

![alt 图表](/images/redis/redis_hash.png)


* 应用场景：缓存实体对象等。