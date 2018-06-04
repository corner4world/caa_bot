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

import sys # 操作系统模块1
import os # 操作系统模块2
import types # 数据类型
import time # 时间模块
import datetime # 日期模块

#-----系统外部需安装库模块引用-----


#-----DIY自定义库模块引用-----
sys.path.append("..")
import config #系统配置参数
import re #正则模块

#--------- 外部模块处理<<结束>> ---------#


#--------- 内部模块处理<<开始>> ---------#

# ---外部参变量处理

# ---全局变量处理


# ---本模块内部类或函数定义区
#正文识别
class Content_main(object):

    def remove_js_css (self,content):
        """ remove the the javascript and the stylesheet and the comment content (<script>....</script> and <style>....</style> <!-- xxx -->) """
        r = re.compile(r'''<script.*?</script>''',re.I|re.M|re.S)
        s = r.sub ('',content)
        r = re.compile(r'''<style.*?</style>''',re.I|re.M|re.S)
        s = r.sub ('', s)
        r = re.compile(r'''<!--.*?-->''', re.I|re.M|re.S)
        s = r.sub('',s)
        r = re.compile(r'''<meta.*?>''', re.I|re.M|re.S)
        s = r.sub('',s)
        r = re.compile(r'''<ins.*?</ins>''', re.I|re.M|re.S)
        s = r.sub('',s)
        return s

    def remove_empty_line (self,content):
        """remove multi space """
        r = re.compile(r'''^\s+$''', re.M|re.S)
        s = r.sub ('', content)
        r = re.compile(r'''\n+''',re.M|re.S)
        s = r.sub('\n',s)
        return s

    def remove_any_tag (self,s):
        s = re.sub(r'''<[^>]+>''','',s)
        return s.strip()

    def remove_any_tag_but_a (self,s):
        text = re.findall (r'''<a[^r][^>]*>(.*?)</a>''',s,re.I|re.S|re.S)
        text_b = self.remove_any_tag (s)
        return len(''.join(text)),len(text_b)

    def remove_image (self,s,n=50):
        image = 'a' * n
        r = re.compile (r'''<img.*?>''',re.I|re.M|re.S)
        s = r.sub(image,s)
        return s

    def remove_video (self,s,n=1000):
        video = 'a' * n
        r = re.compile (r'''<embed.*?>''',re.I|re.M|re.S)
        s = r.sub(video,s)
        return s

    def sum_max (self,values):
        cur_max = values[0]
        glo_max = -999999
        left,right = 0,0
        for index,value in enumerate (values):
            cur_max += value
            if (cur_max > glo_max) :
                glo_max = cur_max
                right = index
            elif (cur_max < 0):
                cur_max = 0

        for i in range(right, -1, -1):
            glo_max -= values[i]
            if abs(glo_max < 0.00001):
                left = i
                break
        return left,right+1

    def method_1 (self,content, k=1):
        if not content:
            return None,None,None,None
        tmp = content.split('\n')
        group_value = []
        for i in range(0,len(tmp),k):
            group = '\n'.join(tmp[i:i+k])
            group = self.remove_image (group)
            group = self.remove_video (group)
            text_a,text_b= self.remove_any_tag_but_a (group)
            temp = (text_b - text_a) - 8 
            group_value.append (temp)
        left,right = self.sum_max (group_value)
        return left,right, len('\n'.join(tmp[:left])), len ('\n'.join(tmp[:right]))

    def extract (self,content):
        left,right,x,y = self.method_1 (content)
        return '\n'.join(content.split('\n')[left:right])

#--------- 内部模块处理<<结束>> ---------#

#---------- 主过程<<开始>> -----------#

def main():

    print ("") #调试用
    
if __name__ == '__main__':
    
    main()
    
#---------- 主过程<<结束>> -----------#