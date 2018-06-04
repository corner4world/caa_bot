#!/usr/bin/env python
# -*- coding: UTF-8 -*-  

'''
{
"版权":"LDAE工作室",
"author":{
"1":"腾辉",
"2":"吉更"
"3":"MLtf"
}
"初创时间:"2017年3月",
}
'''

# 相似度类
class Similar(object):

    # 比对词向量的构造
    def vector_cos_word(self,list_v1=[],list_v2=[]):
        
        list_v1_out = []
        list_v2_out = []
        list_b = list_v1 + list_v2
        list_s = sorted(set(list_b),key=list_b.index) # 去重排序
        
        #print(list_s,"\n",list_v1,"\n",list_v2) # 调试用
        
        for x in list_s:
        
            list_v1_out.append(list_v1.count(x))
            list_v2_out.append(list_v2.count(x))
                
        #print(list_s,list_v1_out,list_v2_out) # 调试用
                
        return list_v1_out,list_v2_out
            
    
    # 词向量余弦相似度计算
    def cos_word(self,sim_1=[],sim_2=[]):
    
        sim_value = -1 # 相似度值赋初值 1 完全相似 -1 完全相反

        pow_1 = 0
        pow_2 = 0
        inner_product = 0
        list_em = []  # 标准向量
        import math
        
        sim_1,sim_2 = self.vector_cos_word(list_v1=sim_1,list_v2=sim_2)
        #print(sim_1,sim_2)
        for i in range(len(sim_1)):
            #print(i) # 调试用
            inner_product += sim_1[i] * sim_2[i]
            pow_1 += sim_1[i]**2
            pow_2 += sim_2[i]**2
        #print ("inner_product=",inner_product**2,"pow_1*pow_2=",pow_1*pow_2)
        sim_value = round(inner_product/(math.sqrt(pow_1*pow_2)),10) # 保留小数点后10位
        
        return sim_value

# 文本抽取类
class Extract_txt(object):

    #对文本按自然段分段 mark_p 为自然分段标记符列表
    def div_cut(self,content_p="",mark_p=["']\"","</p>","</div>"]):
    
        list_t = []
        
        # 自然分段标记处理
        for x in mark_p:
            content_p = content_p.replace(x,"\n")
            
        content_p = content_p.replace("\r\n","\n")
        #print (content_p.count("\n")) # 调试用
        list_t = content_p.split("\n")
        
        return list_t

    #对含标点的文本分句
    def sentence_cut(self,content_p,father_if=1):
    
        import  re # 引用正则库
        # 主句与子句分割
        
        if (father_if == 1):
            cutlist =['。','？','！']
        else:
            cutlist =['，','；','：','”']
            
        content_p = content_p.replace("["," ")
        content_p = content_p.replace("]"," ")
        content_p = content_p.replace("'"," ")
        content_p = content_p.replace("\""," ")
            
        # 对汉语标点符号的错误进行纠正
        if (father_if == 1):
            content_p = content_p.replace("?","？")
            content_p = content_p.replace("!","！")
        else:
            content_p = content_p.replace(":","：")
            
        pat = re.compile('\s+')
        content_p=re.sub(pat,'',content_p)
        
        bst=[content_p]
        est=[]
        
        for flag in cutlist:
            for a in bst:
                est.extend(a.split(flag))
            bst,est=est,[]
            
        return bst
        
    # 获得自然段——主句映射字典
    def sentence_div_main_get(self,content_p=""):
        
        dic_div ={} # 自然段落字典
        dic_sen_main = {} # 主句字典
        list_t = [] # 临时队列
        list_t = self.div_cut(content_p=content_p) # 自然段分段
        #print ("分段结果：",len(list_t))
        i = 1
        for x in list_t:
            dic_div[i] = x
            i +=1
        j = 1
        # 主句分割 并建立在字典建立索引
        while (j < i):
            list_t = []
            #print(j,dic_div[j]) #调试用
            list_t = self.sentence_cut(dic_div[j],father_if=1)
            #print ("自然段的主句切割：",list_t,type(list_t)) # 调试用
            dic_sen_main[j]=list_t
            j += 1
            
        return dic_sen_main

#---------- 主过程<<开始>> -----------#
def main():

    print ("")  # 防止代码外泄 只输出一个空字符

if __name__ == '__main__':
    main()
#---------- 主过程<<结束>> -----------#