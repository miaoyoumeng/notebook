### # Codis

Codis 是由豌豆荚开源的产品，涉及组件众多，其中 ZooKeeper 存放路由表和代理节点元数据、分发 Codis-Config 的命令；Codis-
Config 是集成管理工具，有 Web 界面供使用；Codis-Proxy 是一个兼容 Redis 协议的无状态代理；Codis-Redis 基于
Redis 2.8 版本二次开发，加入 slot 支持，方便迁移数据。

![](/images/db/redis/db-redis-cluster-3.png)

优点：

  * 开发简单，对应用几乎透明
  * 性能比 Twemproxy 好
  * 有图形化界面，扩容容易，运维方便

缺点：

  * 代理依旧影响性能
  * 组件过多，需要很多机器资源
  * 修改了 Redis 代码，导致和官方无法同步，新特性跟进缓慢
  * 开发团队准备主推基于 Redis 改造的 reborndb