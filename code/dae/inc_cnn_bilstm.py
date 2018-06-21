#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''

{

"版权":"LDAE工作室",

"author":{

"1":"zhui",
"2":"吉更",

}

"初创时间:"2017年3月",

}

'''

#--------- 外部模块处理<<开始>> ---------#

#-----系统自带必备模块引用-----
import sys
from time import time
import random

#-----系统外部需安装库模块引用-----

import codecs
from collections import Counter
import numpy as np
import tensorflow as tf

#-----DIY自定义库模块引用-----
import cnn_bilstm_load_data
import cnn_bilstm_text_cnn
from diy.inc_sys import * #自定义系统级功能模块
import cnn_bilstm_config as config_cb

#--------- 外部模块处理<<结束>> ---------#

#--------- 内部模块处理<<开始>> ---------#

# 主调用函数
def run_it(str_t="",action_p="",flag=1,segment_p=""):
    
    result_c = "" # 分类结果
    time_start = time.time() # 执行时间初值
    
    txt_t = ""
    txt_t += "1," # 临时文本
    list_seg = []
    list_seg = segment_p.seg_pseg(txt_p=str_t)
    list_t = []
    for x in list_seg:
        try:
            list_t = eval(x)
        except:
            list_t = []
        if (list_t):
            txt_t += list_t[0] + "/" + list_t[1] + "|"
    txt_t = txt_t[0:-1]
    lines = [txt_t] # 待处理文本分词词性标注表达
    print ("分词词性标注表达：",lines) # 调试用
    
    word_weights, char_weights, tag_weights = cnn_bilstm_load_data.load_embedding()
    word_voc, char_voc, tag_voc, label_voc = cnn_bilstm_load_data.load_voc()

    # load data 载入数据
    
    # 采用工程模式一次输入一个短文本
    sentences_test, chars_test, tags_test, labels_test = cnn_bilstm_load_data.init_data( lines , word_voc, char_voc, tag_voc, label_voc,run_if=1)
    
    #print ("测试句：",sentences_test,"\n测试字符：", chars_test,"\n测试标签", tags_test,"\n测试标注", labels_test) # 测试用
    
    # init model 初始化模型
    
    model = cnn_bilstm_text_cnn.DCModel(
        config_cb.MAX_LEN, 
        word_weights, 
        char_weights, 
        tag_weights, 
        model_path = config_cb.DIR_MODEL,
        label_voc=label_voc
        )

    saver = tf.train.Saver()
    
    if (flag):
        saver.restore(model.sess, config_cb.TRAIN_ALL_MODEL)
    else:
        saver.restore(model.sess, config_cb.DIR_MODEL)

    pre_y,pre_proba = model.predict(sentences_test, chars_test ,tags_test)
    
    file_w = codecs.open(config_cb.path_main + 'result/predict.csv', 'a', encoding='utf-8')
    for num, scores in enumerate(pre_proba):
        result_c = model._label_voc_rev[pre_y[num]]
        try:
            file_w.write('%d,%f,%f,%f,%f,%f,%f,%f\n' % (int(model._label_voc_rev[pre_y[num]]), scores[0],scores[1],scores[2],scores[3],scores[4],scores[5],scores[6]))
        except:
            pass
    file_w.close()
    
    print('识别引擎处理时间： %d 秒!' % (time.time()-time_start)) # 调试用
    
    return result_c
    
if __name__ == '__main__':
    
    print ("")