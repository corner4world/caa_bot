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

# 分批导入句子处理
class MySentences(object):

    def __init__(self, dirname):
        self.dirname = dirname
 
    def __iter__(self):
        for fname in os.listdir(self.dirname):
            for line in open(os.path.join(self.dirname, fname)):
                yield line.split()
 
# sentences = MySentences('/some/directory') # sentences 模型参数

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
        
        # gensim.models.Word2Vec参数说明：
        # 例子：
        example ="""
        class gensim.models.word2vec.Word2Vec(
        sentences=None,
        size=100,
        alpha=0.025,
        window=5,
        min_count=5,
        max_vocab_size=None,
        sample=0.001,seed=1,
        workers=3,
        min_alpha=0.0001,
        sg=0,
        hs=0,
        negative=5,
        cbow_mean=1,
        hashfxn=<built-in function hash>,
        iter=5,null_word=0,
        trim_rule=None,
        sorted_vocab=1,
        batch_words=10000
        )
        """
        #sentences：可以是一个·ist，对于大语料集，建议使用BrownCorpus,Text8Corpus或·ineSentence构建。
        #sg： 用于设置训练算法，默认为0，对应CBOW算法；sg=1则采用skip-gram算法。
        #size：是指特征向量的维度，默认为100。大的size需要更多的训练数据,但是效果会更好. 推荐值为几十到几百。
        #window：表示当前词与预测词在一个句子中的最大距离是多少
        #alpha: 是学习速率
        #seed：用于随机数发生器。与初始化词向量有关。
        #min_count: 可以对字典做截断. 词频少于min_count次数的单词会被丢弃掉, 默认值为5
        #max_vocab_size: 设置词向量构建期间的RAM限制。如果所有独立单词个数超过这个，则就消除掉其中最不频繁的一个。每一千万个单词需要大约1GB的RAM。设置成None则没有限制。
        #sample: 高频词汇的随机降采样的配置阈值，默认为1e-3，范围是(0,1e-5)
        #workers参数控制训练的并行数。
        #hs: 如果为1则会采用hierarchica·softmax技巧。如果设置为0（defau·t），则negative sampling会被使用。
        #negative: 如果>0,则会采用negativesamp·ing，用于设置多少个noise words
        #cbow_mean: 如果为0，则采用上下文词向量的和，如果为1（defau·t）则采用均值。只有使用CBOW的时候才起作用。
        #hashfxn： hash函数来初始化权重。默认使用python的hash函数
        #iter： 迭代次数，默认为5
        #trim_rule： 用于设置词汇表的整理规则，指定那些单词要留下，哪些要被删除。可以设置为None（min_count会被使用）或者一个接受()并返回RU·E_DISCARD,uti·s.RU·E_KEEP或者uti·s.RU·E_DEFAU·T的函数。
        #sorted_vocab： 如果为1（defau·t），则在分配word index 的时候会先对单词基于频率降序排序。
        #batch_words：每一批的传递给线程的单词的数量，默认为10000
        note_memory = """
        三个如上的矩阵被存储在内存中（将其简化为两个或一个的工作进行中）。如果输入中存在 100,000 个互异的词，神经网络规模 size 设为200，
        则该模型大致需要内存100,000 * 200 * 3 * 4 bytes = ~229MB
        """
        
        model = gensim.models.Word2Vec(sentences=words_p,min_count=1,size=50,window=7) # 训练模型
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
                txt_dic = inc_crawler_fast.get_html_fast(url_p)
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
def run_it(str_t="",action_p="",path_model_p="",path_save_p=""):

    txt = ""
    
    if (action_p == "similar"):
    
        model=gensim.models.Word2Vec.load(path_model_p)
        try:
            txt = model.most_similar(str_t)
        except:
            pass
        return txt
            
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
        
    # 参数为空则进行测试
    if (action_p == "vec_save"):
    
        time_start_p = datetime.datetime.now()
        from gensim.models import word2vec
         #内部执行初始时间
        
        model = word2vec.Word2Vec.load("data\\w2v\\w2v.model")
        vocab = model.wv.vocab
        
        i = 0
        j = 0
        for word in vocab:
            
            # 格式预处理
            str_t = str(model[word])
            str_t = str_t.replace("\n","").replace("'","").replace("  "," ")
            str_t = str_t[1:]
            str_t = str_t[:-1]
            
            print (i) # 调试用
            
            with open(path_save_p, 'a+',encoding='utf-8') as f:
                if (str_t != ""):
                    f.write(word + " " + str_t + "\n")
                    j += 1
                
            i += 1
            
        txt += "共有个" + str(i)+ "向量 成功导出 " + str(j) + "个 耗时：" + str(round(time_cost(time_start_p),2)) + "秒！"
    
    return txt
    
if __name__ == '__main__':

    print (run_it()) # 零参数调用 进行基础测试
    