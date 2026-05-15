## Redis geospatial (地理位置)

> Redis 的 Geo 在 Redis 3.2 版本就推出了! 这个功能可以推算地理位置的信息: 两地之间的距离, 方圆几里的人

### # geoadd

> 添加地理位置
    
    
    127.0.0.1:6379> geoadd china:city 118.76 32.04 manjing 112.55 37.86 taiyuan 123.43 41.80 shenyang
    (integer) 3
    127.0.0.1:6379> geoadd china:city 144.05 22.52 shengzhen 120.16 30.24 hangzhou 108.96 34.26 xian
    (integer) 3
    

**规则**

两级无法直接添加，我们一般会下载城市数据(这个网址可以查询 GEO： http://www.jsons.cn/lngcode)！

  * 有效的经度从-180度到180度。
  * 有效的纬度从-85.05112878度到85.05112878度。

    
    
    # 当坐标位置超出上述指定范围时，该命令将会返回一个错误。
    127.0.0.1:6379> geoadd china:city 39.90 116.40 beijin
    (error) ERR invalid longitude,latitude pair 39.900000,116.400000
    

### # geopos

> 获取指定的成员的经度和纬度
    
    
    127.0.0.1:6379> geopos china:city taiyuan manjing
    1) 1) "112.54999905824661255"
       1) "37.86000073876942196"
    2) 1) "118.75999957323074341"
       1) "32.03999960287850968"
    

获得当前定位, 一定是一个坐标值!

### # geodist

> 如果不存在, 返回空

单位如下

  * m
  * km
  * mi 英里
  * ft 英尺

    
    
    127.0.0.1:6379> geodist china:city taiyuan shenyang m
    "1026439.1070"
    127.0.0.1:6379> geodist china:city taiyuan shenyang km
    "1026.4391"
    

### # georadius

> 附近的人 ==> 获得所有附近的人的地址, 定位, 通过半径来查询

获得指定数量的人

    
    
    127.0.0.1:6379> georadius china:city 110 30 1000 km			以 100,30 这个坐标为中心, 寻找半径为1000km的城市
    1) "xian"
    2) "hangzhou"
    3) "manjing"
    4) "taiyuan"
    127.0.0.1:6379> georadius china:city 110 30 500 km
    1) "xian"
    127.0.0.1:6379> georadius china:city 110 30 500 km withdist
    1) 1) "xian"
       2) "483.8340"
    127.0.0.1:6379> georadius china:city 110 30 1000 km withcoord withdist count 2
    1) 1) "xian"
       2) "483.8340"
       3) 1) "108.96000176668167114"
          2) "34.25999964418929977"
    2) 1) "manjing"
       2) "864.9816"
       3) 1) "118.75999957323074341"
          2) "32.03999960287850968"
    

参数 key 经度 纬度 半径 单位 [显示结果的经度和纬度] [显示结果的距离] [显示的结果的数量]

### # georadiusbymember

> 显示与指定成员一定半径范围内的其他成员
    
    
    127.0.0.1:6379> georadiusbymember china:city taiyuan 1000 km
    1) "manjing"
    2) "taiyuan"
    3) "xian"
    127.0.0.1:6379> georadiusbymember china:city taiyuan 1000 km withcoord withdist count 2
    1) 1) "taiyuan"
       2) "0.0000"
       3) 1) "112.54999905824661255"
          2) "37.86000073876942196"
    2) 1) "xian"
       2) "514.2264"
       3) 1) "108.96000176668167114"
          2) "34.25999964418929977"
    

参数与 georadius 一样

### # geohash(较少使用)

> 该命令返回11个字符的hash字符串
    
    
    127.0.0.1:6379> geohash china:city taiyuan shenyang
    1) "ww8p3hhqmp0"
    2) "wxrvb9qyxk0"
    

将二维的经纬度转换为一维的字符串, 如果两个字符串越接近, 则距离越近

### # 底层

> geo底层的实现原理实际上就是Zset, 我们可以通过Zset命令来操作geo
    
    
    127.0.0.1:6379> type china:city
    zset
    

查看全部元素 删除指定的元素

    
    
    127.0.0.1:6379> zrange china:city 0 -1 withscores
     1) "xian"
     2) "4040115445396757"
     3) "hangzhou"
     4) "4054133997236782"
     5) "manjing"
     6) "4066006694128997"
     7) "taiyuan"
     8) "4068216047500484"
     9) "shenyang"
    1)  "4072519231994779"
    2)  "shengzhen"
    3)  "4154606886655324"
    127.0.0.1:6379> zrem china:city manjing
    (integer) 1
    127.0.0.1:6379> zrange china:city 0 -1
    1) "xian"
    2) "hangzhou"
    3) "taiyuan"
    4) "shenyang"
    5) "shengzhen"
    

## # 参考文章

  * http://www.jsons.cn/lngcode
  * https://www.cnblogs.com/junlinsky/p/13528452.html
  * https://www.cnblogs.com/touyel/p/12728096.html
  * https://www.cnblogs.com/junlinsky/p/13528452.html
  * https://www.cnblogs.com/wang-sky/p/13857787.html


