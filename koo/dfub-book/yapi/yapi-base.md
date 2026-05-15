## @string

返回随机字串，有如下几种使用方式：

参数|是否必选|描述
:-:|:-:|:-:
length|可选|字串长度
min|可选|字串最短长度
max|可选|字串最大长度
pool|可选|表示字符池。如果传入 ‘lower’、‘upper’、‘number’或’symbol’，表示从内置的字符池从选取。

```
@string
@string(length)
@string(pool, length)
@string(min, max)
@string(pool, min, max)
```

## @integer
使用方法：@integer(min?, max?)

返回一个随机的整数。

* min：可选参数，整数最小值。
* max：可选参数，整数最大值。

## @float

@float(min?, max?, dmin?, dmax?)

返回一个随机浮点数。

参数|是否必选|描述
:-:|:-:|:-:
min|可选|整数部分最小值。
max|可选|整数部分最大值。
dmin|可选|小数部分最小长度。
dmax|可选|小数部分最大长度。

```
Random.natural()
// => 1002794054057984
Random.natural(10000)
// => 71529071126209
Random.natural(60, 100)
// => 77
```
## @character
语法：@character(pool?)

作用：返回一个随机字符。

参数|是否必选|描述
:-:|:-:|:-:
pool |可选|字符串。表示字符池，将从中选择一个字符返回。如果传入了 'lower' 或 'upper'、'number'、'symbol'，表示从内置的字符池从选取：

```
{
    lower: "abcdefghijklmnopqrstuvwxyz",
    upper: "ABCDEFGHIJKLMNOPQRSTUVWXYZ",
    number: "0123456789",
    symbol: "!@#$%^&*()[]"
}
```
## @boolean

语法：boolean( min?, max?, current? )

作用：返回一个随机的布尔值。

参数|是否必选|描述
:-:|:-:|:-:
min|可选|指示参数 current 出现的概率。概率计算公式为 min / (min + max)。该参数的默认值为 1，即有 50% 的概率返回参数 current。
max|可选|指示参数 current 的相反值 !current 出现的概率。概率计算公式为 max / (min + max)。该参数的默认值为 1，即有 50% 的概率返回参数 !current。
current|可选|可选值为布尔值 true 或 false。如果未传入任何参数，则返回 true 和 false 的概率各为 50%。该参数没有默认值。在该方法的内部，依据原生方法 Math.random() 返回的（浮点）数来计算和返回布尔值，例如在最简单的情况下，返回值是表达式 Math.random() >= 0.5 的执行结果。

```
Random.boolean()
// => true
Random.boolean(1, 9, true)
// => false
Random.bool()
// => false
Random.bool(1, 9, false)
```

## @natural

语法：@natural(min?, max?)

返回一个随机的自然数（大于等于 0 的整数）。

参数|是否必选|描述
:-:|:-:|:-:
min|可选|指示随机自然数的最小值。默认值为 0。
max|可选|指示随机自然数的最大值。默认值为 9007199254740992。
```
Random.natural()
// => 1002794054057984
Random.natural(10000)
// => 71529071126209
Random.natural(60, 100)
// => 77
```

## @id
作用：随机生成一个 18 位身份证。
```
Random.id()
// => "420000200710091854"
```
## @guid
作用：随机生成一个 GUID。

```
Random.guid()
// => "662C63B4-FD43-66F4-3328-C54E3FF0D56E"
```
