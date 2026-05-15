## @image
语法：image( size?, background?, foreground?, format?, text? )

* Random.image()
* Random.image( size )
* Random.image( size, background )
* Random.image( size, background, text )
* Random.image( size, background, foreground, text )
* Random.image( size, background, foreground, format, text )

作用：生成一个随机的图片地址。

size
可选。

指示图片的宽高，格式为 '宽x高'。默认从下面的数组中随机读取一个：
```
[
    '300x250', '250x250', '240x400', '336x280', 
    '180x150', '720x300', '468x60', '234x60', 
    '88x31', '120x90', '120x60', '120x240', 
    '125x125', '728x90', '160x600', '120x600', 
    '300x600'
]
```
background
可选。

指示图片的背景色。默认值为 '#000000'。

foreground
可选。

指示图片的前景色（文字）。默认值为 '#FFFFFF'。

format
可选。

指示图片的格式。默认值为 'png'，可选值包括：'png'、'gif'、'jpg'。

text
可选。

指示图片上的文字。默认值为参数 size。
```
Random.image()
// => "http://dummyimage.com/125x125"
Random.image('200x100')
// => "http://dummyimage.com/200x100"
Random.image('200x100', '#fb0a2a')
// => "http://dummyimage.com/200x100/fb0a2a"
Random.image('200x100', '#02adea', 'Hello')
// => "http://dummyimage.com/200x100/02adea&text=Hello"
Random.image('200x100', '#00405d', '#FFF', 'Mock.js')
// => "http://dummyimage.com/200x100/00405d/FFF&text=Mock.js"
Random.image('200x100', '#ffcc33', '#FFF', 'png', '!')
// => "http://dummyimage.com/200x100/ffcc33/FFF.png&text=!"
```

## @imageData
语法：imageData(size, text)

作用：生成一段随机的 Base64 图片编码。

size
可选。

指示图片的宽高，格式为 '宽x高'。默认从下面的数组中随机读取一个：
```
[
    '300x250', '250x250', '240x400', '336x280', 
    '180x150', '720x300', '468x60', '234x60', 
    '88x31', '120x90', '120x60', '120x240', 
    '125x125', '728x90', '160x600', '120x600', 
    '300x600'
]
```
text
可选。

指示图片上的文字。默认值为参数 size。

```
Random.dataImage()
// => "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAH0AAAB9CAYAAACPgGwlAAAFJElEQVR4Xu2dS0hUURzG/1Yqlj2otJe10AqCoiJaFFTUpgcUhLaKCIogKCEiCl0U1SIIF1EIQlFEtCmkpbWSHlAQYRYUlI9Ie6nYmI9hfIx1LpzL3PGO/aeuM/r/f7PRufe7d873/ea75xw3ZjTumDtMeKlKIAPQVfF2zAK6PuaArpA5oAO6xgQUesacDugKE1BoGU0HdIUJKLSMpgO6wgQUWkbTAV1hAgoto+mArjABhZbRdEBXmIBCy2g6oCtMQKFlNB3QFSag0DKaDugKE1BoGU0HdIUJKLSMpgO6wgQUWkbTAV1hAgoto+mArjABhZbRdEBXmIBCy2g6oCtMQKFlNB3QFSag0DKaDugKE1BoGU0HdIUJKLSMpgO6wgQUWkbTAV1hAgoto+mArjABhZbRdEBXmIBCy2g6oCtMQKFlNB3QFSag0DKaDugKE1BoGU0HdIUJKLQ8bpo+fft+ylxYSJ23LvpisOfNST/N7ENniYa9/0xy4GsTdT+6+09Yx9t4/slEgovSDt2EO3P3YcoqWuUMsWln3oihFlTWUlbhSvf4UKid2iqOUfhVrXussKZ9xHXh10/oW1lxUnmNt/EkNXimOK3QTTtn7Sv1DDUees66rTT/3B0a/NFCvc9raOqf9+YL0PfiIX0/f8ADPdrXTZEPde6xyMd66rx5wXlvnwThN8/cL4ttc7S3i0L3rjqaVI2HyWdMZGmFbhwtvv7cgZm7ZS9NyS/wbboBb1ttwQy2tdLng2s90OOPxSa24FI15azZTAOtDdRyZAOZe84ru0GTps2g0P1r7pcjVeMZE5rMm6Yduh3nktt1CaHHesk/XUW5W4sp8v4lfTm5ywN9eCBCQz/baOBLE0Ua3rgg4z/DPCUmz5xD2SvWU6IpIBXjYTIKXDahoNtHvUmho/KMZ5HmN6f31FZT2+Wjbmix12dkZtNoTwYO9P8dT+A0mTecMNBNwPmnKmnyrDyKhxnv1U4B0d5f9KmkyHPaPinMwfYrJxKu7v8GPajxMDkFKpsQ0JMJ2KZjmm8e9817CjxNt/O4Odjf+JZaj2/zDXQ06EGNJ1CSSdws7dDNAsvsr7OXr3UWVeG6x87wv5WXOD9jAzZbtf7md669nscP3KbOLa2gaE+Xc27axl2UWbB0xLxvFmnmuJnTzU/7e+wuIJXjSYJToNK0Q/ebi41Du3Xz20bZBGJX3fH3Mav0jqpyd9Xvt3o3W0Ezt492H/tZQY8nUIpJ3izt0J39s8/L7q9N03NWb/LVhOuferZyWYuX0WDnD2evHv+XOPs5sdc4+/RFRX+eECFnn25eqRpPkpwClacdeqBucDNWAoDOikmWCNBl8WS5AXRWTLJEgC6LJ8sNoLNikiUCdFk8WW4AnRWTLBGgy+LJcgPorJhkiQBdFk+WG0BnxSRLBOiyeLLcADorJlkiQJfFk+UG0FkxyRIBuiyeLDeAzopJlgjQZfFkuQF0VkyyRIAuiyfLDaCzYpIlAnRZPFluAJ0VkywRoMviyXID6KyYZIkAXRZPlhtAZ8UkSwTosniy3AA6KyZZIkCXxZPlBtBZMckSAbosniw3gM6KSZYI0GXxZLkBdFZMskSALosnyw2gs2KSJQJ0WTxZbgCdFZMsEaDL4slyA+ismGSJAF0WT5YbQGfFJEsE6LJ4stwAOismWSJAl8WT5QbQWTHJEgG6LJ4sN4DOikmWCNBl8WS5AXRWTLJEgC6LJ8sNoLNikiUCdFk8WW4AnRWTLNFvXskYA3TG3JwAAAAASUVORK5CYII="
Random.dataImage('200x100')
// => "data:image/png;base64,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"

```