
# JKD 1.8升级

## dubbo.
```
修改dubbo.properties：dubbo.jdk=1.8
jenkins构建：选择jdk1.8构建参数
```

## 鲨鱼worker
```
修改worker.properties：dubbo.jdk=1.8
jenkins构建：选择jdk1.8构建参数
```
## tomcat
```

```

# 搜索引擎
## 当前部署方式

![部署方式](http://images.koolearn.com/fe_upload/2018/12/2018-12-17-1545049043378.png)

## 调整后部署方式

![部署方式](http://images.koolearn.com/fe_upload/2018/12/2018-12-17-1545049438338.png)

## 调整后说明
1、以业务传递的索引名当做路由

2、搜索集群部署调整、升级、业务隔离切割，对代码透明

# rabbitmq 调整

## 原来方式

1、按业务组分两套集群

2、集群部署方式，没有考虑机房机柜属性

3、客户端用spring-rabbit原生的

4、已暴露问题：
```
一、客户端出现流控，导致java进程线程池爆满。
二、机房单点
三、个别业务流量异常，可能影响整个集群稳定性
```   
![方式](http://images.koolearn.com/fe_upload/2018/12/2018-12-18-1545115967081.png)

## 新方式

一、接入方式
![方式](http://images.koolearn.com/fe_upload/2018/12/2018-12-18-1545116281172.png)

二、基于spring-rabbitmq封装了一个异步发送的队列，缓解流控问题，但是在出现流控情况下，可能出现消息丢失情况。

三、双机房集群部署、未来三机房集群

# codis 改造

##  方式 
1、三元桥、m7、阿里云都有proxy和从节点。
2、master节点暂时在三元桥和 m7机房
