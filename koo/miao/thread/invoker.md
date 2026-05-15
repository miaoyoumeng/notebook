### 线程池调用方法

##### 一、Runnable

```java
public interface Runnable {
    public abstract void run();
}
```
Runnable 是一个接口，就实现run方法，在run方法里面编写你要执行的代码就行了，但是没有任务返回接口，并且无法抛出异常。


```java
Runnable runnable = new Runnable() {
    @Override
    public void run() {
        // TODO: 
    }
};
Thread thread = new Thread(runnable);
thread.start();

```

##### 二、Callable

```java
public interface Callable<V> {
    V call() throws Exception;
}
```

Callable 是一个接口，就实现call方法，在call方法里面编写你要执行的代码就行了，返回的就是执行的结果了。有返回的结果，且可以抛出异常！一般配合ThreadPoolExecutor使用的。

```java
ExecutorService executor = Executors.newFixedThreadPool(1);
Future<String> future = executor.submit(new Callable<String>() {
    @Override
    public String call() throws Exception {
        return null;
    }
});

try {
    future.get();
} catch (Exception e) {
    e.printStackTrace();
}
```

##### 三、Future

Future也是一个接口，它可以对具体的Runnable或者Callable任务进行取消、判断任务是否已取消、查询任务是否完成、获取任务结果。

**1、jdk1.8之前：**
```java
public interface Future<V> {
    //中断
    boolean cancel(boolean mayInterruptIfRunning);
    //任务最终状态是否为“被取消”
    boolean isCancelled();
    //任务最终状态是否为“完成”
    boolean isDone();
    //得到任务执行结果，方法阻塞
    V get() throws InterruptedException, ExecutionException;
    //得到任务执行结果，方法阻塞
    V get(long timeout, TimeUnit unit)
        throws InterruptedException, ExecutionException, TimeoutException;
}
```
***两个get方法都会阻塞当前调用get的线程，直到返回结果或者超时才会唤醒当前的线程。***


**1)不支持手动完成**

我通过其他路径已经获取到了任务结果，现在没法把这个任务结果，通知到正在执行的线程，所以必须主动取消或者一直等待它执行完成。

**2)不支持进一步的非阻塞调用**

这个指的是我们通过Future的get方法会一直阻塞到任务完成，但是我还想在获取任务之后，执行额外的任务，因为Future不支持回调函数，所以无法实现这个功能。

**3)不支持链式调用**

这个指的是对于Future的执行结果，我们想继续传到下一个Future处理使用，从而形成一个链式的pipline调用，这在Future中是没法实现的。

**4)不支持多个Future合并**

比如我们有10个Future并行执行，我们想在所有的Future运行完毕之后，执行某些函数，是没法通过Future实现的。

**5)不支持异常处理**

Future的API没有任何的异常处理的api，所以在异步运行时，如果出了问题是不好定位的。

**2、jdk1.8之后，提供了CompletableFuture**

[CompletableFuture详解](/thread/completable-future.html)