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

#-----系统自带必备模块引用-----
import os # 操作系统模块
import sys # 操作系统模块1
import datetime # 系统时间模块
import time # 系统时间模块

#-----系统外部需安装库模块引用-----
import tornado.web #tornado web接口类

#-----DIY自定义库模块引用-----
sys.path.append("..")
import config #系统配置参数
from diy.inc_sys import * #自定义系统级功能模块
from diy.inc_conn import * #自定义数据库功能模块 
import inc_dae # 主数据分析引擎模块
import diy.inc_file as inc_file # 基本自定义文件模块

#-----DIY自定义库模块引用-----

#--------- 外部模块处理<<结束>> ---------#


#--------- 内部模块处理<<开始>> ---------#

# ---外部参变量处理

# ---全局变量处理

# ---本模块内部类或函数定义区

# web服务基础模块
class BaseHandler(tornado.web.RequestHandler):

    def write(self,chunk): 
        self.set_header('Access-Control-Allow-Origin', '*')
        super(BaseHandler, self).write(chunk)

    def get_current_user(self):
        return self.get_secure_cookie("username")
    
    # 重要参数获取
    def arg_get(self,q_p="",answer_p="",action_p="",page_p=1,id_p=0):
        
        try:
            q_p = self.get_argument('q')
        except:
            q_p = ""
            
        try:
            action_p = self.get_argument('action')
        except:
            action_p = ""
            
        try:
            page_p = int(self.get_argument('page'))
        except:
            page_p = 1
            
        try:
            id_p = int(self.get_argument('id'))
        except:
            id_p = 0
            
        try:
            answer_p = self.get_argument('answer')
        except:
            answer_p = ""
        
        #print(q_p,action_p,page_p,id_p) # 调试用
        
        return q_p,action_p,answer_p,page_p,id_p
    
    # 获得系统处理后的json码
    def get_json(self,q,action,answer,page,id):

        result = ""
        #print("问题:",q,"行为:",action,"答案：",answer,"分页:",page,"ID:",id) # 调试用
        
        #self.write (q) #调试用
        if (action == ""):
        
            pass
        
        else:
            result = inc_dae.run_it(q_p=q,action_p=action,answer_p=answer,page_p=page,id_p=id) # 调试用 用于显示详细错误信息
            #try:
                #result = inc_dae.run_it(q_p=q,action_p=action,answer_p=answer,page_p=page,id_p=id) # 调试用
            #except BaseException as e:
                #result = "数据分析内嵌式调用错误"
                #print ("get_json异常信息：",e)
                
        return result

# 主页模块
class IndexHandler(tornado.web.RequestHandler):
    
    def get(self,*args):
        # 访问日志处理
        dic_login_p = {}
        dic_t = {}
        txt_log = "" # 日志的文本内容
        path_p = "data\\log\\z_log_web_index.csv"
        file_file = inc_file.File_file()
        dic_t["time_v"] = str_split(datetime.datetime.now()) # 访问时间
        dic_t["ip"] = self.request.remote_ip # 获得IP
        dic_t["id"] = 0
        # 获得用户cookie资料
        try:
            
            str_t = self.get_secure_cookie("session_ldae_user")
            str_t = str_t.decode('utf-8')
            # 解密session字典
            str_t = secret_ldae(str_t,key_p=config.dic_config["secret_key"],salt_p = config.dic_config["secret_salt"],secret_if="no")
            dic_login_p = eval(str_t)
            if ("id" in dic_login_p):
                dic_t["id"] = dic_login_p["id"]
            
        except:
        
            pass
        
        #print ("日志参数",path_p,dic_t) # 调试用
        
        # 将访问日志字典转化为csv格式
        if (dic_t):
            txt_log = str(dic_t["id"]) + "," + dic_t["ip"] + "," + dic_t["time_v"] + "\n"
            
        # 写入访问日志
        try:
            file_file.write_add(path_p=path_p,renew_if=0,content_p=txt_log)
        except:
            pass
            
        # 渲染首页
        self.render('index.html',
        name_soft=config.dic_config["name_soft"],
        type_soft=config.dic_config["type_soft"],
        vol_soft=config.dic_config["vol_soft"],
        authority_soft=config.dic_config["authority_soft"],
        author_soft=config.dic_config["author_soft"],
        qq_group=config.dic_config["qq_group"],
        tel_ldae=config.dic_config["tel_ldae"],
        url_ldae=config.dic_config["url_ldae"],
        sys_time=str(datetime.datetime.now())
        ) #渲染首页 

# 管理模块
class AdminHandler(BaseHandler):

    #用户权限标定
    def newword_power_is(self,roles_p):

        for i in range(8):
            row = config.dic_config["power_" + str(i)]
            if (roles_p == hash_make(hash_make(row[0]))):
                return row[1]
                
        return "n/a"
    
    @tornado.web.authenticated
    def get(self,*args):
        
        # 登陆时间取得
        str_time = str(self.get_secure_cookie("time_login"))
        str_time = str_time.replace("b'","")
        str_time  = str_time.replace("'","")
        
        str_roles = str(self.get_secure_cookie("roles"))
        str_roles = str_roles.replace("b'","")
        str_roles  = str_roles.replace("'","")
        
        self.render('admin.html',
        name_soft=config.dic_config["name_soft"],
        type_soft=config.dic_config["type_soft"],
        vol_soft=config.dic_config["vol_soft"],
        authority_soft=config.dic_config["authority_soft"],
        author_soft=config.dic_config["author_soft"],
        qq_group=config.dic_config["qq_group"],
        tel_ldae=config.dic_config["tel_ldae"],
        url_ldae=config.dic_config["url_ldae"],
        admin_roles=self.newword_power_is(str_roles),
        logintime_last=str_time
        
        )

# 登录模块
class LoginHandler(BaseHandler):

    def get(self):
        self.render('login.html',
        name_soft=config.dic_config["name_soft"],
        type_soft=config.dic_config["type_soft"],
        vol_soft=config.dic_config["vol_soft"],
        )

    def post(self,*args):
        
        res_m = 0 #数据库记录数
        username = "" #数据库内用户名
        roles = "" #数据库内用户权限

        res_m , username , roles = self.user_check(rs_sqlite_file,self.get_argument('username'),self.get_argument('password'))
        #self.write ("<h1>" + str(res_m) + " " + username + " " + roles + "</h1>") #调试用
        
        if ( res_m > 0 ):
            
            self.set_secure_cookie("username", username)
            self.set_secure_cookie("roles", roles)
            self.set_secure_cookie("time_login", str_split(datetime.datetime.now()))
            
            self.redirect("/ldae")
            
        else:
            pass
            self.redirect("/login")

# 登录退出模块
class LogoutHandler(tornado.web.RequestHandler):

    def get(self):
        #self.write ("<h1>" + str(self.get_secure_cookie("username")) + " " + str(self.get_secure_cookie("roles")) + " " + str(self.get_secure_cookie("time_login")) + "</h1>") #调试用
        self.clear_cookie("username")
        self.clear_cookie("roles")
        self.clear_cookie("time_login")
        
        self.redirect("/login")
        
#APi模块 强调速度 系统核心模块
class Api(BaseHandler):

    def input_do(self):
        txt = ""
        q,action,answer,page,id = self.arg_get()
            
        #print("问题:",q,"行为:",action,"答案：",answer,"分页:",page,"ID:",id,"加解密操作",secret_if) # 调试用
        
        txt = self.get_json(q,action,answer,page,id)
        
        return txt
        
    def get(self):
        self.write(self.input_do())
        
    def post(self):
        self.write(self.input_do())
        
#展示模块 
class Show(BaseHandler):

    # 获得调用模块名
    def get_model_is(self,action_p):
        
        #rs_sqlite_file = Conn_sqlite3(config.path_main + config.dic_config["path_sqlite"],0) # 生成文件数据库实例
        rs_way_mysql = Conn_mysql(config.dic_config["host_mysql"],config.dic_config["user_mysql"],config.dic_config["pwd_mysql"], "ldae_way_" + config.dic_config["name_mysql_after"], int(config.dic_config["port_mysql"])) # 生成MYSQL数据库way方法实例
        #rs_basedata_mysql = Conn_mysql(config.dic_config["host_mysql"],config.dic_config["user_mysql"],config.dic_config["pwd_mysql"], "ldae_basedata_" + config.dic_config["name_mysql_after"], int(config.dic_config["port_mysql"])) # 生成MYSQL数据库基础数据实例
        #rs_index_mysql = Conn_mysql(config.dic_config["host_mysql"],config.dic_config["user_mysql"],config.dic_config["pwd_mysql"], "ldae_index_" + config.dic_config["name_mysql_after"], int(config.dic_config["port_mysql"])) # 生成MYSQL数据库索引数据实例
        
        model_is = "未识别"
        sql = "select smallclass_name from bna_smallclass where action='" + action_p + "'"
        res, rows = rs_way_mysql.read_sql(sql)
        if (res < 1):
            return model_is
        else:
            model_is = rows[0][0]
            
        rs_way_mysql.close_cur() #关闭数据游标
        rs_way_mysql.close() #关闭数据连接
        
        return model_is
    
    # 是非型意图识别解释
    def get_meaning_yesno(self,meaning=6):
        
        txt = "未知分型"
        
        if (meaning == 0):
            txt = "解答型"
        if (meaning == 1):
            txt = "是非型"
            
        return txt
            
    # 是为型意图识别
    def get_meaning_whathow(self,meaning=6):
        
        txt = "未知分型"
        
        if (meaning == 0):
            txt = "是什么（实体解答）型"
        if (meaning == 1):
            txt = "怎样办，为什么（实质解答）型"

        return txt
        
    # 词性解释
    def pseg_what_is(self,dic_p={},pseg_p=""):
    
        what_is = ""
        explain = ""
        if (pseg_p in dic_p):
            what_is = dic_p[pseg_p][0]
            explain = dic_p[pseg_p][1]
        return what_is,explain
        
    # 结果分析
    def get_result_what(self,dic_t={},model_is=""):
        
        txt = ""
        list_t = []
        model_is = model_is.strip()
        
        if (model_is == "LR_是非型_意图识别"):
            if ("classify" in dic_t):
                txt = self.get_meaning_yesno(meaning=dic_t["classify"])
                
        if (model_is == "svm_是为型_意图识别"):
            if ("classify" in dic_t):
                txt = self.get_meaning_whathow(meaning=dic_t["classify"])
                
        if (model_is == "Cnn+Bilstm意图识别"):
            if ("classify" in dic_t):
                txt = self.get_meaning_yesno(meaning=dic_t["classify"])
                
        if (model_is == "知识图谱识别"):
            arr_t = []
            if (dic_t["kg"] != ""):
                txt += "<br><br>"
                arr_t = dic_t["kg"].split(",")
                for x in arr_t:
                    txt += x.replace("|"," / ") + "<br><br>"
        
        if (model_is == "输入提示"):
            arr_t = []
            if (dic_t):
                txt += "<br><br>"
                for x in dic_t:
                    txt += dic_t[x] + "<br><br>"
        
        if (model_is == "分词"):
            list_order = []
            if (dic_t):
                dic_t_2 = {}
                # 转化为整数 用于正确排序输出
                for x in dic_t:
                    dic_t_2[int(x)] = dic_t[x]
                list_order = sorted(dic_t_2.items(), key=lambda d:d[0], reverse = False)
                txt += "<br><br>"
                for x in list_order:
                    txt += x[1] + "<br><br>"
        
        if (model_is == "词性标注"):
        
            dic_pseg = {}
            list_order = []
            str_t = ""
            dic_pseg = {
"Ag":['形语素','形容词性语素。形容词代码为 a，语素代码ｇ前面置以A。'],
"a":['形容词','取英语形容词 adjective的第1个字母。'],
"ad":['副形词','直接作状语的形容词。形容词代码 a和副词代码d并在一起。'],
"an":['名形词','具有名词功能的形容词。形容词代码 a和名词代码n并在一起。'],
"b":['区别词','取汉字“别”的声母。'],
"c":['连词','取英语连词 conjunction的第1个字母。'],
"dg":['副语素','副词性语素。副词代码为 d，语素代码ｇ前面置以D。'],
"d":['副词','取 adverb的第2个字母，因其第1个字母已用于形容词。'],
"e":['叹词','取英语叹词 exclamation的第1个字母。'],
"f":['方位词','取汉字“方”'],
"g":['语素','绝大多数语素都能作为合成词的“词根”，取汉字“根”的声母。'],
"h":['前接成分','取英语 head的第1个字母。'],
"i":['成语','取英语成语 idiom的第1个字母。'],
"j":['简称略语','取汉字“简”的声母。'],
"k":['后接成分','n/a'],
"l":['习用语','习用语尚未成为成语，有点“临时性”，取“临”的声母。'],
"m":['数词','取英语 numeral的第3个字母，n，u已有他用。'],
"Ng":['名语素','名词性语素。名词代码为 n，语素代码ｇ前面置以N。'],
"n":['名词','取英语名词 noun的第1个字母。'],
"nr":['人名','名词代码 n和“人(ren)”的声母并在一起。'],
"ns":['地名','名词代码 n和处所词代码s并在一起。'],
"nt":['机构团体','“团”的声母为 t，名词代码n和t并在一起。'],
"nz":['其它专名','“专”的声母的第 1个字母为z，名词代码n和z并在一起。'],
"o":['拟声词','取英语拟声词 onomatopoeia的第1个字母。'],
"p":['介词','取英语介词 prepositional的第1个字母。'],
"q":['量词','取英语 quantity的第1个字母。'],
"r":['代词','取英语代词 pronoun的第2个字母,因p已用于介词。'],
"s":['处所词','取英语 space的第1个字母。'],
"tg":['时语素','时间词性语素。时间词代码为 t,在语素的代码g前面置以T。'],
"t":['时间词','取英语 time的第1个字母。'],
"u":['助词','取英语助词 auxiliary'],
"vg":['动语素','动词性语素。动词代码为 v。在语素的代码g前面置以V。'],
"v":['动词','取英语动词 verb的第一个字母。'],
"vd":['副动词','直接作状语的动词。动词和副词的代码并在一起。'],
"vn":['名动词','指具有名词功能的动词。动词和名词的代码并在一起。'],
"w":['标点符号','n/a'],
"x":['非语素字','非语素字只是一个符号，字母 x通常用于代表未知数、符号。'],
"y":['语气词','取汉字“语”的声母。'],
"z":['状态词','取汉字“状”的声母的前一个字母。'],
"un":['未知词','不可识别词及用户自定义词组。取英文Unkonwn首两个字母。(非北大标准，CSW分词中定义)'],
}
                    
            if (dic_t):
                dic_t_2 = {}
                # 转化为整数 用于正确排序输出
                for x in dic_t:
                    dic_t_2[int(x)] = dic_t[x]
                list_order = sorted(dic_t_2.items(), key=lambda d:d[0], reverse = False)
                txt += "<br><br>"
                for x in list_order:
                    list_t = []
                    try:
                        list_t = eval(x[1]) 
                    except:
                        pass
                    if (list_t):
                        what_is,explain = self.pseg_what_is(dic_p=dic_pseg,pseg_p=list_t[1])
                        txt += "<div title=\"" + explain + "\"> " + list_t[0] + "&nbsp&nbsp&nbsp&nbsp /" + list_t[1] + " &nbsp&nbsp&nbsp&nbsp" + what_is + "</div><br><br>"
                txt += "（提示：鼠标如果放在字符上面，可以获得相关解释！）"
                
        if (model_is == "TF_IDF"):
            list_order = []
            if (dic_t):
                list_order = sorted(dic_t.items(), key=lambda d:d[1], reverse = True)
                txt += "<br><br>"
                for x in list_order:
                    txt += x[0] + "<br><br>"
                    
        if (model_is == "主题(关键)词"):
            list_order = []
            if (dic_t):
                list_order = sorted(dic_t.items(), key=lambda d:d[1], reverse = True)
                txt += "<br><br>"
                for x in list_order:
                    txt += x[0] + "<br><br>"
                    
        if (model_is == "命名实体"):
            list_order = []
            if (dic_t):
                list_order = sorted(dic_t.items(), key=lambda d:d[1], reverse = True)
                txt += "<br><br>"
                for x in list_order:
                    txt += x[0] + "<br><br>"
                    
        if (model_is == "近义词"):
            list_order = []
            if (dic_t):
                list_order = sorted(dic_t.items(), key=lambda d:d[1], reverse = True)
                txt += "<br><br>"
                for x in list_order:
                    txt += x[0] + "<br><br>"
                    
        if (model_is == "答案抽取_相似度"):
            
            list_t = []
            tup_order = []
            list_last = []
            numb_div = 0
            numb_dic = 0
            list_div = [] # 已处理完的段落编号列表
            list_dot = ["，","。","？","！","”’"] # 标点符号列表 校验用
            
            if (dic_t):
                tup_order = sorted(dic_t.items(), key=lambda d:d[1][1]*d[1][3], reverse = True)
                dic_t = {}
                j = 1
                for x in tup_order:
                    #print (j,"",x) # 调试用
                    if (x[1][3] in dic_t):
                        # 保留段落号靠前的重复句
                        if (dic_t[x[1][3]][2][2] > x[1][2][2]):
                            dic_t[x[1][3]] = [x[1][1]*x[1][3],x[1][0],x[1][2]]
                    else:
                        dic_t[x[1][3]] = [x[1][1]*x[1][3],x[1][0],x[1][2]]
                    j += 1
                    
                tup_order = sorted(dic_t.items(), key=lambda d:d[1][0], reverse = True)
                
                dic_t = {}
                i = 1
                for x in tup_order:
                    dic_t[i] = [x[1][1],x[1][2]]
                    i += 1
                
                numb_dic = len(dic_t)
                j = 1
                while (j <= len(dic_t)):
                    
                    numb_div = dic_t[j][1][1]
                    
                    if (numb_div in list_div):
                        # 已处理过该段落的所有句子
                        j += 1
                        continue 
                    
                    if (dic_t[j][0] in list_last):
                        pass
                    else:
                        list_last.append(dic_t[j])
                    
                    k = j + 1
                    while(k <= len(dic_t)):
                        #print(j,k)
                        if (k in list_last[0]):
                            pass
                        else:
                            if (dic_t[k][1][1] == numb_div):
                                list_last.append(dic_t[k])
                        
                        k +=1
                        
                    list_div.append(numb_div) # 已处理完的段落加入如验证集
                    j += 1
                if (list_last):
                    numb_div = list_last[0][1][1]
                    txt += """
                 <div id="result" align="left" style="width:550px; border:none; overflow:hidden;">
                &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
                """
                    j = 1
                    while (j <= len(list_last)):
                
                        # 同一段落加相应排版标签
                        if (numb_div != list_last[j-1][1][1]):
                            txt += "<br><br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"
                            numb_div = list_last[j-1][1][1]
                        
                        if (list_last[j-1][0][-1] in list_dot):
                            txt +=  list_last[j-1][0]
                        else:
                            txt +=  list_last[j-1][0] + "。"
                        
                        j +=1
                    txt += "</div>"
            # 结果字典为空
            else:
                txt += "n/a"
                
        if (model_is == "短文本相似度"):
            if (dic_t):
                txt += "<br><br>短文本相似度："
                txt += str(dic_t["value_similar"])

        return txt
    
    # 输入处理
    def input_do(self):
    
        time_start = datetime.datetime.now()
        txt = "<center><br><br>"
        q,action,answer,page,id = self.arg_get()
        
        #print("问题:",q,"行为:",action,"答案：",answer,"分页:",page,"ID:",id) # 调试用
        bigclass_name = ""
        model_is = ""
        result = ""
        result_what = "" #结果解析
        
        # 校验性处理
        if (q.strip() == ""):
            return "<center><br><br><br><br><br>输入不能为空!</center>"
        
        # 双提交的特殊处理
        if (action == "answer_extract_similar" or action == "answer_extract_deeplearn" ):
            #特殊提交页的特殊处理
            if (answer == ""):
            
                try:
                    bigclass_name = self.get_argument('bigclass_name')
                except:
                    bigclass_name = "暂未列出"
                    
                with open("./views/form_answer_extract.html", 'r',encoding='utf-8') as f:
                    txt= f.read()
                txt = txt.replace("{{question_form}}",q)
                txt = txt.replace("{{action_form}}",action)
                txt = txt.replace("{{bigclass_name_form}}",bigclass_name)
                txt = txt.replace("{{local_url}}",config.dic_config["path_statics"])
                txt = txt.replace("{{name_soft}}",config.dic_config["name_soft"])
                txt = txt.replace("{{type_soft}}",config.dic_config["type_soft"])
                txt = txt.replace("{{vol_soft}}",config.dic_config["vol_soft"])
                txt = txt.replace("{{authority_soft}}",config.dic_config["authority_soft"])
                txt = txt.replace("{{author_soft}}",config.dic_config["author_soft"])
                txt = txt.replace("{{qq_group}}",config.dic_config["qq_group"])
                txt = txt.replace("{{tel_ldae}}",config.dic_config["tel_ldae"])
                txt = txt.replace("{{url_ldae}}",config.dic_config["url_ldae"])
                txt = txt.replace("{{sys_time}}",str(datetime.datetime.now()))
                
                return txt
            
        if (action == "similar_shorttxt"):
            #特殊提交页的特殊处理
            if (answer == ""):
                try:
                    bigclass_name = self.get_argument('bigclass_name')
                except:
                    bigclass_name = "暂未列出"
                    
                with open("./views/form_similar_shorttxt.html", 'r',encoding='utf-8') as f:
                    txt= f.read()
                txt = txt.replace("{{question_form}}",q)
                txt = txt.replace("{{action_form}}",action)
                txt = txt.replace("{{bigclass_name_form}}",bigclass_name)
                txt = txt.replace("{{local_url}}",config.dic_config["path_statics"])
                txt = txt.replace("{{name_soft}}",config.dic_config["name_soft"])
                txt = txt.replace("{{type_soft}}",config.dic_config["type_soft"])
                txt = txt.replace("{{vol_soft}}",config.dic_config["vol_soft"])
                txt = txt.replace("{{authority_soft}}",config.dic_config["authority_soft"])
                txt = txt.replace("{{author_soft}}",config.dic_config["author_soft"])
                txt = txt.replace("{{qq_group}}",config.dic_config["qq_group"])
                txt = txt.replace("{{tel_ldae}}",config.dic_config["tel_ldae"])
                txt = txt.replace("{{url_ldae}}",config.dic_config["url_ldae"])
                txt = txt.replace("{{sys_time}}",str(datetime.datetime.now()))
                
                return txt
                
        # 重要，获得分析结果
        
        result = self.get_json(q,action,answer,page,id)
        #print("分析结果",result) # 调试用
        
        dic_t = {}
        
        # 输入与输出解析
        txt += "<div><b>输入:</b> <font style=\"color:red;font-weight: bold;font-size:22px\"> <xmp> " + q + " </xmp></font><br></div>"
        
        try:
            bigclass_name = self.get_argument('bigclass_name')
        except:
            bigclass_name = "未知"
            
        txt += "<div><b>功能大类:</b> " + bigclass_name + "</div>"
        
        model_is = self.get_model_is(action_p =action)
        
        print("请求行为：",action,"模式：",model_is) #调试用
        
        txt += "<div><b>调用模块:</b> " + model_is + "</div>"
        
        # 分析结果说明
        if (model_is):
            try:
                dic_t = eval(result)
            except:
                pass
                
        # 获得分析结果
        #print ("分析结果元素",dic_t,model_is) # 调试用
        result_what = self.get_result_what(dic_t=dic_t,model_is=model_is)
        
        if (result_what):
            txt += "<br><br><div><b>分析结果:</b> " + result_what + "</div><br><br>"
        
        # 调用示例
        txt += "<div>"
        txt += "<b>调用示例（建议post方式测试）:</b>  <br>"

        url_p = "api?action=" + action + "&q=" + q + "&answer=" + answer
        txt += "<div><a href=\"" + url_p + "\" target=\"_blank\">" + url_p +"</a></div>"
        txt += "</div>"
        
        # json码
        txt += "<div>"
        txt += "<br><b>返回代码:</b>  <br>"
        txt += "<div>" + result + "</div>"
        txt += "</div>"
        
        time_last = str(round(time_cost(time_start),2))
        txt += "<div><br>耗时：" + time_last + " 秒</div>"
        
        txt += "</center>"
        
        return txt
        
    def get(self):
        self.write(self.input_do())
        
    def post(self):
        self.write(self.input_do())
        
#外部调用执行模块 强调速度 系统核心模块
class Do(BaseHandler):
    
    def get_input(self):
    
        dic_a = {} # 内部参数字典 注意 所有数值全部是字符 使用时需转化
        for x in self.request.arguments:
            if x in dic_a:
                pass
            else:
                str_t = self.request.arguments[x]
                try:
                    dic_a[x] = str_t[0].decode('utf-8')
                except:
                    pass
        try:
            file = self.get_argument('file')
        except:
            file = "run"
            
        #self.write (str(dic_a)) #调试用
        
        try:
            run_model =__import__(file)
            result = run_model.run_it(dic_p=dic_a)
        except:
            result = "API调用错误"
        
        return result
        
    def get(self):
        self.write(self.get_input())
        
    def post(self):
        self.write(self.get_input())

#class CheckCodeHandler(): #验证码
    #def get(self): #HTTP GET方式
        #pass

#class SendMsgHandler(): #邮箱验证码
    #def get(self): #HTTP GET方式
        #pass

#class RegisterHandler(): #注册
    #def get(self): #HTTP GET方式
        #pass

#class UploadImageHandler(): #上传图片
    #def get(self): #HTTP GET方式
        #pass

def main():
    print("")

if __name__ == "__main__":
    main()
