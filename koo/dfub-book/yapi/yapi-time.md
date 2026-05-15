
## @timestamp

返回当前unix时间戳

## @now
语法：@now(unit?, format?)

参数|是否必选|描述
:-:|:-:|:-:
unit|可选|表示时间单位，用于对当前日期和时间进行格式化。可选值有：year、month、week、day、hour、minute、second、week，默认不会格式化。
format |可选|指示生成的日期和时间字符串的格式。默认值为 yyyy-MM-dd HH:mm:ss。

```
Random.now()
// => "2014-04-29 20:08:38 "
Random.now('day', 'yyyy-MM-dd HH:mm:ss SS')
// => "2014-04-29 00:00:00 000"
Random.now('day')
// => "2014-04-29 00:00:00 "
Random.now('yyyy-MM-dd HH:mm:ss SS')
// => "2014-04-29 20:08:38 157"

Random.now('year')
// => "2014-01-01 00:00:00"
Random.now('month')
// => "2014-04-01 00:00:00"
Random.now('week')
// => "2014-04-27 00:00:00"
Random.now('day')
// => "2014-04-29 00:00:00"
Random.now('hour')
// => "2014-04-29 20:00:00"
Random.now('minute')
// => "2014-04-29 20:08:00"
Random.now('second')
// => "2014-04-29 20:08:38"
```

## @date

语法：@date(format)

作用：返回一个随机的时间字符串。

参数|是否必选|描述
:-:|:-:|:-:
format|可选|指示生成的时间字符串的格式。默认值为 yyyy-MM-dd。

## @time

语法：@time(format)

作用：返回一个随机的时间字符串。

参数|是否必选|描述
:-:|:-:|:-:
format|可选|指示生成的时间字符串的格式。默认值为 HH:mm:ss。

## @datetime
@datetime(format?)

返回一个随机的日期和时间字符串。

参数|是否必选|描述
:-:|:-:|:-:
format|可选|生成的日期和时间字符串的格式。默认值为yyyy-MM-dd HH:mm:ss。
