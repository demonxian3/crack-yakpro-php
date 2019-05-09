# crack-yakpro-po
cracking PHP code obfuscation which using yarkpo method

*incomplete*


## 破解思路: 

##### 0x00 Yarkpo 混淆代码的特征主要有两个
1. goto 代替流程
2. 字符串用10进制、16进制编码

`这两个特征在文本中特别明显，如下`

``` php

<?php
 goto xmr59; xmr59: defined("\111\x4e\137\111\x41") or exit("\101\x63\143\x65\x73\163\x20\x64\145\156\151\x65\x64"); 
 goto a5gDB; Tk8Vg: require_once ROOT_PATH . "\x6d\x6f\144\145\x6c\x2f\143\x6f\x6d\x6d\x6f\x6e\x2e\160\150\160"; 
 goto j7igX; MRNIE: require_once ROOT_PATH . "\x6d\x6f\x64\x65\154\57\156\157\x74\x69\143\x65\56\160\x68\x70"; 
 goto YiQux; a5gDB: !defined("\122\x4f\117\x54\x5f\x50\101\x54\110") && define("\x52\x4f\117\124\137\x50\101\x54\110",
 IA_ROOT . "\57\x61\144\x64\x6f\156\x73\x2f\153\165\156\144\x69\x61\156\137\146\141\x72\155\57");
```

##### 0x01 先说说第2个特征，字符串编码的破解思路

其实这个字符串编码严格意义都不算是什么加密手段，只不过把汉字或者ASCII符号转换成 8进制 或 16进制这两种数字编码

仔细观察下面这一串，不难发现这一串有的是8进制编码，如 `\101`，有的是16进制编码如 `\x6f` ，也就是8进制和16进制的混合编码

`\101\x63\143\x65\x73\163\x20\x64\145\156\151\x65\x64`

对于这种编码，在 python 中直接黏贴就可以解析出对应的 ASCII 字符， 但如果是中文， python的交互式shell还直接解析不出来

可以写 py 脚本头部加上 #coding:utf-8 然后一个最简单的反编码器就出来了

```
#coding: utf-8
#python2.7
//解析英文
print "\101\x63\143\x65\x73\163\x20\x64\145\156\151\x65\x64"
//解析中文
print "\344\277\235\345\xad\230\xe6\x88\x90\345\x8a\x9f"



