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
    
    def get_chat(self,remote_ip_p="0.0.0.0",user_host_p="0:0"):
        
        result = ""
        try:
            q = self.get_argument('q')
        except:
            q = ""
            result = "Question is null!"
        #self.write (q) #调试用
        if q:
            result = inc_chat.run_it(q,remote_ip_p=remote_ip_p,user_host_p=user_host_p) # 调用问答分析引擎
            try:
                pass
            except Exception as err:  
                print(err)  
            finally:  
                print("API is wrong!")
                
        return result
        
    def get(self):
        remote_ip = self.request.remote_ip # 获得访问端IP
        user_host = self.request.host # 获得访问端host
        self.write(self.get_chat(remote_ip_p=remote_ip,user_host_p=user_host))
        
    def post(self):
        remote_ip = self.request.remote_ip # 获得访问端IP
        user_host = self.request.host # 获得访问端host
        self.write(self.get_chat(remote_ip_p=remote_ip,user_host_p=user_host))

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
