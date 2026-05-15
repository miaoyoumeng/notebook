## Twemproxy

多个同构 Twemproxy（配置相同）同时工作，接受客户端的请求，根据 hash 算法，转发给对应的 Redis。

Twemproxy 方案比较成熟了，但是效果并不是很理想。一方面是定位问题比较困难，另一方面是它对自动剔除节点的支持不是很友好。

![](/images/db/redis/db-redis-cluster-2.png)

优点：

  * 开发简单，对应用几乎透明
  * 历史悠久，方案成熟

缺点：

  * 代理影响性能
  * LVS 和 Twemproxy 会有节点性能瓶颈
  * Redis 扩容非常麻烦
  * Twitter 内部已放弃使用该方案，新使用的架构未开源