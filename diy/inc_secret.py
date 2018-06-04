#!/usr/bin/env python
# -*- coding: UTF-8 -*- 

'''
{
"版权":"LDAE工作室",
"author":{
"1":"power",
"2":"吉更",
"3":"腾辉",
}
"初创时间:"2017年3月",
}
'''
#--------- 外部模块处理<<开始>> ---------#

#-----系统自带必备模块引用-----

import sys # 操作系统模块1
import os # 系统模块
import base64 # base64加密模块
import pickle # 存取结构化数据模块
import hashlib # hashlib加密模块
import psutil # 系统库

#-----系统外部需安装库模块引用-----

from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

#-----DIY自定义库模块引用-----
sys.path.append("..")
import diy.inc_file  as inc_file #自定义文件处理功能模块
#--------- 外部模块处理<<结束>> ---------#


#--------- 内部模块处理<<开始>> ---------#

# ---外部参变量处理

# ---全局变量处理


# ---本模块内部类或函数定义区

# 加密的基础类
class Secret_base(object):

    # 进行加解密处理
    def secret_do(self,file_p,key_p="ldae_is_good", secret_if=1):

        burst_if = 0
        password=bytes(key_p, encoding="utf-8")
        salt = b"llddaaeeiissookk"
        kdf = PBKDF2HMAC(algorithm=hashes.SHA256(),length=32,salt=salt,iterations=100000,backend=default_backend())
        #kdf = PBKDF2HMAC(algorithm=hashes.SHA224,length=32,salt=b"123",iterations=100000,backend=default_backend())
        jey = base64.urlsafe_b64encode(kdf.derive(password))
        key = Fernet(jey)
        #文件操作实例
        file_do = inc_file.File_base()
        
        file_size = file_do.getDocSize(file_p)
        print ("\n文件大小：" + file_size )
        print ("(file_sizes：" + file_size +")\n")
            
        #超过系统内存某阈值值分片
        mem = psutil.virtual_memory()
        numb_mem_free = float(mem.total)
        numb_mem_free = numb_mem_free/1024/1024/1024/8 #可占用内存估计阈值
        
        if ("G" in file_size):
            numb_size = float(file_size.replace(" G",""))
            if (numb_size > numb_mem_free):
                burst_if = 1
        if ("M" in file_size):
            numb_size = float(file_size.replace(" M",""))
            if (numb_size > numb_mem_free*1024):
                burst_if = 1
                
        # 加密处理
        if secret_if == 1:
            
            # ----- 分片处理开始 -----
            if (burst_if > 0):
                
                print ("\n文件大于 " + str(int(numb_mem_free)) + "G，进行分片处理......")
                print ("(Sizes of file is more than 512M,so it is burstting......)\n")

                f = open(key_p + ".txt", 'a',encoding="utf-8")
                
                try:
                
                    t = open(file_p, 'r', encoding="utf-8")
                    
                except:
            
                    t = open(file_p, 'r')
                
                for line in t:
                
                    str_t = line
                    str_t = str_t.encode("utf-8")
                    token = key.encrypt(str_t) # 加密
                    f.write(str(token) + "\r\n") 
                    
                f.close()
                t.close()
                
                os.remove(file_p)
                os.rename(key_p + ".txt",file_p)
                
                return True

            # ----- 分片处理结束 -----
            
            # ----- 非分片处理开始 -----
            if (burst_if == 0):
            
                try:
                
                    t = open(file_p, 'r', encoding="utf-8")
                    text = t.read()
                    text = text.encode("utf-8")
                    t.close()
            
                except:
            
                    t = open(file_p, 'r')
                    text = t.read()
                    text = text.encode("utf-8")
                    t.close()
        
                try:
            
                    token = key.encrypt(text) # 加密
                    #print(token) # 调试用
        
                    f = open(file_p, 'wb')
                    f.write(token)
                    f.close()
                    return True
    
                except:
            
                    print ("\nThe running is bad!Try it again,please!\n")
                    return False
                    pass
                
            # ----- 非分片处理结束
                
            return True
        
        # 解密处理
        if secret_if == 2:
            
            # ----- 分片解密开始 -----
            if (burst_if == 1):
                
                print ("\n文件大于512M，进行分片处理......")
                print ("(Sizes of file is more than 512M,so it is burstting......)\n")
            
                f = open(key_p + ".txt", 'w')
                t = open(file_p,'r',encoding="utf-8")
                
                for line in t:
                
                    if (line != "\n"):
                        line = line.replace("b'","")
                        line = line.replace("'","")
                        line = line.replace("\n","")
                        byte_t = line.encode("utf-8")
                        #print (byte_t) #调试用
                        try:
                            source_str = key.decrypt(byte_t)
                            source_str = source_str.decode("utf-8") # 解密
                            f.write(source_str)
                        except:
                            pass
                f.close()
                t.close()
                
                os.remove(file_p)
                os.rename(key_p + ".txt",file_p)
                
                return True
                
            # ----- 分片解密结束 -----
            
            # ----- 非分片解密开始 -----
            if (burst_if == 0):
            
                text = open(file_p, 'rb').read()
                if (text[0:5] != b"gAAAA"):
            
                    print ("\n源文件不是加密文件，请再试一次!")
                    print ("The file is not a Secret file!Try it again,please!\n")
                    return False
                try:
            
                    source_str = key.decrypt(text)
                    source_str = source_str.decode("utf-8") # 解密
            
                except:
            
                    print ("\n密钥错误，请再试一次!")
                    print ("The key is wrong!Try it again,please!\n")
                    return False
            
                try:
        
                    f = open(file_p, 'w', encoding="utf-8")
                    f.write(source_str)
                    f.close()
                    return True
        
                except:

                    f = open(file_p, 'w')
                    f.write(source_str)
                    f.close()
                    return True
                
            # ----- 非分片解密结束 -----
            
            return True