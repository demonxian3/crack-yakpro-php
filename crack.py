#!coding: utf-8
import re
import os
import sys
import pickle


#是否强制训练，不读取缓存数据
forceTraining=0

#目标文件名
targetfn = "api.php"

#普通标签缓存文件名
lbdatafn = "lbdata.txt"

#条件标签缓存文件名
ifdatafn = "ifdata.txt"

#目的文件名 存储content变量(密文)
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
            #if num < 127:
            res += chr(num);
            #else:
            #    res += "\\x"+str(hex(num))[2:]
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
    return content


#导出标签键值
def getLabel(content):
    labelDict = {};
    labelIfDict = {};

    labelList = re.findall(r"([a-zA-Z0-9_]{5}): ",content);
    for name in labelList:
    
        value = re.findall(r""+name+": (.*?)\s+\w{5}:", content);

        if len(value) and "[{$" in value[0]:
            value = re.findall(r""+name+": (.*?)\s+\w{5}:", content, re.S);

        #重新调整最后一个标签的正则
        if len(value) == 0:
            #value = re.findall(r""+name+": (.*?)$", content);
            value = ""
        else:
            value = value[0];

        #包含if的标签先不收录
        if "if " not in value:
            #去除多重 goto 保留第一个
            value = removeGoto(value)
            labelDict[name]  = value;
        else:
            #value = re.findall(r""+name+": (if \(.*?{\$.})", content);
            value = re.findall(r""+name+": (if \(.*?\[{\$.}\"\]\) {.*?goto \w{5};.*?}.*?goto \w{5};)", content);
            if value == []:
                value = re.findall(r""+name+": (if.*?{.*?}.*?goto \w{5};)", content);

            if len(value) != 0:
                labelIfDict[name] = value[0];

    return (labelDict, labelIfDict)


#训练普通标签
def trainLabel(labelDict,labelIfDict):
    for lbidx in labelDict:
        lbstr = labelDict[lbidx];

        while "goto" in lbstr:
            lbnxt = re.findall(r"goto (\w{5});", lbstr)[0];
    
            if lbnxt in labelDict:
                rpstr = labelDict[lbnxt];
            elif lbnxt in labelIfDict:
                #rpstr = labelIfDict[lbnxt];
                rpstr = "/*if "+lbnxt+" */";
            else:
                print "ERR: 4399"
                sys.exit();
    
            lbstr = lbstr.replace("goto "+lbnxt+";", rpstr);
    
        labelDict[lbidx] = lbstr;
    return labelDict;



#训练条件标签
def trainIfLabel(labelDict,labelIfDict):
    for ifidx in labelIfDict:
        ifstr = labelIfDict[ifidx];
        
        while "goto" in ifstr:
            lbnxt = re.findall(r"goto (\w{5});", ifstr)[0];
    
            if lbnxt in labelDict:
                rpstr = labelDict[lbnxt];
            elif lbnxt in labelIfDict:
                #rpstr = labelIfDict[lbnxt];
                rpstr = "/*if "+lbnxt+" */";
            else:
                print "ERR: 9877"
                sys.exit();
    
            ifstr = ifstr.replace("goto "+lbnxt+";", rpstr);

    
        labelIfDict[ifidx] = ifstr;

    return labelIfDict;

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
    incres += "}//class"
    print tpldatafn;
    open(tpldatafn,"w").write(incres);


#main
if __name__ == "__main__":
    #[content]
    if os.path.exists(savedatafn) and not forceTraining:
        content = open(savedatafn, "r").read();
    else:
        content = open(targetfn).read();
        content = removeLabel(content);
        content = changeStrcode(content);
        content = simpleFormat(content);
        content = content.replace("\n\n\n", "\n");
        open(savedatafn,"w").write(content);
    

    #[label]
    if os.path.exists(lbdatafn) and not forceTraining:
        labelDict = pickle.loads(open(lbdatafn,"r").read());
    else:
        labelList = getLabel(content);
        labelDict = labelList[0];
        labelIfDict = labelList[1];
        labelDict = trainLabel(labelDict, labelIfDict);
        open(lbdatafn,"w").write(pickle.dumps(labelDict));
        print "dump lbdata ok"
    

    #[iflabel]
    if os.path.exists(ifdatafn) and not forceTraining:
        labelIfDict = pickle.loads(open(ifdatafn,"r").read());
    else:
        labelList = getLabel(content);
        labelDict = labelList[0];
        labelIfDict = labelList[1];
        labelIfDict = trainIfLabel(labelDict,labelIfDict);
        open(ifdatafn,"w").write(pickle.dumps(labelIfDict));
        print "dump ifdata ok"
    
    #[main]
    if len(sys.argv) > 1:
        p1 = sys.argv[1];

        if p1 == "c":
            print content;

        elif p1 == "f":
            mktplFile(content);

        elif p1 in labelDict:
            formatRes(labelDict[p1]);

        elif p1 in labelIfDict:
            formatRes(labelIfDict[p1]);

