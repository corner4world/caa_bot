#!/usr/bin/env python
# -*- coding: UTF-8 -*- 

'''
{
"版权":"LDAE工作室",
"author":{
"1":"腾辉",
"2":"吉更",
"3":"iron",
}
"初创时间:"2017年3月",
}
'''

#--------- 外部模块处理<<开始>> ---------#

#-----系统自带必备模块引用-----


#--------- 外部模块处理<<结束>> ---------#




#--------- 内部模块处理<<开始>> ---------#

# ---外部参变量处理

# ---全局变量处理
headers_d = {"User-Agent": ("Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/56.0.2924.87 Safari/537.36")}

# ---本模块内部类或函数定义区

# get爬取
def get_html_get(url_p="",timeout_p=28,headers_p=headers_d,chartset_p="utf-8"):
    
    import urllib # 爬虫模块
    import requests
    txt = ""
    html = requests.get(url=url_p,timeout=timeout_p, headers=headers_p)
    txt = str(html.text.encode(html.encoding), encoding=chartset_p)
    return txt
    
# post爬取
def get_html_post(url_p="",values={},timeout_p=28,headers_p=headers_d,chartset_p="utf-8"):
    
    result = ""
    
    import urllib.request
    import urllib.parse
    #import json
    
    #将字典格式化成能用的形式
    data = urllib.parse.urlencode(values).encode('utf-8')
    #创建一个request,放入我们的地址、数据、头
    request = urllib.request.Request(url_p, data, headers_p)
    #访问
    result = urllib.request.urlopen(request).read().decode('utf-8')
    #利用json解析包解析返回的json数据 拿到翻译结果
    #result = json.loads(html)
    #print (result) # 调试用
        
    return result 

#---------- 主过程<<开始>> -----------#

def main():
    print("") # 防止代码外泄 只输出一个空字符

if __name__ == '__main__':
    main()


#---------- 主过程<<结束>> -----------##