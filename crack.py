#!coding: utf-8
import re
import os
import sys
import pickle


#是否开启缓存加快运行速度,重刷缓存请设置为0
openCache = 0

#目标文件名
targetfn = "wxapp.php"

#缓存数据文件名
cachefn = "cache.txt"

#目的文件名存储content
savedatafn = "tmp.php"

#目的破解模板文件
tpldatafn = targetfn.split(".")[0] + ".inc.php"



#将数字编码转成字符
def changeStrcode(inpCode):
    inpCode = re.sub(r"\\\\",r"\\",inpCode);

    strlist = re.findall(r"\\\w{2,3}",inpCode);

    for string in strlist:
        repStr = strdecode(string);
        inpCode = inpCode.replace(string, repStr);

    inpCode = inpCode.replace("\n", "\\n");
    return inpCode;

#单字符判断是八进制还是十六进制
def strdecode(string):
    strlist = string.split("\\")[1:];
    res = ""
    try:
        for i in strlist:
            if "x" in i:
                num = int(i[1:],16);
            else :
                num = int(i,8);
            res += chr(num);
    except:
        pass
    return res;



#去除单标签
def removeLabel(content):
    labelLists = re.findall(r"\s+([a-zA-Z0-9_]{5}):",content);

    for label in labelLists:
        matches = re.findall(r"goto "+label+";", content);

        if len(matches) == 0:
            content = re.sub(r""+label+":", "", content);
    return content;


#去除双重连续goto
def removeGoto(value):
    doubleGoto = re.findall("(goto \w{5};).*?(goto \w{5};)" , value);
    if len(doubleGoto) != 0:
        rmLable = doubleGoto[0][1];
        value = value.replace(rmLable,'');
    return value;


#简单排版
def simpleFormat(content):
    for key in re.findall(r"\w{5}: if",content):
        content = content.replace(key, "\n"+key);
    for pub in re.findall(r"public function",content):
        content = content.replace(pub, "\n"+pub);
    for pub in re.findall(r"private function",content):
        content = content.replace(pub, "\n"+pub);
    return content


#导出标签键值
def getLabel(content):
    labelDict = {};

    labelList = re.findall(r"([a-zA-Z0-9_]{5}): ",content);
    for name in labelList:

    
        #获取所有标签对应的值;
        value = re.findall(r""+name+": (.*?)\s+\w{5}:", content);

        if len(value) and "[{$" in value[0]:
            value = re.findall(r""+name+": (.*?)\s+\w{5}:", content, re.S);

        #重新调整最后一个标签的正则
        if len(value) == 0:
            #value = re.findall(r""+name+": (.*?)$", content);
            value = ""
        else:
            value = value[0];

        #循环次数
        i=30;
        #动态正则
        mlb = ".*?}";

        #收录foreach标签
        if "foreach " in value:
            while i>0:
                i-=1;
                value = re.findall(r""+name+": (foreach .*?{"+mlb+".*?goto \w{5};)",content, re.S);
                rbraces = value[0].count("}");
                lbraces = value[0].count("{");
                if lbraces > rbraces:
                    mlb = mlb + mlb * (lbraces - rbraces)
                elif lbraces == rbraces:
                    break;

            if len(value) != 0:
                value = value[0].replace('\n','')
                gotoList = re.findall(r"goto \w{5};", value);
                if len(gotoList) > 1:
                    prefix = value.split('{')[0];
                    lastGoto = gotoList.pop();
                    firstGoto = gotoList[0];
                    value = prefix + '{' + firstGoto + '}' + lastGoto;
                labelDict[name] = {'type':'fe', 'value':value, 'access':False};


        #收录if标签
        elif "if " in value:
            while i>0:
                i-=1;
                value = re.findall(r""+name+": (if.*?{"+mlb+".*?goto \w{5};)", content, re.S);
                rbraces = value[0].count("}");
                lbraces = value[0].count("{");
                if lbraces > rbraces:
                    mlb = mlb + mlb * (lbraces - rbraces)
                elif lbraces == rbraces:
                    break;

            if len(value) != 0:
                value = value[0].replace('\n','')
                labelDict[name] = {'type':'if', 'value':value, 'access':False};

        #收录普通标签
        else:
            #去除双重goto
            value = removeGoto(value)
            if value and value[0] == '}':
                value = '';
            labelDict[name] = {'type':'od', 'value':value, 'access':False};

    #for i in labelDict:
    #    if labelDict[i]['type'] == 'fe':
    #        print i,labelDict[i]['type'],labelDict[i]['value']
    #sys.exit();
        
    return labelDict;


#训练普通标签
def trainLabel(labelDict):
    #训练普通标签
    for lbidx in labelDict:
        lbvalue = labelDict[lbidx]['value'];


        while "goto" in lbvalue:
            lbnxt = re.findall(r"goto (\w{5});", lbvalue)[0];
            lbtype = labelDict[lbnxt]['type'];

            if lbtype == 'fe':
                rpstr = "/*foreach "+lbnxt+" */\n";
                if not labelDict[lbnxt]['access']:
                    rpstr += labelDict[lbnxt]['value'];

            elif lbtype == 'if':
                rpstr = "/*if "+lbnxt+" */\n";
                if not labelDict[lbnxt]['access']:
                    rpstr += labelDict[lbnxt]['value'];

            elif lbtype == 'od':
                rpstr = labelDict[lbnxt]['value'];

            else:
                print "UNKNOW TYPE"
                sys.exit();

            labelDict[lbnxt]['access'] = True;
            lbvalue = lbvalue.replace("goto "+lbnxt+";", rpstr);

        labelDict[lbidx]['value'] = lbvalue;
    return labelDict

    
#格式化输出结果
def formatRes(string):

    if ";" in string:
        string = string.replace(";",";\n");

    if "{" in string:
        string = string.replace("{","{\n");

    if "}" in string:
        string = string.replace("}","\n}\n");

    for s in string.split("\n"):
        print s.strip();


#生成手工破解框架文件
def mktplFile(content):
    global labelDict;

    incres = "<?php\n\n";
    topcode = re.findall(r".*?class", content)[0] + "\n";

    if re.findall(r"goto (\w{5});",topcode):
        topcode = labelDict[re.findall(r"goto (\w{5});",topcode)[0]];
        incres += topcode.replace(";", ";\n");

    incres += re.findall(r"class.*?{", content)[0] + "\n";

    for func in re.findall(r"(public function.*?){", content):
        incres += "    "+func + "{\n\n    }//pub\n\n"
    for func in re.findall(r"(private function.*?){", content):
        incres += "    "+func + "{\n\n    }//pri\n\n"
    incres += "}//class"
    print tpldatafn;
    open(tpldatafn,"w").write(incres);


#main
if __name__ == "__main__":

    if openCache:
        if not os.path.exists(savedatafn):
            print savedatafn + 'is not found';
            sys.exit();

        if not os.path.exists(cachefn):
            print cachefn + 'is not found';
            sys.exit();

        content = open(savedatafn, 'r').read();
        labelDict = pickle.loads(open(cachefn,'r').read());
        
    else:
        content = open(targetfn).read();
        content = removeLabel(content);
        content = changeStrcode(content);
        content = simpleFormat(content);
        content = content.replace("\n\n\n", "\n");
        open(savedatafn,"w").write(content);
        print "dump content ok";
        labelDict = getLabel(content);
        labelDict = trainLabel(labelDict);
        open(cachefn,"w").write(pickle.dumps(labelDict));
        print "dump labelDict ok"
    


    
    #[main]
    if len(sys.argv) > 1:
        p1 = sys.argv[1];

        if p1 == "c":
            print content;

        elif p1 == "f":
            mktplFile(content);

        else:
            try:
                formatRes(labelDict[p1]['value']);
            except:
                print 'error'
