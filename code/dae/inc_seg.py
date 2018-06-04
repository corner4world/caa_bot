#!/usr/bin/env python

# -*- coding: UTF-8 -*-  

'''

{

"版权":"LDAE工作室",

"author":{

"1":"出门向右",
"2":"吉更",

}

"初创时间:"2017年3月",

}

'''

#--------- 外部模块处理<<开始>> ---------#

#-----系统自带必备模块引用-----

import sys # 操作系统模块1

#-----系统外部需安装库模块引用-----

import jieba # 引入结巴分词类库 第三方库

#-----DIY自定义库模块引用-----
import config #系统配置参数

# ---全局变量处理
jieba.default_logger.setLevel('ERROR') #结巴分词 自动纠错
import jieba.posseg as pseg #引入词性标注模式
user_dic_path = config.dic_config["path_jieba_dic"]
jieba.load_userdict(user_dic_path)# 导入专用字典

#--------- 内部模块处理<<开始>> ---------#

# nlp基础类
class Nlp_base(object):

    # 自然分段
    def nature_paragraph(self,txt_p="",list_p=[],ignore_list=[]):
        
        if (len(list_p) == 0):
        
            list_p = [
            "'",
            "\n",
            "\"",
            ",",
            "（",
            "）",
            "(",
            ")",
            "，",
            "。",
            "；",
            "“",
            "”",
            "（",
            "）",
            "？",
            "：",
            "《",
            "》",
            "『",
            "』",
            "[",
            "]",
            "！",
            "、",
            "\\",
            "=",
            "×",
            "÷",
            "+",
            "-",
            "≈",
            "【",
            "】",
            "〖",
            "〗",
            "[",
            "]",
            "｛",
            "｝",
            "?",
            "±",
            "/",
            "≌",
            "∽",
            "∪",
            "∩",
            "∈",
            "\r\n", 
            "\n",
            "\r",
            " ",
            "  ",
            "|",
            "_",
            ]
        
        # 利用标点和特殊符号分段
        for x in list_p:
            txt_p = txt_p.replace(x,"\n" + x + "\n")
        
        # 停用词初滤
        for x in ignore_list:
            txt_p = txt_p.replace(x,"")
        
        return txt_p

# 分词
class Segment(Nlp_base):

    def __init__(self,txt_p="",threshold_p=0,way_p="precise"):
    
        self.txt_p = txt_p
        self.threshold_p = threshold_p
        self.way_p = way_p
        
    # 自然分段
    
    def section_nature(self,txt_p):
        pass
        
    # 自然分词
    def seg_nature(self):
        pass

    # 结巴中文分词
    def seg_jieba(self,txt_p="",way_p=""):
        
        if (txt_p == ""):
            txt_p = self.txt_p
        
        if (way_p == ""):
            way_p = self.way_p
        
        list_p = []

        if (len(txt_p) == 0):
            return list_p
        
        #  搜索引擎模式
        if (way_p == "search"):
            try:
                list_p = jieba.cut_for_search(txt_p)
            except:
                list_p = []
                
        # 默认 精确模式   
        if (way_p == "precise"):
        
            try:
                list_p = jieba.cut(txt_p)
            except:
                list_p = []
                
        # 全模式   
        if (way_p == "all"):
            try:
                list_p = jieba.cut(txt_p,cut_all=True)
            except:
                list_p = []
                
        # 标注模式   
        if (way_p == "pseg"):
            try:
                list_p = pseg.cut(txt_p)
            except:
                list_p = []
                
        return list_p
        
    # 主分词方法
    def seg_main(self,txt_p="",threshold_p=0,way_p="precise"):
        
        list_s = []
        str_t = ""
        list_last = []
        list_t = []
    
        if (txt_p == ""):
            txt_p = self.txt_p
            
        if (threshold_p == ""):
            threshold_p = self.threshold_p
        
        if (way_p == ""):
            way_p = self.way_p
            
        # 自然分段
        str_t = self.nature_paragraph(txt_p)
        list_s = str_t.split("\n")
        for x in list_s:
            if (len(x) < 2):
                list_last.append(x)
            else:
                
                # 阈值自然分词
                if (len(x) <= threshold_p):
                    list_last.append(x)
                else:
                    # 标准分词
                    list_t = self.seg_jieba(txt_p=x)
                    for y in list_t:
                        list_last.append(y)
        
        return list_last
        
#--------- 内部模块处理<<结束>> ---------#

if __name__ == '__main__':
    
    print ("")

    





