#!/usr/bin/env python
# -*- coding: UTF-8 -*-  

'''
{
"版权":"LDAE工作室",
"author":{
"1":"集体",
}
"初创时间:"2017年3月",
}
'''

#--------- 外部模块处理<<开始>> ---------#

# ---全局变量处理
import sys # 操作系统模块1
sys.path.append("..")
import config #系统配置参数

#-----系统自带必备模块引用-----

import os # 操作系统模块2
import types # 数据类型
import time # 时间模块
import datetime # 日期模块
import math # 数学模块

#-----系统外部需安装库模块引用-----

import numpy as np # numpy开源的数值计算扩展
import operator # 内置操作符的函数接口
from numpy import * # numpy开源的数值计算扩展
import matplotlib.pyplot as plt # 可视化工具的pyplot绘图模块

#-----DIY自定义库模块引用-----

sys.path.append("diy")
from inc_sys import * #自定义系统级功能模块 
from inc_conn import * #自定义数据库功能模块
import diy.inc_nlp as inc_nlp # 自然语言处理模块

#--------- 外部模块处理<<结束>> ---------#


#--------- 内部模块处理<<开始>> ---------#

# ---外部参变量处理



# ---本模块内部类或函数定义区

# 模型训练的基类
class Dae_base (object):

    def __init__(self):
        self.eps = 1.0e-6
        self.alpha = 0.001 # 步长
        self.steps = 16  # 迭代次数

    def savefile(self,savepath,content):
        fp = open(savepath,"wb")
        fp.write(content)
        fp.close()

    # 基础数据文件转矩阵
    # path: 数据文件路径
    # delimiter: 文件分隔符
    def file2matrix(self,path,delimiter):
        
        list_t1 = []
        list_t2 = []
        recordlist = []
        
        fp = open(path,"r") # 读取文件内容
        content = fp.read()
        fp.close()
        rowlist = content.splitlines() # 按行转换为一维表
        #print (rowlist) #调试用
        # 逐行遍历 结果按分隔符分割为行向量
        for row in rowlist:
            list_t2 = []
            if row.strip():
                list_t1 = row.split(delimiter)
                for y in list_t1:
                    y = y.replace("'","")
                    y = float(y)
                    list_t2.append(y)
                
                recordlist.append(list_t2)
        #print (recordlist) #调试用
        
        return mat(recordlist)# 返回转换后的矩阵形式
    # 权重数据文件转矩阵
    def weights2matrix(self,path_input_p,delimiter):
        
        list_t1 = []
        list_t2 = []
        recordlist = []
        
        fp = open(path_input_p,"r") # 读取文件内容
        content = fp.read()
        fp.close()
        rowlist = content.splitlines() # 按行转换为一维表
        #print (rowlist) #调试用
        # 逐行遍历 结果按分隔符分割为行向量
        for row in rowlist:
            list_t2 = []
            if row.strip():
                list_t1 = row.split(delimiter)
                for y in list_t1:
                    y = y.replace("'","")
                    y = float(y)
                    list_t2 = [y]
                    recordlist.append(list_t2)
                
        return recordlist
        
    # 欧氏距离
    def distEclud(self,vecA, vecB):
        return linalg.norm(vecA-vecB)+self.eps 
    
    # 相关系数
    def distCorrcoef(self,vecA, vecB):
        return corrcoef(vecA, vecB, rowvar = 0)[0][1]

    # Jaccard距离
    def distJaccard(self,vecA, vecB):
        temp = mat([array(vecA.tolist()[0]),array(vecB.tolist()[0])])
        return dist.pdist(temp,'jaccard')

    # 余弦相似度
    def cosSim(self,vecA, vecB):
        return (dot(vecA,vecB.T)/((linalg.norm(vecA)*linalg.norm(vecB))+eps))[0,0]

    # 绘制散点图    
    def drawScatter(self,plt,mydata,size=20,color='blue',mrkr='o'):
        m,n = shape(mydata)
        if (m>n and m>2):
            plt.scatter(mydata.T[0],mydata.T[1],s=size,c=color,marker=mrkr)   
        else:
            plt.scatter(mydata[0],mydata[1],s=size,c=color,marker=mrkr)   

    # 绘制分类点
    def drawScatterbyLabel(self,plt,Input):
        m,n=shape(Input)
        target = Input[:,-1] 
        for i in range(m):
            if target[i][0]==0:
                plt.scatter(Input[i,0],Input[i,1],c='blue',marker='o')
            else:
                plt.scatter(Input[i,0],Input[i,1],c='red',marker='s')


    # 硬限幅函数
    def hardlim(self,dataSet):
        dataSet[nonzero(dataSet.A>0)[0]]=1
        dataSet[nonzero(dataSet.A<=0)[0]]=0
        return dataSet

    # Logistic函数
    def logistic(self,wTx):
        return 1.0/(1.0+exp(-wTx))

    def buildMat(self,dataSet):
        m,n=shape(dataSet)
        dataMat = zeros((m,n))
        dataMat[:,0] = 1 
        dataMat[:,1:] = dataSet[:,:-1]
        return dataMat

    # 二元分类函数
    def classifier_two(self,testData, weights,output_p = 0):
        
        prob = 0 # 概率初值
        
        #print (testData) # 测试用
        #print (weights) # 测试用
        #print (sum(testData*weights)) # 测试用
        
        prob = self.logistic(sum(testData*weights)) # 求取概率--判别算法
        
        #print ("预测的概率",prob) # 测试用
        # 单独输出概率值
        if (output_p == 1):
            return prob
            
        if (prob > 0.5): 
            return 1.0 # prob>0.5 返回为1
        else: 
            return 0.0          # prob<=0.5 返回为0

    # 最小二乘回归，用于测试    
    def standRegres(self,xArr,yArr):
        xMat = mat(ones((len(xArr),2)))
        yMat = mat(ones((len(yArr),1)))
        xMat[:,1:] = (mat(xArr).T)[:,0:]
        yMat[:,0:] = (mat(yArr).T)[:,0:]
        xTx = xMat.T*xMat
        if linalg.det(xTx) == 0.0:
            print ("This matrix is singular, cannot do inverse")
            return
            ws = xTx.I * (xMat.T*yMat)
            return ws
            
    # tf_idf计算
    def tf_idf(self,nump_tf_p=0,numb_div_p=1,numb_all_p=0.00000001,numb_idf_p=1):
        value_p = 0
        value_p = (nump_tf_p/numb_div_p)*math.log(numb_all_p/numb_idf_p)
        return value_p

# 特征基础类
class Feature_base(object):
    
    def __init__(self):
        self.test = "hello world!"
        self.dic_punctuation = dic_txt_make(path_p=config.dic_config["path_dic"]  +  "dic_punctuation.txt",what_is=1) # 标点符号队列型字典装载
        self.dic_feeling = dic_txt_make(path_p=config.dic_config["path_dic"]  +  "dic_feeling.txt",what_is=3) # 语气词字典装载
        self.dic_ne = dic_txt_make(path_p=config.dic_config["path_dic"]  +  "dic_ne.txt",what_is=3) # 标准命名实体字典装载
        self.dic_guide = dic_txt_make(path_p=config.dic_config["path_dic"]  +  "dic_guide.txt",what_is=3) # 引导词字典装载
        self.dic_query = dic_txt_make(path_p=config.dic_config["path_dic"]  +  "dic_query.txt",what_is=3) # 疑问词字典装载
        self.dic_verb = dic_txt_make(path_p=config.dic_config["path_dic"]  +  "dic_verb.txt",what_is=3) # 领域动词字典装载
        self.dic_em = dic_txt_make(path_p=config.dic_config["path_dic"]  +  "dic_em.txt",what_is=3) # 情感字典装载
        self.dic_cost = dic_txt_make(path_p=config.dic_config["path_dic"]  +  "dic_cost.txt",what_is=3) # 领域经济词字典装载
        
    # 问题分型特征采集
    def value_get(self,str_t="",dim_p=16):
        
        list_w = []
        list_t = ""
        
        try:
            list_t = eval(str_t)
        except:
            pass
       
        if (isinstance(list_t,list)):
            
            list_w = list_t
            str_t = ""
            for x in list_w:
                str_t += x
            
        else:
        
            seg = inc_nlp.Segment()  # 分词对象实例化
            if (str_t):
                list_w = seg.seg_jieba(str_t) #采用默认分词方法
            else:
                return dic_f

        dic_f = {}
        str_t2 = str_t
        str_t3 = ""
        arr_t = ""
        len_avg_q = 0
        
        
        if (list_w):
        
            for i in range(dim_p):
                dic_f["f" + str(i+1)] = 0
            
            # 1 字符串长度 
            if (dim_p >= 1):
                dic_f["f1"] = len(str_t)
            
            # 2 标点符号数
            if (dim_p >= 2):
                if (self.dic_punctuation):
                    for x in self.dic_punctuation:
                        dic_f["f2"] += str_t.count(x)
                        str_t2 = str_t2.replace(x,"@~@")
                    
            # 3 标点符号自然分句的平均长度
            if (dim_p >= 3):
                arr_t = str_t2.split("@~@")
                if arr_t:
                    i = 0
                    for x in arr_t:
                        str_t3 = x.strip()
                        if (len(str_t3) > 0):
                            #print (i,x,len(str_t3))#调试用
                            len_avg_q +=len(str_t3)
                            i += 1
                    dic_f["f3"] = int(len_avg_q/i)
                
            # 4 特殊标点数
            if (dim_p >= 4):
                dic_f["f4"] += str_t.count("!")
                dic_f["f4"] += str_t.count("?")
                dic_f["f4"] += str_t.count("！")
                dic_f["f4"] += str_t.count("？")
            
            # 5-15 分词处理后及相关特征的匹配处理
            
            if (dim_p > 5):
                i = 1
                for x in list_w:
                    #print (x) #调试用
                    
                    
                    #5 语气词数 (吗，么，哦......由语气助词字典判别)
                    if x in self.dic_feeling:
                        if (dim_p >= 5):
                            dic_f["f5"] += 1
                            
                    #6 疑问词数 （是什么，怎么，如何，由疑问词字典判别）
                    if x in self.dic_query:
                        if (dim_p >= 6):
                            dic_f["f6"] += 1
                            
                    #7 情感正负面词数（良好，恶性....由情感词字典判别）
                    #8 情感词在分词队列中的位置的和
                    if x in self.dic_em:
                        if (dim_p >= 7):
                            dic_f["f7"] += 1
                        if (dim_p >= 8):
                            dic_f["f8"] += i
                    
                    #9 英文与数字词数
                    if (x.encode( 'UTF-8' ).isdigit()):
                        if (dim_p >= 9):
                            dic_f["f9"] += 1
                    if (x.encode( 'UTF-8' ).isalpha()):
                        if (dim_p >= 9):
                            dic_f["f9"] += 1
                            
                    #10 经济敏感词（花费，需要多少钱，数词+货币单位组合.....，由经济字典判别）
                    if x in self.dic_cost:
                        if (dim_p >= 10):
                            dic_f["f10"] += 1
                            
                    #11 引导词数（由引导字典判别）
                    if x in self.dic_guide:
                        if (dim_p >= 11):
                            dic_f["f11"] += 1
                    #13 专业标定动词词数（由专业标定词字典判别）
                    if x in self.dic_verb:
                        if (dim_p >= 13):
                            dic_f["f13"] += 1
                    
                    #14 领域主题（命名实体）词数（由专业词字典判别）
                    #15 领域主题词（命名实体）在分词队列中的位置的和
                    if x in self.dic_ne:
                        if (dim_p >= 14):
                            dic_f["f7"] += 1
                        if (dim_p >= 15):
                            dic_f["f15"] += i
                        
                    i += 1
                
                #16 文本共有多少分词数
                if (dim_p == 16):
                    dic_f["f6"] = i-1

            list_t = ["年","月","岁","日"]
            
            #12 存活词数（年，月，日，多长时间，生存率  由存活词字典判别）
            if (dim_p >= 12):
                for y in list_t:
                    if (y in x):
                        dic_f["f12"] += 1

        return dic_f
        
    # min-max(极值)归一
    def dim_get_max_min(self,row_p=(),which_p=1,name_table_p="feature_train_txt",rows_max=(),rows_min=(),numb_dim=16):
        
        dic_d = {}
        numb_t = 0
        numb_t2 = 0
        
        # 空值校验
        if (row_p):
            pass
        else:
            return dic_d
        
        # 空值校验
        if (rows_max and rows_min):
            pass
        else:
            return dic_d
        
        if (which_p == 1):
        
            j = 1
            for x in row_p:
            
                numb_t = rows_max[0][j-1] - rows_min[0][j-1]
                
                if (numb_t > 0):
                    numb_t2 = (x - rows_min[0][j-1])/numb_t
                    numb_t2 = round(numb_t2,8)
                    dic_d["f" + str(j)] = numb_t2
                else:
                    dic_d["f" + str(j)] = 0
                    
                if (j == numb_dim):
                    break
                
                j += 1
        
        return dic_d
        
    # Z-score(标准化)归一
    def dim_get_stand(self,row_p=(),which_p=2,name_table_p="feature_train_txt",rows_avg=(),rows_std=(),numb_dim=16):
        
        dic_d = {}
        numb_t = 0
        numb_t2 = 0

        if (which_p == 2):
        
            j = 1
            for x in row_p:
            
                numb_t = rows_std[0][j-1]
                
                if (numb_t > 0):
                    numb_t2 = (x - rows_avg[0][j-1])/numb_t
                    numb_t2 = round(numb_t2,8)
                    dic_d["f" + str(j)] = numb_t2
                else:
                    dic_d["f" + str(j)] = 0
                    
                if (j == numb_dim):
                    break
                
                j += 1
                
        return dic_d
        
    # 数据库批处理无量纲化
    def dim_db_make(self,name_table_p="feature_train_txt",row_feature_p=16,limit_p=0,which_p=2):
    
        txt = "数据库批处理无量纲化"
        dic_d = {}
        sql = "select "
        
        #rs_sqlite_file = Conn_sqlite3(config.path_main + config.dic_config["path_sqlite"],0) # 生成文件数据库实例
        #rs_way_mysql = Conn_mysql(config.dic_config["host_mysql"],config.dic_config["user_mysql"],config.dic_config["pwd_mysql"], "ldae_way_" + config.dic_config["name_mysql_after"], int(config.dic_config["port_mysql"])) # 生成MYSQL数据库way方法实例
        rs_basedata_mysql = Conn_mysql(config.dic_config["host_mysql"],config.dic_config["user_mysql"],config.dic_config["pwd_mysql"], "ldae_basedata_" + config.dic_config["name_mysql_after"], int(config.dic_config["port_mysql"])) # 生成MYSQL数据库基础数据实例
        #rs_index_mysql = Conn_mysql(config.dic_config["host_mysql"],config.dic_config["user_mysql"],config.dic_config["pwd_mysql"], "ldae_index_" + config.dic_config["name_mysql_after"], int(config.dic_config["port_mysql"])) # 生成MYSQL数据库索引数据实例
        
        # min-max(极值)归一
        if (which_p == 1):
        # 调用特征项
            for i in range(0,row_feature_p):
                sql += "min(f" + str(i+1) +"),"
            sql = sql[:-1]
            sql += " from " + name_table_p + ""
            if (limit_p > 0):
                sql += " limit " + str(limit_p)
            res_min, rows_min = rs_basedata_mysql.read_sql(sql)
            if (res_min < 1):
                return "特征库无内容或数据库读取失败"
            #print (rows_min) #调试用 
            
            # 生成特征分类器参数文件
            f = open(config.dic_config["path_f"] + "feature_min.txt", "w")
            f.write(str(rows_min))
            f.close()
            
            sql = "select "
            for i in range(0,row_feature_p):
                sql += "max(f" + str(i+1) +"),"
            sql = sql[:-1]
            sql += " from " + name_table_p + ""
            if (limit_p > 0):
                sql += " limit " + str(limit_p)
            res_max, rows_max = rs_basedata_mysql.read_sql(sql)
            if (res_max < 1):
                return "特征库无内容或数据库读取失败"
            #print (rows_max) #调试用
            # 生成特征分类器参数文件
            f = open(config.dic_config["path_f"] + "feature_max.txt", "w")
            f.write(str(rows_max))
            f.close()
            
            # 计算回写数据库
            sql = "select "
            for i in range(0,row_feature_p):
                sql += "f" + str(i+1) +","
            sql += "id from " + name_table_p + " where v2=0 order by id"
            res, rows = rs_basedata_mysql.read_sql(sql)
            i = 1
            for row in rows:
        
                dic_d ={}
                dic_d = self.dim_get_max_min(row_p=row,which_p=1,name_table_p=name_table_p,rows_max=rows_max,rows_min=rows_min,numb_dim=row_feature_p)
            
                sql = "update " + name_table_p + "  set "
                for y in dic_d:
                    sql += y + "=" + str(dic_d[y]) + ","
                sql += "v2=1 where id=" + str(row[row_feature_p])
                update_if = rs_basedata_mysql.write_sql(sql)
                #print (i,sql) # 调试用
                i += 1
        
        # Z-score(标准化)归一
        if (which_p == 2):
        
            # 求均值 
            sql = "select "
            for i in range(0,row_feature_p):
                sql += "avg(f" + str(i+1) +"),"
            sql = sql[:-1]
            sql += " from " + name_table_p + " order by id"
            
            if (limit_p > 0):
                sql += " limit " + str(limit_p)
            res_avg, rows_avg = rs_basedata_mysql.read_sql(sql)
            if (res_avg < 1):
                return "特征库无内容或数据库读取失败"
            # 生成特征分类器参数文件
            f = open(config.dic_config["path_f"] + "feature_avg.txt", "w")
            f.write(str(rows_avg))
            f.close()
            
            # 求标准差
            sql = "select "
            for i in range(0,row_feature_p):
                sql += "STDDEV_SAMP(f" + str(i+1) +"),"
            sql = sql[:-1]
            sql += " from " + name_table_p + "" 
            res_std, rows_std = rs_basedata_mysql.read_sql(sql)
            if (res_std < 1):
                return "特征库无内容或数据库读取失败"
            # 生成特征分类器参数文件
            f = open(config.dic_config["path_f"] + "feature_std.txt", "w")
            f.write(str(rows_std))
            f.close()
            
            #print ("均值",rows_avg,"\n","标准差",rows_std)#调试用
            
            # 计算回写数据库
            sql = "select "
            for i in range(0,row_feature_p):
                sql += "f" + str(i+1) +","
            sql += "id from " + name_table_p + " where v2=0 order by id"
            res, rows = rs_basedata_mysql.read_sql(sql)
            res,rows = rs_basedata_mysql.read_sql(sql)
            if (res_std < 1):
                return "数据处理完毕或数据库读取失败"
            i = 1
            for row in rows:
        
                dic_d ={}
                
                dic_d = self.dim_get_stand(row_p=row,which_p=2,name_table_p=name_table_p,rows_avg=rows_avg,rows_std=rows_std,numb_dim=row_feature_p)
                
                sql = "update " + name_table_p + "  set "
                for y in dic_d:
                    sql += y + "=" + str(dic_d[y]) + ","
                sql += "v2=1 where id=" + str(row[row_feature_p])
                update_if = rs_basedata_mysql.write_sql(sql)
                #print (i,sql) # 调试用
                i += 1
        
        rs_basedata_mysql.close_cur() #关闭数据游标
        rs_basedata_mysql.close() #关闭数据连接
        
        return txt
    
    # 数据库特征批处理生成
    def value_db_make(self,name_table_p="feature_train_txt",row_feature_p=16,limit_p=0,dim_p=16):
    
        txt = "数据库特征批处理生成"
        id = 0
        dic_f ={}
        
        #rs_sqlite_file = Conn_sqlite3(config.path_main + config.dic_config["path_sqlite"],0) # 生成文件数据库实例
        #rs_way_mysql = Conn_mysql(config.dic_config["host_mysql"],config.dic_config["user_mysql"],config.dic_config["pwd_mysql"], "ldae_way_" + config.dic_config["name_mysql_after"], int(config.dic_config["port_mysql"])) # 生成MYSQL数据库way方法实例
        rs_basedata_mysql = Conn_mysql(config.dic_config["host_mysql"],config.dic_config["user_mysql"],config.dic_config["pwd_mysql"], "ldae_basedata_" + config.dic_config["name_mysql_after"], int(config.dic_config["port_mysql"])) # 生成MYSQL数据库基础数据实例
        #rs_index_mysql = Conn_mysql(config.dic_config["host_mysql"],config.dic_config["user_mysql"],config.dic_config["pwd_mysql"], "ldae_index_" + config.dic_config["name_mysql_after"], int(config.dic_config["port_mysql"])) # 生成MYSQL数据库索引数据实例
        
        # 调用特征项
        sql = "select "
        for i in range(0,row_feature_p):
            sql += "f" + str(i+1) +","
        sql += "id,question from " + name_table_p + " where v1=0"
        #print (sql) # 调试用
        if (limit_p > 0):
            sql += " limit " + str(limit_p)
        res, rows = rs_basedata_mysql.read_sql(sql)
        if (res < 1):
            return "特征库无内容或数据库读取失败"
        
        for row in rows:

            # 更新原始特征值
            dic_f = self.value_get(str_t=row[row_feature_p+1],dim_p=row_feature_p)
            if (dic_f):
                sql = "update " + name_table_p + " set "
                for y in dic_f:
                    sql += y + "=" + str(dic_f[y]) + ","
                sql += "v1=1 where id=" + str(row[row_feature_p])
                update_if = rs_basedata_mysql.write_sql(sql)
        
        rs_basedata_mysql.close_cur() #关闭数据游标
        rs_basedata_mysql.close() #关闭数据连接
        
        return txt

# 训练主类
class Train_dae(Dae_base,Feature_base):

    # 由数据库生成训练文件
    def csv_train_lr(self,path_out_p="../data/dae/train_lr_",which_p=1,name_table_train_p="feature_train_txt",name_table_test_p="feature_test_txt",row_feature_p=16,dim_p=2):
        
        txt = ""
        txt_csv = ""
        sql = "select "
        j = 1
        
        #rs_sqlite_file = Conn_sqlite3(config.path_main + config.dic_config["path_sqlite"],0) # 生成文件数据库实例
        #rs_way_mysql = Conn_mysql(config.dic_config["host_mysql"],config.dic_config["user_mysql"],config.dic_config["pwd_mysql"], "ldae_way_" + config.dic_config["name_mysql_after"], int(config.dic_config["port_mysql"])) # 生成MYSQL数据库way方法实例
        rs_basedata_mysql = Conn_mysql(config.dic_config["host_mysql"],config.dic_config["user_mysql"],config.dic_config["pwd_mysql"], "ldae_basedata_" + config.dic_config["name_mysql_after"], int(config.dic_config["port_mysql"])) # 生成MYSQL数据库基础数据实例
        #rs_index_mysql = Conn_mysql(config.dic_config["host_mysql"],config.dic_config["user_mysql"],config.dic_config["pwd_mysql"], "ldae_index_" + config.dic_config["name_mysql_after"], int(config.dic_config["port_mysql"])) # 生成MYSQL数据库索引数据实例
        for i in range(0,row_feature_p):
            sql += "f" + str(i+1) +","
        sql += "what from " + name_table_train_p
        res, rows = rs_basedata_mysql.read_sql(sql)
        print (sql) # 调试用
        if (res < 1):
            return "训练集数据库为空或数据库读取错误"
        #print (rows) # 调试用
        while j<=dim_p:
        
            #print(j) # 调试用
            txt_csv = ""
            for row in rows:
                numb_row = len(row) - 1
                for i in range(numb_row):
                    #print (i,row[i]) #调试用
                    txt_csv += str(row[i]) + ","

                if ( int(row[numb_row]) == j-1 ):
                    txt_csv += "1.0"
                else:
                    txt_csv += "0.0"
                txt_csv += "\n"
                
            # 生成结果文件
            f = open(path_out_p + str(j) + ".csv", "w")
            f.write(txt_csv)
            f.close()
            
            print (str(j) + " " + path_out_p + str(j) + ".csv 文件已生成") #调试用
            
            j +=1
            
        # 生成测试集数据文件
        sql = "select question,what from " + name_table_test_p
        res, rows = rs_basedata_mysql.read_sql(sql)
        if (res < 1):
            return "测试集数据库为空或数据库读取错误"
        
        # 逐行写入测试文件
        f = open(path_out_p + "test.csv", "a+")
        for row in rows:
            try:
                f.write("\"" + row[0] + "\"," + str(row[1]) + "\n")
            except:
                pass
        f.close()
        print ("\n")
        print (path_out_p + "test.csv 文件已生成") #调试用
        
        rs_basedata_mysql.close_cur() #关闭数据游标
        rs_basedata_mysql.close() #关闭数据连接
        
        return txt
    
    # logistic回归
    def train_lr(self,path_input_p="../data/dae/train_lr.csv",path_out_p="../data/dae/result_lr.csv",steps_p=64,test_p=0):
        
        txt = ""

        # 1.导入数据
        Input = self.file2matrix(path_input_p,",")
        target = Input[:,-1] #获取分类标签列表
        [m,n] = shape(Input)
        if (test_p):
            print ("行:",m,"列:",n) # 调试用
        #print ("分类标签",target) # 调试用
        
        # 2.按分类绘制散点图
        # self.drawScatterbyLabel(plt,Input) # 理论分析用
        
        # 3.构建b+x 系数矩阵：b这里默认为1
        dataMat = self.buildMat(Input)
        if (test_p):
            print ("稀疏矩阵抽样：\n",dataMat) # 调试用
        
        # 4. 定义步长和迭代次数 
        alpha = self.alpha # 使用默认步长
        if (steps_p  == 0 ):
            steps = self.steps  #使用默认迭代次数
        else:
            steps = steps_p
            
        weights = ones((n,1))# 初始化权重向量
        weightlist = []
        
        # 5. 计算权重分类器
        for k in range(steps):
            gradient = dataMat*mat(weights) # 梯度
            output = self.logistic(gradient)  # logistic函数
            errors = target-output # 计算误差
            weights = weights + alpha*dataMat.T*errors
        
        for x in weights:
            txt += str(x[0]) + ","
        txt = txt[:-1]
        txt = txt.replace("[[","")
        txt = txt.replace("]]","")
        txt = txt.replace(" ","")
        
        # 6. 永固化权重
        f = open(path_out_p, "w")
        f.write(txt)
        f.close()

        return txt
        

# 用户画像类
class User():
    
    def q2u(self,numb_p=6):
    
        txt = ""
        dic_t = {}
        dic_r = {} # 排序字典
        numb_work_all = 0
        numb_rs_all = 0
        numb_word_all = 0
        numb_td_idf = 0 # TF-IDF值
        rank_t = 0 # 最后的排名值
        list_t = [] # 排名队列
        sql_last = "" # 最后的更新语句
        sql_head = ""
        sql_where = ""
        
        #rs_sqlite_file = Conn_sqlite3(config.path_main + config.dic_config["path_sqlite"],0) # 生成文件数据库实例
        rs_way_mysql = Conn_mysql(config.dic_config["host_mysql"],config.dic_config["user_mysql"],config.dic_config["pwd_mysql"], "ldae_way_" + config.dic_config["name_mysql_after"], int(config.dic_config["port_mysql"])) # 生成MYSQL数据库way方法实例
        #rs_basedata_mysql = Conn_mysql(config.dic_config["host_mysql"],config.dic_config["user_mysql"],config.dic_config["pwd_mysql"], "ldae_basedata_" + config.dic_config["name_mysql_after"], int(config.dic_config["port_mysql"])) # 生成MYSQL数据库基础数据实例
        #rs_index_mysql = Conn_mysql(config.dic_config["host_mysql"],config.dic_config["user_mysql"],config.dic_config["pwd_mysql"], "ldae_index_" + config.dic_config["name_mysql_after"], int(config.dic_config["port_mysql"])) # 生成MYSQL数据库索引数据实例
        
        import math #数学计算库
        
        # 数据源装载
        sql = "select count(*) from qa"
        res, rows = rs_basedata_mysql.read_sql(sql)
        if (res < 1):
            return "记录总数为空或数据库读取错误"
        else:
            numb_rs_all = rows[0][0] # 获得文档总数
            if (numb_rs_all < 1):
                return "记录总数为空或数据库读取错误"
                
        sql = "select hash,forward_question from qa where v3=0"
        res, rows = rs_basedata_mysql.read_sql(sql)
        if (res < 1):
            return "已全部处理完毕或数据库读取错误"
        else:
            numb_work_all = res
            
        # 主循环开始
        count_do = 1
        for row in rows:
        
            dic_r = {}
            sql = "update qa set v3=1 where hash='" + row[0] + "'"
            update_if = rs_basedata_mysql.write_sql(sql) # 打上访问标记
            
            # 获得正序字典
            try:
                dic_t = eval(row[1])
            except:
                continue
                
            if (dic_t):
                
                numb_word_all = len(dic_t)
                
                for x in dic_t:
                    
                    # 构造排序字典
                    sql = "select idf from index_question where keyword='" + x + "'"
                    res_t, rows_t = rs_basedata_mysql.read_sql(sql)
                    if (res_t > 0 and x != 'numb_key_ldae'):
                        numb_td_idf = round(len(dic_t[x])/numb_word_all * math.log(numb_rs_all/(rows_t[0][0]+1)),8)
                        rank_t = numb_td_idf # 暂时不做任何修订
                        #print (x,dic_t[x],numb_td_idf,rank_t) # 调试用
                        if (x in dic_r):
                            pass
                        else:
                            dic_r[x] = rank_t
                    
                #print (dic_r) # 调试用
                list_t = sorted(dic_r.items(), key=lambda d:d[1], reverse = True)#排名
                #print (list_t) # 调试用
                
                # 检索用户模型是否存在
                sql_last = ""
                sql = "select id from user_main where hash='" + row[0] + "' limit 1"
                res_u, rows_u = rs_basedata_mysql.read_sql(sql)
                if (res_u > 0):
                    sql_head = "update user_main set "
                    sql_where = " where id=" + str(rows_u[0][0]) + " "
                else:
                    sql_head = "insert user_main set "
                    sql_last = "hash='" + row[0] + "',"
                    sql_where = " "
                
                i = 1 
                for y in list_t:
                    print (y[0],y[1])
                    sql_last += "m" + str(i)+ "='" + y[0] + "',a" + str(i) + "=" + str(y[1]) + "," 
                    if (i  >= numb_p):
                        break
                    else:
                        i += 1
                
                # 数据存入用户画像模型表
                sql_last = sql_head + sql_last + sql_where
                
                if (sql_last):
                    sql_last = sql_last[:-1]
                
                print (sql_last) # 调试用
                sql_do = rs_basedata_mysql.write_sql(sql_last)
                
            #e("stop_1") #调试用

            print ("第" + str(count_do) + "次操作,完成率：" + "%.4f" % float(count_do*100.0/numb_work_all) + "%")
            count_do += 1
            
        rs_basedata_mysql.close_cur() #关闭数据游标
        rs_basedata_mysql.close() #关闭数据连接
            
        return txt
      

# 测试主类
class Test_dae(Dae_base):

    # logistic的准确率
    def rate_lr(self):
        pass

    def classifier_lr(self,path_input_p="../data/dae/result_lr_0.csv",numb_fea_p=2,dim_p=2):
        txt = ""
        cf = ""
        
        # 1.导入数据
        #weights = self.file2matrix(path_input_p,",")
        
        #weights = mat([[4.2],[-0.147324],[2.874846]]) # 测试数据示例
        # 2. 调用分类器
        if (numb_fea_p == 2):
            testdata = mat([[-0.147324,2.874846]])
            
        if (numb_fea_p == 16):
            testdata = mat([[0.14388489,0.00000000,0.38461538,0.00000000,0.00000000,0.11764706,0.40000000,0.02527076,0.12500000,0.25000000,0.00000000,0.00000000,0.00000000,0.40000000,0.02527076,0.00000000]])
        
        m,n =  shape(testdata)
        testmat = zeros([m,n+1])
        testmat[:,1] = 1
        testmat[:,1:] = testdata
        
        #默认7维分类
        dic_cf = {}
        print ("分类号  分类概率")
        j = 1
        while j<=dim_p:
            porb = 0.0
            weights = mat(self.weights2matrix("../data/dae/result_lr_" + str(j) + ".csv",delimiter=","))
            porb = self.classifier_two(testmat,weights,output_p=1)
            print (j-1,porb) #调试用
            dic_cf[j-1] = porb # 赋值排序数组
            j += 1
        
        # 分类值比较 默认取最大可能概括
        cf = max(dic_cf, key=dic_cf.get)
        txt = "最后的分类是：" + str(cf)
        
        return txt

# 特征主类
class Feature_dae(Train_dae):

    def __init__(self):
        pass

    # logistic回归分类器
    def what_class_lr(self,list_last=[],path_dae_p="./data/dae/",dim_p=7,test_p=0,name_model_p="x"):
    
        what_is = 6 #分型判别值
        if (list_last):
        #获得概率
            testdata = mat(list_last)
            m,n =  shape(testdata)
            testmat = zeros([m,n+1])
            testmat[:,1] = 1
            testmat[:,1:] = testdata
        
            #默认7维分类
            dic_cf = {}
            if (test_p):
                print ("分类号  分类概率")
            j = 1
            while j<=dim_p:
                porb = 0.0
                weights = mat(self.weights2matrix(path_dae_p + "result_lr_" + str(j) +  "_" + name_model_p + ".csv",delimiter=","))
                porb = self.classifier_two(testmat,weights,output_p=1)
                if (test_p):
                    print (j-1,porb) #调试用
                dic_cf[j-1] = porb # 赋值排序数组
                j += 1
        
            # 分类值比较 默认取最大可能概括
            what_is = max(dic_cf, key=dic_cf.get)
            
            return what_is
    
    # 问题分类处理
    def question_cf(self,q_p="",numb_fea_p=16,dim_p=7,dic_min={},dic_max={},path_dae_p="./data/dae/",path_dic_p=config.dic_config["path_dic"]  +  "",name_model_p="x"):
    
        if (q_p != ""):
        
            list_last = self.question_fea(q_p=q_p,numb_fea_p=numb_fea_p,dim_p=dim_p,dic_min=dic_min,dic_max=dic_max,path_dae_p=path_dae_p,path_dic_p=path_dic_p)
            what_is = self.what_class_lr(list_last=list_last,path_dae_p=path_dae_p,dim_p=dim_p,test_p=0,name_model_p=name_model_p)

        #print("\n----  最后的分类是：" + str(what_is) + " -----\n") #调试用
        
        return what_is
        
    # 归一化上下限字典
    def dic_max_min(self,path_f_p="./data/f/"):
        dic_min = {}
        csv_reader = csv.reader(open(path_f_p + 'f_min.csv', encoding='utf-8'))
        for x in csv_reader:
            i = 1
            for y in x:
                dic_min[i] = float(y)
                i +=1
        #print (dic_min) # 调试用
        dic_max = {}
        csv_reader = csv.reader(open(path_f_p + 'f_max.csv', encoding='utf-8'))
        for x in csv_reader:
            i = 1
            for y in x:
                dic_max[i] = float(y)
                i +=1
        return dic_min,dic_max
    
    # 问答知识库问题标注
    def divine_q_db(self,numb_fea_p=16,dim_p=2,limit_p=0):
        txt = ""
        
        #rs_sqlite_file = Conn_sqlite3(config.path_main + config.dic_config["path_sqlite"],0) # 生成文件数据库实例
        rs_way_mysql = Conn_mysql(config.dic_config["host_mysql"],config.dic_config["user_mysql"],config.dic_config["pwd_mysql"], "ldae_way_" + config.dic_config["name_mysql_after"], int(config.dic_config["port_mysql"])) # 生成MYSQL数据库way方法实例
        #rs_basedata_mysql = Conn_mysql(config.dic_config["host_mysql"],config.dic_config["user_mysql"],config.dic_config["pwd_mysql"], "ldae_basedata_" + config.dic_config["name_mysql_after"], int(config.dic_config["port_mysql"])) # 生成MYSQL数据库基础数据实例
        #rs_index_mysql = Conn_mysql(config.dic_config["host_mysql"],config.dic_config["user_mysql"],config.dic_config["pwd_mysql"], "ldae_index_" + config.dic_config["name_mysql_after"], int(config.dic_config["port_mysql"])) # 生成MYSQL数据库索引数据实例
        
        # 原力参数获取
        dic_min,dic_max = self.dic_endline()
        #print (dic_max) # 调试用
        # 获得待标准数据源
        sql = "select id,question from qa where v3=0 "
        if (limit_p > 0):
            sql += "limit " + str(limit_p)
        #sql += " order by rand()" # 调试用
        res, rows = rs_basedata_mysql.read_sql(sql)
        if (res < 1):
            return "问答知识库读取错误或数据库读取错误"
        for row in rows:
            
            what_is = 0
            
            try:
                print(row[0],row[1]) 
            except:
                pass
                
            what_is = self.question_cf(q_p=row[1],numb_fea_p=numb_fea_p,dim_p=dim_p,dic_min=dic_min,dic_max=dic_max,name_model_p="x")
            sql = "update qa set what=" + str(what_is) + ",v3=1 where id=" + str(row[0])
            update_if = rs_basedata_mysql.write_sql(sql)
        
        rs_basedata_mysql.close_cur() #关闭数据游标
        rs_basedata_mysql.close() #关闭数据连接
        
        return txt
        
def run_it():

    print("") # 调试用

#--------- 内部模块处理<<结束>> ---------#

#---------- 主过程<<开始>> -----------#

def main():

    #1 过程一
    run_it()
    #2 过程二
    #3 过程三
    
if __name__ == '__main__':
    main()
    
#---------- 主过程<<结束>> -----------#