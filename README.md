# crack-yakpro-po
cracking PHP code obfuscation which using yarkpo method

*incomplete*


### 破解思路: Yarkpo 混淆代码的特征主要有两个
1. goto 代替流程
2. 字符串用10进制、16进制编码

`这两个特征在文本中特别明显，如下`

``` php

<?php
 goto xmr59; xmr59: defined("\111\x4e\137\111\x41") or exit("\101\x63\143\x65\x73\163\x20\x64\145\156\151\x65\x64"); 
 goto a5gDB; Tk8Vg: require_once ROOT_PATH . "\x6d\x6f\144\145\x6c\x2f\143\x6f\x6d\x6d\x6f\x6e\x2e\160\150\160"; goto j7igX; 
 MRNIE: require_once ROOT_PATH . "\x6d\x6f\x64\x65\154\57\156\157\x74\x69\143\x65\56\160\x68\x70"; goto YiQux; 
 a5gDB: !defined("\122\x4f\117\x54\x5f\x50\101\x54\110") && define("\x52\x4f\117\124\137\x50\101\x54\110", 
 IA_ROOT . "\57\x61\144\x64\x6f\156\x73\x2f\153\165\156\144\x69\x61\156\137\146\141\x72\155\57");
```



