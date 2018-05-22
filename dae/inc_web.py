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

# 前台服务分类
class Web_foreground(object):
    
    # 前台服务分类JS码生成
    def get_class_js(self,path_p=""):
    
        txt = ""
        txt_1 = ""
        txt_1 += "var onecount_x0;"  + "\n"
        txt_1 += "onecount_x0=0;" + "\n"
        txt_1 += "subcat_x0 = new Array();" + "\n"

        txt_2 = ""
        txt_2 += "var mytext = '';" + "\n"
        txt_2 += "mytext += '<select name=\"bigclass_name\" onChange=\"changelocation_x0(document.myform_x0.bigclass_name.options[document.myform_x0.bigclass_name.selectedIndex].value)\" size=\"1\"><option selected value=\"\">';"+ "\n"
        txt_2 += "mytext += '<option value=\"\" selected = \"selected\">请选择大类</option>';" + "\n"
        
        rs_way_mysql = Conn_mysql(config.dic_config["host_mysql"],config.dic_config["user_mysql"],config.dic_config["pwd_mysql"], "ldae_way_" + config.dic_config["name_mysql_after"], int(config.dic_config["port_mysql"])) # 生成MYSQL数据库way方法实例
        
        sql = "select bigclass_name from bna_bigclass "
        sql += "where bigclass_name in "
        sql += "(select bigclass_name from bna_smallclass where power > 0 ) "
        sql += "and power > 0 "
        sql += "order by power"
        res_b, rows_b = rs_way_mysql.read_sql(sql)
        if(res_b < 1):
            txt = "BNA大类数据库为空或数据库读取错误"
            return txt
        
        i = 0
        for rows in rows_b:
        
            txt_2 += "mytext += '<option value=\"" + rows[0] + "\">" + rows[0] + "</option>';" + "\n"
            #print (rows[0]) # 调试用
            
            sql = "select smallclass_name,action from bna_smallclass "
            sql += "where bigclass_name='" + rows[0] + "' and power > 0 "
            sql += "order by power"
            res_t, rows_t = rs_way_mysql.read_sql(sql)

            if (res_t > 0):
                for x in rows_t:
                    print (x[0],rows[0],x[1]) # 调试用
                    txt_1 += "subcat_x0[" + str(i)+ "] = new Array(\"" + x[0] + "\",\"" + rows[0] + "\",\"" + x[1] + "\");" + "\n"
                    i += 1
                    
        txt_1 += "onecount_x0=" + str(i) + ";"
        txt_1 += """
function changelocation_x0(locationid)
{document.myform_x0.action.length = 0;

    var locationid=locationid;
    var i;
    for (i=0;i < onecount_x0; i++)
        {
        if (subcat_x0[i][1] == locationid)    
            { 
        document.myform_x0.action.options[document.myform_x0.action.length] = new Option(subcat_x0[i][0], subcat_x0[i][2]);
       
        }        
        }
        
    }
        """
        print (txt_1) # 调试用
        with open(path_p + 'bna_class.js', 'w',encoding='utf-8') as f:
            f.write(txt_1)
        
        txt_2 += "mytext += '</select>';" + "\n"
        txt_2 += "document.write(mytext);" + "\n"
        print (txt_2) # 调试用
        with open(path_p + 'bna_bigclass.js', 'w',encoding='utf-8') as f:
            f.write(txt_2)
            
        rs_way_mysql.close_cur() #关闭数据游标
        rs_way_mysql.close() #关闭数据连接
        
        txt = "js文件写入完成"
        return txt


# 主执行调用入口函数
def run_it(action_p="",path_p="./statics/js/"):
    
    txt = ""
        
    if (action_p == "class_js"):
    
        txt = "hello"
        web_foreground = Web_foreground() # 实例化前台处理模块
        txt = web_foreground.get_class_js(path_p=path_p)
        return txt
    
    return txt
    
if __name__ == '__main__':
    print ("") # 防止代码泄漏只输出空字符 
    