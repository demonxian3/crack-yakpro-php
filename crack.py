#!coding: utf-8
import re
import os
import sys
import pickle
from optparse import OptionParser


#是否开启缓存加快运行速度,重刷缓存请设置为0
openCache = 1

#目标文件名
targetfn = "test.php"

#缓存数据文件名
cachefn = "cache.txt"

#目的文件名存储content
savedatafn = "tmp.php"

#目的破解模板文件
tpldatafn = targetfn.split(".")[0] + ".dec.php"

#核心数据结构
"""
labelData:{
    'type': labelType,
    'dict': labelDict,
}

labelDict : {
    'labe1': {value:'xxx', type:'if', access:True},
    'labe2': {value:'xxx', type:'fe', access:False},
}

labelType : {
    'if': [labe1, labe2],
    'fe': [labe3, labe4],
    'od': [labe5, labe6],
}
"""

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
    labelDict = { };
    labelType = {
        'od': [],
        'if': [],
        'fe': [],
        'sw': []
    };

    labelList = re.findall(r"([a-zA-Z0-9_]{5}): ",content);
    for name in labelList:

        #获取所有标签对应的值;
        value = re.findall(r""+name+": (.*?)\s+\w{5}:", content);

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
                labelType['fe'].append(name);

        #收录switch
        elif "switch (" in value :
            while i>0:
                i-=1;
                value = re.findall(r""+name+": (switch .*?{"+mlb+".*?goto \w{5};)",content, re.S);
                if value:
                    rbraces = value[0].count("}");
                    lbraces = value[0].count("{");
                    if lbraces > rbraces:
                        mlb = mlb + mlb * (lbraces - rbraces)
                    elif lbraces == rbraces:
                        break;

            if len(value) != 0:
                value = value[0].replace('\\n','');
                lpos = value.find('{');
                rpos = value.rfind('}');
                inner = value[lpos:rpos];
                prefix = value[:lpos];
                caseList = re.findall(r"(case .*?goto \w{5};)", inner);

                #default 情况复杂暂不处理
                #defaList = re.findall(r"(default: .*?goto \w{5};)",value);
                #if not defaList:
                #    defaStr = '';
                #else:
                #    defaStr = defaList[0];

                value = prefix + '{\n' + '\n'.join(caseList) + '\n}'
                labelDict[name] = {'type':'sw', 'value':value, 'access':False};
                labelType['sw'].append(name);

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
                gotoList = re.findall(r"goto \w{5};", value);
                if len(gotoList) > 1:
                    prefix = value.split('{')[0];
                    lastGoto = gotoList.pop();
                    firstGoto = gotoList[0];
                    value = prefix + '{' + firstGoto + '}' + lastGoto;
                labelDict[name] = {'type':'if', 'value':value, 'access':False};
                labelType['if'].append(name);

        #收录普通标签
        else:
            #去除双重goto
            value = removeGoto(value)
            if value and value[0] == '}':
                value = '';
            labelDict[name] = {'type':'od', 'value':value, 'access':False};
            labelType['od'].append(name);

    labelData = {
       'dict': labelDict,
       'type': labelType,
    }
    return labelData;


#训练各类标签
def trainLabel(labelData):

    labelDict = labelData['dict'];
    labelType = labelData['type'];

    def train(dictType):
        for lbidx in labelType[dictType]:
            lbvalue = labelDict[lbidx]['value'];

            while "goto" in lbvalue:
                lbnxt = re.findall(r"goto (\w{5});", lbvalue)[0];
                lbtype = labelDict[lbnxt]['type'];

                if lbtype == 'fe':
                    rpstr = "/*foreach "+lbnxt+" */\n";
                    if not labelDict[lbnxt]['access']:
                        labelDict[lbnxt]['access'] = True;
                        rpstr += labelDict[lbnxt]['value'];

                elif lbtype == 'sw':
                    rpstr = "/*switch "+lbnxt+" */\n";
                    if not labelDict[lbnxt]['access']:
                        labelDict[lbnxt]['access'] = True;
                        rpstr += labelDict[lbnxt]['value'];

                elif lbtype == 'if':
                    rpstr = "/*if "+lbnxt+" */\n";
                    if not labelDict[lbnxt]['access']:
                        labelDict[lbnxt]['access'] = True;
                        rpstr += labelDict[lbnxt]['value'];

                elif lbtype == 'od':
                    rpstr = labelDict[lbnxt]['value'];

                else:
                    print "UNKNOW TYPE"
                    sys.exit();

                lbvalue = lbvalue.replace("goto "+lbnxt+";", rpstr);

            labelDict[lbidx]['value'] = lbvalue;
    

    train('od');
    train('if');
    train('fe');
    train('sw');

    return {'type':labelType, 'dict':labelDict};

    
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
        topcode = labelDict[re.findall(r"goto (\w{5});",topcode)[0]]['value'];
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
    usage = "Usage: %prog ";

    parser = OptionParser(usage=usage);

    parser.add_option('-o','--cache', action='store_true', dest='openCache');
    parser.add_option('-f','--mktplfile',action='store_true', dest='mktplfile');
    parser.add_option('-c','--cachefn', type='string', dest='cachefn');
    parser.add_option('-t','--target', type='string', dest='targetfn');
    parser.add_option('-s','--savedatafn', type='string', dest='savedatafn');

    (options, args) = parser.parse_args();
    #print options;

    if options.openCache:
        openCache = 0;

    if options.targetfn:
        targetfn = options.targetfn;

    if options.cachefn:
        cachefn = options.cachefn;

    if options.savedatafn:
        savedatafn = options.savedatafn;


    if openCache:
        if not os.path.exists(savedatafn):
            print savedatafn + 'is not found';
            sys.exit();

        if not os.path.exists(cachefn):
            print cachefn + 'is not found';
            sys.exit();

        content = open(savedatafn, 'r').read();
        labelData = pickle.loads(open(cachefn,'r').read());
        
    else:
        content = open(targetfn).read();
        content = removeLabel(content);
        content = changeStrcode(content);
        content = simpleFormat(content);
        content = content.replace("\n\n\n", "\n");
        open(savedatafn,"w").write(content);
        print "dump content ok";
        labelData = getLabel(content);
        labelData = trainLabel(labelData);
        open(cachefn,"w").write(pickle.dumps(labelData));
        print "dump labelData ok"
    

    if options.mktplfile:
        mktplFile(content);
    elif len(args)>0:
        label = args[0]
        formatRes(labelData['dict'][label]['value']);

