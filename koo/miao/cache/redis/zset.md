### 有序集合（zset）

* 已排序的字符串集合，同时元素不能重复
* 简单格式举例：zadd key score member [score member ...]，zrank key member
* 底层内部编码：ziplist（压缩列表）、skiplist（跳跃表）
* 应用场景：排行榜，社交需求（如用户点赞）。