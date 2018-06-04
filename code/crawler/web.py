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

#--------- 模块处理<<开始>> ---------#

#-----系统自带必备模块引用-----
import sys # 操作系统模块1

#-----系统外部需安装库模块引用-----
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.websocket

from tornado.options import define, options

#-----DIY自定义库模块引用-----
from service.handler import * #导入web路由

#--------- 模块处理<<结束>> ---------#

# ---外部参变量处理

# ---全局变量处理
###config_web_start###

#mvc配置_start
settings = {
    "template_path": 'views',    #前台渲染模板文件路径
    "static_path": 'statics',        #静态文件路径
    "static_url_prefix": '/statics/',  #静态文件前缀
    "cookie_secret": "bZJc2derneeos6GkHn/VB9oXwQt8S0R0kRvJ5/xJ89E=",        #构造函数中指定cookie_secret参数
    #"xsrf_cookies": True,       #防止cookie的跨站访问攻击
    "login_url": "/login",
    "autoreload":True,
    #"xheaders":True
    #'ui_methods': ui_methods
    }
#mvc配置_end

#路由配置_start
handler_list=[
    (r"/", IndexHandler),    #主页
    (r"/login", LoginHandler),    #登录
    (r'/logout', LogoutHandler),    #退出
    (r'/ldae', AdminHandler),    #管理
    (r'/api', Api),    #API服务
    (r'/do', Do),    #外部调用
    #(r'/autologin', AutologinHandler),    #自动登录脚本处理
    #(r"/check_code", CheckCodeHandler),  #验证码
    #(r"/send_msg", SendMsgHandler),  #邮箱验证码
    #(r"/register", RegisterHandler),  #注册
    #(r"/upload_image", UploadImageHandler),  #上传图片
    ]
#路由配置_end

###config_web_end###

# ---本模块内部类或函数定义区
def web_start():

    define("port", default=config.dic_config["web_port"], help="run on the given port", type=int)
    tornado.options.parse_command_line()
    app = tornado.web.Application(handler_list, **settings)
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()

#--------- 内部模块处理<<结束>> ---------#

#---------- 主过程<<开始>> -----------#

def main():
    #pass
    web_start() #启动网站伺服

if __name__ == "__main__":

    main()
    
#---------- 主过程<<结束>> -----------#