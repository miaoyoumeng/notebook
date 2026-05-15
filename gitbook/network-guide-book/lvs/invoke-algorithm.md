### LVS的调度算法


LVS的负载均衡算法有动态和静态之分：

静态算法:

* 1:rr(Round-robin):负载调度器将用户的请求轮询的分发到不同的服务器上（用户请求被等比例的分发到服务器上,不同性能的服务有着同样的负载）
* 2：wrr(weight Routnd-robin)：负载调度器将用户的请求根据不同服务器的权重分发（不同性能的服务器有着不同的负载）
* 3：dh(Destination hashing)： 目标地址散列调度：根据目标地址通过hash算法就行调度实现负载均衡,
* 4:sh(Source hashing):源地址散列地址调度，根据源地址通过hash算法就行调度实现负载均衡）

动态算法：

1：lc: least connection  （最近最少连接）

基于overhead来进行负载均衡(最少overhead 优先负载),通过活动连接个数×256+非活动连接的方式判断overhead

2：wlc : weight least connetion(加权最少连接)

采用的方式是overhead/权重值的算法，Overhead=活动连接个数×256+非活动连接个数

wlc是Linux企业集群默认算法（考虑到了非活动连接数，来实现负载均衡，其平衡企业负载方面做得相当出色)

3:sed ：最少期望延迟  ，这个算法在计算权重值的时候不再考虑非活动连接数

采用(活动连接数+1) \* 256/权重值 的方式判断overhead

4：NQ: never queue （永不排队）

  当某个real server只要有空闲连接时就将请求分发到其上面

5:LBLC:基于本地的最少连接 locality-based least connection  该算法是静态的dh算法的扩展，主要用户cache集群

6:LBLCR：Locality-Based Least-Connection with replication Scheduling：带复制的基于本地最少连接

  其应用的场景是，后台的服务器如果是cache服务器的时候，多个cache服务器之间可以共享资源

DR模型特性：

1：所有集群节点必须要在同一个物理网络中

2：RIP可以使用公有，私有地址，不支持端口映射

3：director 仅处理入站请求，出站不经过director(解决了lvs-dnat的调度器负载较大的瓶颈问题)

4:集群节点不再使用director作为他们的网关

5：DR模型比NAT模型可以使用更多的Real server（NAT模型最多支持10个real server）