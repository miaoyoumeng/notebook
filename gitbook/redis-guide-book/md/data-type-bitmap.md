## Redis Bitmap （位存储）

> Bitmap 即位图数据结构，都是操作二进制位来进行记录，只有0 和 1 两个状态。

  * **用来解决什么问题** ？

比如：统计用户信息，活跃，不活跃！ 登录，未登录！ 打卡，不打卡！ **两个状态的，都可以使用 Bitmaps** ！

如果存储一年的打卡状态需要多少内存呢？ 365 天 = 365 bit 1字节 = 8bit 46 个字节左右！

  * **相关命令使用**

使用bitmap 来记录 周一到周日的打卡！ 周一：1 周二：0 周三：0 周四：1 ......

    
    
    127.0.0.1:6379> setbit sign 0 1
    (integer) 0
    127.0.0.1:6379> setbit sign 1 1
    (integer) 0
    127.0.0.1:6379> setbit sign 2 0
    (integer) 0
    127.0.0.1:6379> setbit sign 3 1
    (integer) 0
    127.0.0.1:6379> setbit sign 4 0
    (integer) 0
    127.0.0.1:6379> setbit sign 5 0
    (integer) 0
    127.0.0.1:6379> setbit sign 6 1
    (integer) 0
    

查看某一天是否有打卡！

    
    
    127.0.0.1:6379> getbit sign 3
    (integer) 1
    127.0.0.1:6379> getbit sign 5
    (integer) 0
    

统计操作，统计 打卡的天数！

    
    
    127.0.0.1:6379> bitcount sign # 统计这周的打卡记录，就可以看到是否有全勤！
    (integer) 3
    



