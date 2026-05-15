## redis 集群扩缩容

#### 扩容

当集群出现容量限制或者其他一些原因需要扩容时，redis cluster提供了比较优雅的集群扩容方案。

1. 首先将新节点加入到集群中，可以通过在集群中任何一个客户端执行cluster meet 新节点ip:端口，或者通过redis-trib add node添加，新添加的节点默认在集群中都是主节点。

2. 迁移数据 迁移数据的大致流程是，首先需要确定哪些槽需要被迁移到目标节点，然后获取槽中key，将槽中的key全部迁移到目标节点，然后向集群所有主节点广播槽（数据）全部迁移到了目标节点。直接通过redis-trib工具做数据迁移很方便。 现在假设将节点A的槽10迁移到B节点，过程如下： 
    
    B:cluster setslot 10 importing A.nodeId
    A:cluster setslot 10 migrating B.nodeId
    
循环获取槽中key，将key迁移到B节点 
    
    A:cluster getkeysinslot 10 100
    A:migrate B.ip B.port "" 0 5000 keys key1[ key2....]
    
向集群广播槽已经迁移到B节点

    
    
    cluster setslot 10 node B.nodeId
    

##### 缩容

缩容的大致过程与扩容一致，需要判断下线的节点是否是主节点，以及主节点上是否有槽，若主节点上有槽，需要将槽迁移到集群中其他主节点，槽迁移完成之后，需要向其他节点广播该节点准备下线（cluster
forget nodeId）。最后需要将该下线主节点的从节点指向其他主节点，当然最好是先将从节点下线。