#!coding: utf-8
import re
import sys
from pprint import pprint

class KhazixCrack:
    def __init__(self):
        self.input = "";
        self.output = "";
        self.result = [];
        self.filecode = "";
        self.needPad = 0;
        self.prefixStr = "";
        self.suffixStr = "";
        self.tagList = {};
        self.labelDict = {};
        self.resBlock = [];
        self.resCode = "";

    def preprocess(self):
        #去除捣蛋标签，没人跳转的那种
        labelLists = re.findall(r"\s+([a-zA-Z0-9_]{5}):",self.filecode);

        for label in labelLists:
            matches = re.findall(r"goto "+label+";", self.filecode);

            if len(matches) == 0:
                self.filecode = re.sub(r""+label+":", "", self.filecode);



    def render(self, filename):
        self.filecode = open(filename, "r").read();

        self.preprocess();
        headCode = re.findall(r"(.*?\s+class.*?)public", self.filecode);
        if len(headCode) != 0:
            self.parseFunction(headCode[0]);

        funList = re.findall(r"(\s*function.*?)(\s+public|$)", self.filecode);

        for funCode in funList:
            self.parseFunction(funCode[0]);

        self.clear(); 
        self.formats();
        self.changeStrcode();
        self.postprocess();

        print self.resCode;
        #return self.filecode;


    def parseFunction(self, funcode):
        self.brace = [];
        self.inpBlock = [];
        self.outBlock = [];
        self.resBlock = [];
        self.labelList = [];
        self.input = funcode
        self.mkdBlock = self.input.split('{');

        #以 { 和 } 作为分隔符进行分块
        for block in self.mkdBlock:
            if "}" in block:
                self.inpBlock += block.split("}");
            else:
                self.inpBlock += [block];

        if len(self.inpBlock) > 2:
            self.inpBlock.pop();

        #记录话括弧
        for c in self.input:
            if c == "{":
                self.brace.append(c);
            elif c == "}":
                self.brace.append(c);

        #获取所有 label键 => label值
        for block in self.inpBlock:
            self.labelList = re.findall(r"([a-zA-Z0-9_]{5}): ",block);
            
            for labelName in self.labelList:

                labelValue = re.findall(r""+labelName+": (.*?)\s+[a-zA-Z0-9_]{5}:", block);

                #重新调整最后一个标签的正则
                if len(labelValue) == 0:
                    labelValue = re.findall(r""+labelName+": (.*?)$", block);

                self.labelDict[labelName]  = labelValue[0];


        #pprint(self.labelDict);

        for block in self.inpBlock:
            #print block
            if "goto" not in block:
                self.resBlock.append(block);
                continue;

            #寻找第一个goto, 这里要想办法不考虑 } goto 的情况
            matchRes = re.search(r"(^.*?goto (.*?);)", block);
            self.outBlock = matchRes.group(0);
            beginLabel = matchRes.group(2);
            self.rec(beginLabel);
            self.resBlock.append(self.outBlock);

        for i in range(len(self.resBlock)):
            try:
                self.resCode += self.resBlock[i] + self.brace[i];
            except:
                pass;
        self.resCode += "\n\n";

    def rec(self, label):
        #print label;
        #取替换值
        value = self.labelDict[label];

        #替换
        self.outBlock = self.outBlock.replace("goto "+label+";", value);
        #print self.outBlock;

        nextGoto = re.findall(r"goto (.*?);", value);
        
        if len(nextGoto) > 0:
            self.rec(nextGoto[0]);
        else:
            return

    def clear(self):
        self.resCode = re.sub(r'goto [a-zA-Z0-9_]{5};','',self.resCode);
        self.resCode = re.sub(r'\s+[a-zA-Z0-9_]{5}:','',self.resCode);

    def formats(self):
        self.resCode = re.sub(r'\s+public','\npublic',self.resCode);
        self.resCode = self.resCode.replace("class",  "\nclass");
        self.resCode = self.resCode.replace("protect","\nprotect");
        self.resCode = self.resCode.replace("private","\nprivate");
        self.resCode = self.resCode.replace("global", "\nglobal")

        self.resCode = self.resCode.replace('{ ','{\n');
        self.resCode = self.resCode.replace('}','}\n');
        self.resCode = self.resCode.replace('; ',';\n');

    def changeStrcode(self):
        self.resCode = re.sub(r"\\\\",r"\\",self.resCode);
        strlist = re.findall(r"\\\w{2,3}",self.resCode);
        for string in strlist:
            repStr = self.strdecode(string);
            self.resCode = self.resCode.replace(string, repStr);

    def strdecode(self,string):
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



    def postprocess(self):
        if "class " in self.resCode:
            parts = self.resCode.split("class ");
            if len(parts) > 1:
                parts[1] = parts[1].replace("function", "public function");
                self.resCode = "class ".join(parts) + "}//class";



obj = KhazixCrack();
print obj.render('distribution.inc.php.enc');

