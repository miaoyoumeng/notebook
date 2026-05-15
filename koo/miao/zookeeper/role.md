一、leader


&nbsp;&nbsp;&nbsp;&nbsp;Leader作为整个ZooKeeper集群的主节点，负责响应所有对ZooKeeper状态变更的请求。它会将每个状态更新请求进行排序和编号，以便保证整个集群内部消息处理的FIFO。


&nbsp;&nbsp;&nbsp;&nbsp;这里补充一下ZooKeeper的请求类型。对于exists，getData，getChildren等只读请求，收到该请求的zk服务器将会在本地处理，因为由第一讲的ZAB理论可知，每个服务器看到的名字空间内容都是一致的，无所谓在哪台机器上读取数据，因此如果ZooKeeper集群的负载是读多写少，并且读请求分布得均衡的话，效率是很高的。对于create，setData，delete等有写操作的请求，则需要统一转发给leader处理，leader需要决定编号、执行操作，这个过程称为一个事务（transaction）。


&nbsp;&nbsp;&nbsp;&nbsp;事务的编号就不说了，ZAB一章中已经把zxid的格式说得很清楚，已经忘了的可以回头查阅，重点来说说事务的执行。ZooKeeper事务和关系型数据库事务相似之处是都具备原子性，即整个事务（编号+执行）要么一起成功要么一起失败。另外事务还具备幂等性，即对一个事务执行多次，结果永远都是一致的。但ZooKeeper事务不具备关系型数据库事务的回滚机制，原因是不需要，因为ZAB协议已经保证消息是严格FIFO的，并且只有一个leader实际处理事务。（回忆两阶段提交2PC，之所以需要2PC的原因，归根结底是有不止一个“主”，必须保证这么多“主”看到的结果都是一致的）


&nbsp;&nbsp;&nbsp;&nbsp;另一个重要话题是leader选举，ZAB一章中已经提到有三种选举算法，目前默认的版本是FastLeaderElection，另两种已经被标记为deprecated。其过程如下：


* 数据恢复阶段。首先，每个ZooKeeper服务器先读取当前保存在磁盘的事务数据，从而得知当前自己能看到的最大zxid
* 首次发送自己的投票值。在读取数据之后，每个ZooKeeper服务器发送自己提议的leader，这个协议中包含了以下几部分的数据：
```
1)所选举leader的id，在初始阶段，每台服务器的这个值都是自己的id
```
```
2)服务器的最大zxid，因为FIFO原则，这个值越大说明该服务器离主越近
```
```
3)逻辑时钟的值，也就是epoch，每次选举leader这个值会加1
```
```
4)本机在当前选举过程中的状态，有以下几种：LOOKING，FOLLOWING，OBSERVING，LEADING
```
* 每台服务器将自己的上两种数据发送到集群中的其他服务器，同时也会接收来自其他服务器的这两种数据，此时如果该服务器的状态是在选举阶段(LOOKING状态)，那么首先要判断逻辑时钟值，分为以下三种情况：

二、Follower

Follower的逻辑就比较简单了。除了响应本服务器上的读请求外，follower还要处理leader的提议，并在leader提交该提议时在本地也进行提交。Follower处理提议的过程已经在ZAB一章中描述过了。
另外需要注意的是，leader和follower构成ZooKeeper集群的法定人数，也就是说，只有他们才参与新leader的选举、响应leader的提议。


三、Observer

如果ZooKeeper集群的读取负载很高，或者客户端多到跨机房，可以设置一些observer服务器，以提高读取的吞吐量。Observer和Follower比较相似，只有一些小区别：首先observer不属于法定人数，即不参加选举也不响应提议；其次是observer不需要将事务持久化到磁盘，一旦observer被重启，需要从leader重新同步整个名字空间。
