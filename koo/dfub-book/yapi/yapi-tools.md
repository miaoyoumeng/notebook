
## @upper
语法：@upper( str )

作用：把字符串转换为大写。

```
Random.upper('hello')
// => "HELLO"
```
## @lower
语法：@lower( str )

作用：把字符串转换为小写。
```
Random.lower('HELLO')
// => "he
```
## @pick
    使用方式：@pick(arr)

从数组中随机选取一个元素，并返回。
* 示例：@pick(['this', 'is', 'picker', 'test'])

## @shuffle
语法：@shuffle( arr )

作用：打乱数组中元素的顺序，并返回。
```
Random.shuffle(['a', 'e', 'i', 'o', 'u'])
// => ["o", "u", "e", "i", "a"]
```

## @protocol
作用：随机生成一个 URL 协议。返回以下值之一

```
'http'、'ftp'、'gopher'、'mailto'、'mid'、'cid'、'news'、'nntp'、'prospero'、'telnet'、'rlogin'、'tn3270'、'wais'
```