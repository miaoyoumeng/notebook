##### 一、Redis的基本数据结构类型

[官方文档](http://redisdoc.com/index.html)

*1.1、*Redis有以下这五种基本类型：

* String（字符串）
* Hash（哈希）
* List（列表）
* Set（集合）
* zset（有序集合）

*1.2、*三种特殊的数据结构类型

* Geospatial： 地理位置定位，用于存储地理位置信息，并对存储的信息进行操作。
* Hyperloglog： 用来做基数统计算法的数据结构。如统计网站的UV。
* Bitmap： 用一个比特位来映射某个元素的状态，在Redis中，它的底层是基于字符串类型实现的，可以把bitmaps成作一个以比特位为单位的数组

*1.3、*特殊用法

* pub/sub 主题订阅模式实现一个生产者，多个消费者，当然也存在一定的缺点，当消费者下线时，生产的消息会丢失。

![alt 图表](/images/redis/redis_overview.png)

