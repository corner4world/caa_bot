  #!/usr/bin/env python
# -*- coding: UTF-8 -*-  

'''
{
"版权":"LDAE工作室",
"author":{
"1":"吉庚",
"2":"腾辉",
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
import inc_chat # 引用对话模块
import inc_hot # 引用热点模块
import inc_link # 引用热点模块
import diy.inc_file as inc_file # 基本自定义文件模块

#-----DIY自定义库模块引用-----

#--------- 外部模块处理<<结束>> ---------#


#--------- 内部模块处理<<开始>> ---------#

# ---外部参变量处理

# ---全局变量处理

# ---本模块内部类或函数定义区

# web服务基础模块
class BaseHandler(tornado.web.RequestHandler):

    def set_default_headers(self):
        print ("setting headers!!!")
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')

    def get_current_user(self):
        return self.get_secure_cookie("username")
    #用户检查
    def user_check(self,conn_p,username_p,password_p):
        
        res_m = 0 #数据库记录数
        username = "" #数据库内用户名
        roles = "" #数据库内用户权限
        
        username_p = hash_make(hash_make(username_p)) #密文处理
        password_p = hash_make(hash_make(password_p)) #密文处理
        
        #查询用户管理数据库
        sql = "select username,roles from user_main where username='" + username_p + "' and password = '" + password_p + "' order by id desc limit 0,1"
        self.write (str_split(datetime.datetime.now()) + " ::: " + sql) #调试用
        res_m, rows_m = conn_p.read_sql(sql)
        
        if (res_m > 0): 
            username = rows_m[0][0]
            roles = rows_m[0][1]
            roles = hash_make(hash_make(roles))
            
        return res_m , username , roles

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
        
# 快速咨询模块
class Search(tornado.web.RequestHandler):
    
    def get(self,*args):
        
        self.render('search.html',
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
        
# 热点追踪模块
class Hot(tornado.web.RequestHandler):
    
    def get(self,*args):
        
        # 参数处理
        result = "" # 处理结果
        page = 1 #分页数
        action = "list" # 默认功能是列表展示
        
        try:
            page = int(self.get_argument('page'))
        except:
            pass
        #self.write(str(page) + " - ") #调试用
        try:
            action = self.get_argument('action')
        except:
            pass
        #self.write(action + " - ") #调试用
        
        # 调用热点分析引擎
        if (action == "list"):
            result = inc_hot.run_it(page_p=page,test_if=int(config.dic_config["test_if"]))
            self.write(result) #调试用
            
        
# 快速咨询模块
class Qa(tornado.web.RequestHandler):
    
    def get(self,*args):
        
        self.render('qa.html',
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
        
# 快速咨询模块
class Link(tornado.web.RequestHandler):
    
    def get(self,*args):
        
        # 参数处理
        result = "" # 处理结果
        page = 1 #分页数
        action = "list" # 默认功能是列表展示
        
        try:
            page = int(self.get_argument('page'))
        except:
            pass
        #self.write(str(page) + " - ") #调试用
        try:
            action = self.get_argument('action')
        except:
            pass
        #self.write(action + " - ") #调试用
        
        # 调用热点分析引擎
        if (action == "list"):
            result = inc_link.run_it(page_p=page)
            self.write(result) #调试用
        
# 生存预测
class Alive(tornado.web.RequestHandler):
    
    def get(self,*args):
        
        self.render('alive.html',
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
        
# 费用估算
class Cost(tornado.web.RequestHandler):
    
    def get(self,*args):
        
        self.render('cost.html',
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
    def power_is(self,roles_p):

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
        admin_roles=self.power_is(str_roles),
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

# 自动登录模块
class AutologinHandler(BaseHandler):

    def get(self):

        #查询文件数据库
        sql = "select username,roles from session_admin where password='" + self.get_argument('md5_user') + "'"
        #self.write (str_split(datetime.datetime.now()) + " ::: " + sql) #调试用
        res_m, rows_m = rs_sqlite_file.read_sql(sql)
        
        if ( res_m > 0 ):
        
            username = rows_m[0][0]
            roles = rows_m[0][1]
            roles = hash_make(hash_make(roles))
            surl = self.get_argument('surl')
            surl = surl.replace("~!~","?")
            surl = surl.replace("~~","&")
            self.set_secure_cookie("username", username)
            self.set_secure_cookie("roles", roles)
            self.set_secure_cookie("time_login", str_split(datetime.datetime.now()))
            #self.write ("<br>" + surl) #调试用
            self.redirect(surl)
            
        else:
        
            self.write ("<br> 登录不成功!,请重启管理软件！")
            #self.redirect("/login")

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
    
    def get_chat(self):
        
        result = ""
        dic_user = {}
        str_t = ""
        
        # 构造必要的参数字典
        # 获取用户网络参数
        try:
            dic_user["remote_ip"] = self.request.remote_ip
            dic_user["headers"] = self.request.headers
        except:
            pass
        # 用户身份参数
        
        try:
            str_t = self.get_secure_cookie("session_ldae_user")
            str_t = str_t.decode('utf-8')
            # 解密session字典
            str_t = secret_ldae(str_t,key_p=config.dic_config["secret_key"],salt_p = config.dic_config["secret_salt"],secret_if="no")
            dic_user["session"] = eval(str_t)
        except:
            dic_user["session"] = {}
            
        #print ("参数字典",dic_user) # 调试用
        
        try:
            q = self.get_argument('q')
        except:
            q = ""
            result = "Question is null!"
        try:
            action = self.get_argument('action')
        except:
            action = "chat"

        #self.write (q) #调试用
        if (action == "chat"):
        
            result = inc_chat.run_it(q,dic_user) # 调用问答分析引擎
            
            try:
                pass
            except Exception as err:  
                print(err)  

                
            return result
            
        if (action == "search"):
        
            result = inc_chat.run_it(q,dic_user) # 调用问答分析引擎
            
            try:
                pass
            except Exception as err:  
                print(err)  

                
            return result
            
        if (action == "search_tag_xml"):
            
            result = ""
            import search_tag_xml # 导入输入提示模块
            #print (self.request.arguments)
            try:
                result = search_tag_xml.run_it(self.request.arguments)
            except:
                pass
                
            #print (result) # 调试用
            return result
                
        return result
        
    def get(self):
        print("用户提交方式:","get")
        self.write(self.get_chat())
        
    def post(self):
        print("用户提交方式:","post")
        self.write(self.get_chat())

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
