###线程池

#####一、线程池技术方法

* 计算公式如下：

```
MaxProcessMemory - JVMMemory - ReservedOsMemory)/      ThreadStackSize = Number of threads
MaxProcessMemory：  指的是一个进程的最大内存
JVMMemory                 JVM内存
ReservedOsMemory     保留的操作系统内存
ThreadStackSize           线程栈的大小
```
* -Xss: 栈内存大小
    设置单个线程栈大小，一般默认512~1024kb。Jdk1.8 默认: 1024kb


#####二、线程池构建方法
```java
 public ThreadPoolExecutor(int corePoolSize,
                           int maximumPoolSize,
                           long keepAliveTime,
                           TimeUnit unit,
                           BlockingQueue<Runnable> workQueue,
                           ThreadFactory threadFactory,
                           RejectedExecutionHandler handler) ;

 ThreadPoolExecutor executor = new ThreadPoolExecutor(3, 5, 60, TimeUnit.MINUTES,
                                        new LinkedBlockingQueue<Runnable>());
```

* 1、核心参数

参数|描述
---|---
corePoolSize| 线程池中线程的个数,最少的个数,即使是空闲的,也会存在
maximumPoolSize|线程池中允许的连接的最大个数
keepAliveTime| corePoolSize之外的线程,在没有任务时,最大存活时间
unit|keepAlveTime 的时间单位
workQueue|在任务还没有执行前,保存Runnable任务的地方,也就是待执行任务队列
threadFactory| 线程工厂,可自定义线程生成的方式,可以自定义名字等等
handler|在线程池和队列满的时候,如何处理新到来的任务

* 2、BlockingQueue选项

类|描述
---|---
ArrayBlockingQueue|数组，可控容量，避免oom
LinkedBlockingQueue|链表，可控容量，避免oom
SynchronousQueue|没有容量，是无缓冲等待队列，是一个不存储元素的阻塞队列，<br>会直接将任务交给消费者
DelayQueue|无界阻塞队列<br>队列是有序的<br>对象只能在其到期时才能从队列中取走
PriorityBlockingQueue|无界阻塞队列<br>不能保证同优先级元素的顺序

* 3、RejectedExecutionHandler选项

类|描述
---|---
AbortPolicy|拒绝，抛出异常
DiscardOldestPolicy|丢弃最早的任务
DiscardPolicy|丢弃，没有任何异常
CallerRunsPolicy|交给主线程