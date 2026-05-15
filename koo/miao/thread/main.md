

### 主线程调用

示例

```java
	public static void main(String[] args) {
        final String[] contents = new String[]{"我","爱","北","京","天","安", "门"};
        final AtomicInteger atomic = new AtomicInteger(0);

        for (int i = 0; i < 2; i++) {
            new Thread(){
                @Override
                public void run() {
                    while (atomic.get() < contents.length) {
                        final int i = atomic.get();
                        final int index = Long.valueOf(Thread.currentThread().getId() % 2).intValue();
                        if ((i + index) % 2 == 0 && i < contents.length) {
                            System.out.println(Thread.currentThread().toString() + contents[i]);
                            atomic.incrementAndGet();
                        }
                    }
                }
            }.start();
        }
    }
```

输出，每个线程交替顺序处理字符串数组

```txt
Thread[Thread-1,5,main]我
Thread[Thread-0,5,main]爱
Thread[Thread-1,5,main]北
Thread[Thread-0,5,main]京
Thread[Thread-1,5,main]天
Thread[Thread-0,5,main]安
Thread[Thread-1,5,main]门

```


