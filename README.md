# crack-yakpro-po    
破解由 `YAK Pro - Php Obfuscator` 混淆PHP代码的手段    

## 说明   

本脚本执行恢复还原度80%，剩下20%可手工还原，如:排版和逻辑等效替换，非全自动破解

## 环境

``` 
Windows 系统
Python2.7.x
```

## 依赖

``` sh
pip install pickle
pip install pyperclip
pip install optparse
```

## 命令

```
[USAGE]
python crack.py [options]

[OPTION]
-s --savedatafn <filename>  #指定临时文件名，该临时文件存储临时态的代码数据
-o --cache                  #是否关闭读取缓存，第一次使用必须关闭，每次指明则会重新训练数据
-f --mktplfile              #生成破解模板文件
-c --cachefn    <filename>  #指定缓存保存的文件，该缓存文件存储了序列化训练好的数据
-t --target     <filename>  #指定需要破解的文件，该文件被 Yak Pro 混淆说加密

```

## 解释

crack.py 的代码可读性比较差，编写的时候注意力全放在如何将代码混淆的还原度和效率提高，减少人工成本

所以没遵守任何编码规范，逻辑也看起来比较乱几乎很难一眼读懂。最底下有对破解的思路简单说明，如果有想

把代码完善度和可读性进行化优化或者重构想法的朋友可以联系我交流交流: 920248921@qq.com


## 使用方法:

  1. 生成缓存文件（必须）:
  ``` bash
  python crack.py -t your_encode_file.php -o
  ```
  your_encode_file 改为你的加密文件名，需要放在同一目录下，生成缓存文件名这一步很关键，后面的命令
  都依赖此条，请务必先执行，如果文件大的话，计算时间也会比较久，请耐心等待，生成一次后，就无需在执行
  此命令了。一次生成，无限使用
  
  
  2. 生成破解模板文件(可选):
  ```
  python crack.py -f
  ```
  执行后本地会生成 你的文件名.dec.php 的文件模板，可以打开看看
  
  
  3. 破解标签（核心）
  
  > 打开php代码，找到你想破解的块，然后复制第一个goto 如:
  
  ``` php
  public function xxx{ goto abcde; ...后面省略n个字}
  ```
  > 复制如上 abcde标签，到命令行进行代码解码
  ``` bash
  python crack.py abcde
  ```
  > 然后就会返回破解后的结果，结果看起来有点怪，需要第四步手工排版和逻辑等效替换调整一下
  
  
  4. 逻辑等效替换
  破解的代码中会经常看到如下形式
  
  ```php
  /*if epAfl */
  if (!($uid < 1)) {
  $card_id = intval($_GPC["card_id"]);
  /*if m0FKM */

  }
  return $this->result(1, "非法进入");
  gs0uX: $card_id = intval($_GPC["card_id"]);
  /*if m0FKM */
  ```
  
  其中 /\*if xxxxx \*/ 表示下一行代码的标签 xxxxx 会是一个if判断语句，之所以不采用全自动替换if代码
  是因为 yakpro 加密方法将 while 循环使用 if 替换了， 自动替换会导致解码工具死循环输出
  
  所谓等效替换就是，尽可能让代码量变少，以还原出最有可能性的代码，上面的PHP就可以等效替换成如下
  ```php
  if ($uid < 1) {
     return $this->result(1, "非法进入");
  }
  $card_id = intval($_GPC["card_id"]);
  /*if m0FKM */
  ```
  类似的还有很多，此处不一一举例了
  



## 太麻烦了？
联系主人，有偿破解代码:  920248921@qq.com
   
 

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
goto YiQux; a5gDB: !defined("\122\x4f\117\x54\x5f\x50\101\x54\110") && 
define("\x52\x4f\117\124\137\x50\101\x54\110", 
IA_ROOT . "\57\x61\144\x64\x6f\156\x73\x2f\153\165\156\144\x69\x61\156\137\146\141\x72\155\57"); 
goto EpukA; EpukA: 
include ROOT_PATH . "\151\156\x63\x2f\x77\x65\x62\x2f\146\x75\156\143\x74\x69\157\156\56\151\x6e\143\56\160\x68\160"; 
goto Tk8Vg; j7igX: require_once ROOT_PATH . "\155\157\144\x65\x6c\57\x75\163\x65\x72\x2e\x70\x68\160"; 
goto MRNIE; YiQux: class Farm_Distribution { ...
```

##### 0x01 先说说第2个特征，字符串编码的破解思路

其实这个字符串编码严格意义都不算是什么加密手段，只不过把汉字或者ASCII符号转换成 `8进制` 或 `16进制` 这两种数字编码

仔细观察下面这一串，不难发现这一串有的是8进制编码，如 `\101`，有的是16进制编码如 `\x6f` ，也就是8进制和16进制的混合编码

`\101\x63\143\x65\x73\163\x20\x64\145\156\151\x65\x64`

对于这种编码，在 python 中直接黏贴就可以解析出对应的 ASCII 字符， 但如果是中文， python 的交互式shell还直接解析不出来

可以写 py 脚本头部加上 #coding:utf-8 然后一个最简单的反编码器就出来了

``` python
#coding: utf-8
#python2.7
#解析英文
print "\101\x63\143\x65\x73\163\x20\x64\145\156\151\x65\x64"
#解析中文
print "\344\277\235\345\xad\230\xe6\x88\x90\345\x8a\x9f"
```

但如果是对于一整篇密文，这里就不能直接print了，最起码需要使用正则把他们匹配出来，然后

在结合 char() 等函数进行解码， 代码如下:

``` python
#将数字编码转成字符
def changeStrcode(inpCode):
    inpCode = re.sub(r"\\\\",r"\\",inpCode);  #如果是双斜杠，这替换成单斜杆

    strlist = re.findall(r"\\\d{2,3}",inpCode); #匹配2-3个数字，2个是16进制 3个是8进制

    for string in strlist:
        repStr = strdecode(string);
        inpCode = inpCode.replace(string, repStr);
    return inpCode;

def strdecode(string):
    strlist = string.split("\\")[1:];
    res = ""
    try:
        for i in strlist:
            if "x" in i:
                num = int(i[1:],16);        #使用16进制解码
            else :
                num = int(i,8);             #使用8进制解码
            res += chr(num);
    except:
        pass
    return res;
```

跑完上面两个函数，前面的明文也就变成了如下，是不是舒服了一点
``` PHP
<?php
goto xmr59; xmr59: defined("IN_IA") or exit("Access denied"); 
goto a5gDB; Tk8Vg: require_once ROOT_PATH . "model/common.php"; 
goto j7igX; MRNIE: require_once ROOT_PATH . "model/notice.php"; 
goto YiQux; a5gDB: !defined("ROOT_PATH") && define("ROOT_PATH", IA_ROOT . "/addons/kundian_farm/"); 
goto EpukA; EpukA: include ROOT_PATH . "inc/web/function.inc.php"; 
goto Tk8Vg; j7igX: require_once ROOT_PATH . "model/user.php"; 
goto MRNIE; 
YiQux: class Farm_Distribution { ...
```

##### 0x02 下面说说第二个goto特征

现在流行的编程语言基本不会再用goto了，goto越多代码越乱

. 首先研究一下 PHP 中goto 的运作原理

```PHP
<?php

foo: goto coo;
doo: echo "doo";
coo: echo "coo";
goto eoo;
eoo:
?>
```
执行结果就是
> coo

其中的执行顺序：
1. goto coo;
2. echo 'coo';
3. goto eoo;


两个特点：
1. 执行到标签时，标签身后代码会被执行，不一定非要goto才触发
2. goto 跳过去后就算执行完了所有代码不会回溯之前的位置，除非是用goto跳回来的


然后使用深度优先替换： 见到一个goto就替换一个

``` python
labelList = re.findall(r"([a-zA-Z0-9_]{5}): ",srcCode);
for labelName in labelList:
    labelValue = re.findall(r""+labelName+": (.*?)\s+[a-zA-Z0-9_]{5}:", srcCode)[0];
    srcCode.replace("goto "+labelName+";", labelValue);
```

上面指摘去了部分核心代码，运行结果如下
``` PHP
<?php
defined("IN_IA") or exit("Access denied");
!defined("ROOT_PATH") && define("ROOT_PATH", IA_ROOT . "/addons/kundian_farm/");
include ROOT_PATH . "inc/web/function.inc.php";
require_once ROOT_PATH . "model/common.php";
require_once ROOT_PATH . "model/user.php";
require_once ROOT_PATH . "model/notice.php";
```

