### String（字符串）

* String是Redis最基础的数据结构类型，它是二进制安全的，可以存储图片或者序列化的对象，值最大存储为512M
* 应用场景：共享session、分布式锁，计数器、限流。
* 内部编码有3种，int（8字节长整型）/embstr（小于等于39字节字符串）/raw（大于39个字节字符串）
* 简单命令: 

```shell
SET,SETNX,SETEX,PSETEX,GET,GETSET,STRLEN,APPEND,SETRANGE,GETRANGE,
INCR,INCRBY,INCRBYFLOAT,DECR,DECRBY,MSET,MSETNX,MGET
```

```C
struct sdshdr{
  unsigned int len; // 标记buf的长度
  unsigned int free; //标记buf中未使用的元素个数
  char buf[]; // 存放元素的坑
}
```
结构图如下：

![alt 图表](/images/redis/redis_string.png)

*动态字符串操作方法*

* 字符串长度处理：Redis获取字符串长度，时间复杂度为O(1)，而C语言中，需要从头开始遍历，复杂度为O（n）;
* 空间预分配：字符串修改越频繁的话，内存分配越频繁，就会消耗性能，而SDS修改和空间扩充，会额外分配未使用的空间，减少性能损耗。
* 惰性空间释放：SDS 缩短时，不是回收多余的内存空间，而是free记录下多余的空间，后续有变更，直接使用free中记录的空间，减少分配。
* 二进制安全：Redis可以存储一些二进制数据，在C语言中字符串遇到'\0'会结束，而 SDS中标志字符串结束的是len属性。