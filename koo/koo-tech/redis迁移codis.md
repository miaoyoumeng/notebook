# redis迁移codis

## maven依赖变化
### 删除原有的redis客户端依赖
```
  <dependency>
     <groupId>com.koolearn</groupId>
     <artifactId>koo-framework-redis-client</artifactId>
  </dependency>
```
### 增加codis依赖
```
<dependency>
 <groupId>com.koolearn</groupId>
 <artifactId>koo-framework-cache-client</artifactId>
 <version>2.0.0-SNAPSHOT</version>
</dependency>
```
特别注意
由于maven本身的依赖传递及冲突处理策略，对pom的任何修改都可能导致看似不相关的jar包变动。

下面给出两种解决方式：

一、通过修改pom（增加排除、强制增加版本等手段）使其他jar包版本跟之前保持一致。（此方案只需要测试redis相关的功能 大项目推荐使用）

二、任由jar包或版本变动，通过全面的测试避免发生问题

 

## spring xml 配置

连接池配置实例
```
<bean id="jedisPoolConfig" class="redis.clients.jedis.JedisPoolConfig">
 <property name="maxIdle" value="30"/>
 <property name="minIdle" value="10"/>
 <property name="maxTotal" value="300"/>
 <property name="maxWaitMillis" value="3000"/>
 <property name="softMinEvictableIdleTimeMillis" value="1800000"/>
 <property name="timeBetweenEvictionRunsMillis" value="-1"/>
</bean>

```

属性 | 说明
---|---
maxIdle|一个pool最多有多少个状态为idle
minIdle|一个pool最少有多少个状态为idle
maxTotal|最大实例总数
maxWaitMillis|  最大的等待时间，如果超过等待时间，则直接抛出JedisConnectionException
softMinEvictableIdleTimeMillis| 连接空闲的最小时间，达到此值后空闲链接将会被移除
timeBetweenEvictionRunsMillis| 每timeBetweenEvictionRunsMillis秒运行一次空闲

连接回收器  
序列化配置实例
```
<bean id="hessianRedisSerializer" class="com.koolearn.framework.redis.client.HessianRedisSerializer" />

```
客户端配置实例
```
<bean id="redisClient"
 class="com.koolearn.framework.redis.client.KooJedisClient"
 init-method="init" destroy-method="destroy">
 <property name="prefix" value="${业务唯一前缀}"/>
 <property name="config" ref="jedisPoolConfig"/>
 <property name="serializer" ref="hessianRedisSerializer"/>
 <property name="address" value="${zookeeper.cluster.address.codis}"/>
</bean>
```
属性 | 说明
---|---
prefix|业务线前缀
serializer|序列化方式
address| zookeeper 集群地址

# zookeeper各环境地址
环境 |地址
---|---
trunk | zookeeper.cluster.address.codis=zk1.trunk.koolearn.com:2181,zk2.trunk.koolearn.com:2181,zk3.trunk.koolearn.com:2181
neibu | zookeeper.cluster.address.codis=zk1.neibu.koolearn.com:2181,zk2.neibu.koolearn.com:2181,zk3.neibu.koolearn.com:2181
release |zookeeper.cluster.address.codis=zk1.release.koolearn.com:2181,zk2.release.koolearn.com:2181,zk3.release.koolearn.com:2181
product | zookeeper.cluster.address.codis=zk1-codis.cluster.koolearn.com:2181,zk2-codis.cluster.koolearn.com:2181,zk3-codis.cluster.koolearn.com:2181


