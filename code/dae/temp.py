#!/usr/bin/env python
# -*- coding: UTF-8 -*-  

'''
{
"版权":"LDAE工作室",
"author":{
"1":"一世纪末",
"2":"吉更",
}
"初创时间:"2017年3月",
}
'''

#--------- 外部模块处理<<开始>> ---------#

#-----系统自带必备模块引用-----
import sys
import csv
import warnings
warnings.filterwarnings(action='ignore', category=UserWarning, module='gensim')
import gensim
import pickle
import datetime # 日期模块

#-----系统外部需安装库模块引用-----
import jieba


#-----DIY自定义库模块引用-----
import config #系统配置参数
from diy.inc_sys import * #自定义系统级功能模块
from diy.inc_conn import * #自定义数据库功能模块
import diy.inc_crawler_fast as inc_crawler_fast # 引入快速爬虫模块 用于API解析中间件

# ---全局变量处理
jieba.default_logger.setLevel('ERROR') #结巴分词 自动纠错
#import jieba.posseg as pseg #引入词性标注模式
user_dic_path = config.dic_config["path_jieba_dic"]
jieba.load_userdict(user_dic_path)# 导入专用字典

# word2vec对象
class W2v(object):
    
    # 数据装载
    def get_data(self,path_1="",path_2="",clear_if=1,dim=0):
        
        csv_file_1=open(path_1,'r',encoding='utf-8')
        csv_file_2=open(path_2,'r',encoding='utf-8')
        data_1=csv.reader(csv_file_1)
        data_2=csv.reader(csv_file_2)
        
        DATA=[]
        
        for item in data_1:
            try:
                DATA.append(item[dim])
            except:
                pass

        for item in data_2:
            try:
                DATA.append(item[dim])
            except:
                pass
                
        fin_DATA=[]
        list_t = []
        if (clear_if):
        
            for ele in DATA:
                list_t = jieba.cut(ele)
                for x in list_t:
                    if (len(x) > 1):
                        fin_DATA.append(x)
        else:
        
            for ele in DATA:
                fin_DATA.append([w for w in jieba.cut(ele)])
                #pickle.dump(fin_DATA,open("fin_data.p",'w'))
        return fin_DATA
    # 训练词向量
    def train_w2v(self,words_p=[],path_r_p="w2v.model",path_s_p="\\data\\w2v\\"):
        
        time_start_p = datetime.datetime.now() #内部执行初始时间
        
        txt = "生成 "
        
        if (words_p):
            pass
        else:
            words_p = self.get_data(path_1=config.path_main + path_s_p + "question_no_seg.csv",path_2=config.path_main + path_s_p + "answer_no_seg.csv",clear_if=0,dim=0)

        model = gensim.models.Word2Vec(words_p, min_count=1,size=50,window=7) # 训练模型
        model.save(config.path_main + path_s_p + path_r_p) # 保存模型

        txt += config.path_main + path_s_p + path_r_p
        txt += " 成功 "
        txt += "耗时：" + str(round(time_cost(time_start_p),2)) + "秒！"
        
        return txt
        
# 词的基础处理
class Vec(object):

    # 近义词相关词处理
    def sm(self,table_name="similar",numb_len=6,model_p="sm",top_p=3):
        
        txt = ""
        str_t = ""
        txt_dic = ""
        list_t = []
        list_t2 = []
        
        sql = "select keyword,id from " + table_name + " where v1=0"
        #sql += " limit 10" # 调试用
        res, rows = rs_basedata_mysql.read_sql(sql)
        if (res>0):
            numb_all =res
        else:
            return ("近似词库为空或数据库读取错误")
        
        count_t = 1
        for row in rows:
        
            # 打上访问标记
            sql = "update " + table_name + " set v1=1 where id=" + str(row[1])
            print (sql) # 调试用
            updtae_if = rs_basedata_mysql.write_sql(sql)
            
            txt_dic = ""
            list_t = []
            str_t = row[0]
            
            if (str_t):
                str_t = str_t.strip()
                str_t = str_t[0:numb_len]
            else:
                continue
            try:
                print (count_t,str_t)# 调试用
            except:
                pass
            # 微服务请求网址
            url_p = config.dic_config["url_api"] + "api?action=" + model_p + "&q=" + str_t
            
            try:
                print (url_p) # 调试用
                txt_dic = inc_crawler_fast.get_html_get(url_p)
            except:
                pass
                
            if (txt_dic == ""):
                continue
            else:
                try:
                    print (txt_dic) # 调试用
                except:
                    pass
                txt_dic = txt_dic.replace("{","")
                txt_dic = txt_dic.replace("}","")
                txt_dic = txt_dic.replace("\"","")
                list_t = txt_dic.split(",")
                
                if (list_t):
                
                    sql = "update " + table_name + " set "
                    
                    i = 1
                    for x in list_t:
                        list_t2 = []
                        if (i > top_p):
                            break
                        list_t2 = x.split(":")
                        if (str_t != list_t2[0].strip()):
                            try:
                                sql += " sm" + str(i) + "='" + list_t2[0] + "',r" + str(i) + "=" + str(round(float(list_t2[1]),8)) + ","
                            except:
                                pass
                        i+=1
                        
                    sql = sql[0:-1]
                    sql +=" where id=" + str(row[1]) 
                #print (sql) # 调试用
                updtae_if = rs_basedata_mysql.write_sql(sql)
                
            print ("第 " + str(count_t) + " 次操作，完成率：" + str(round(count_t*100/numb_all,2)) + "%")
            count_t += 1
            
        txt = sql
        return txt

# 主执行调用入口函数
def run_it(str_t="",action_p="similar",path_model_p="./data/w2v/w2v.model"):
    txt = ""
    if (str_t):
        pass
    else:
        return txt
        
    if (action_p == "similar"):
        model=gensim.models.Word2Vec.load(path_model_p)
        try:
            txt = model.most_similar(str_t)
        except:
            pass
    if (action_p == "train_w2v"):
        txt = ""
        w2v = W2v()
        txt = w2v.train_w2v()
        return txt
        
    if (action_p == "vec_sm"):
        txt = "hello"
        vec = Vec()
        txt = vec.sm(table_name=str_t)
        return txt
    #words=get_data(path_1="./data/w2v/question_no_seg.csv",path_2="./data/w2v/answer_no_seg.csv",clear_if=1,dim=0)
    #get_data(words_p=words,path_r_p="./data/w2v/w2v.model")
    
    #train_w2v()
    #model=gensim.models.KeyedVectors.load_word2vec_format("./Model/w2v.model",binary=True,unicode_errors="ignore")
    
    #print(model["癌症"])
    
    return txt
    
if __name__ == '__main__':
    print ("") # 防止代码泄漏只输出空字符 
    