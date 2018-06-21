#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
{

"版权":"LDAE工作室",

"author":{

"1":"zhui",
"2":"吉更",

}

"初创时间:"2017年3月",

}
"""
import cnn_bilstm_load_data
import cnn_bilstm_text_cnn 
import cnn_bilstm_config as config_cb
import codecs
from time import time
import random
from collections import Counter
import numpy as np
import sys

def train_total():

    txt = "" # 反馈值变量

    word_weights, char_weights, tag_weights = cnn_bilstm_load_data.load_embedding()
    word_voc, char_voc, tag_voc, label_voc = cnn_bilstm_load_data.load_voc()
    # train data
    sentences, chars, tags, labels = cnn_bilstm_load_data.init_data( config_cb.TRAIN_PATH , word_voc, char_voc, tag_voc, label_voc)

    # init model
    sentences_train, chars_train, tags_train, labels_train = [], [], [], []
    for i in range(0, len(labels)):
        sentences_train.append( sentences[i] )
        chars_train.append( chars[i] )
        tags_train.append( tags[i] )
        labels_train.append( labels[i] )
    
    model = cnn_bilstm_text_cnn.DCModel(
        config_cb.MAX_LEN, word_weights, char_weights, tag_weights, model_path= config_cb.DIR_MODEL,
        label_voc=label_voc)

    print(len(sentences_train), len(chars_train), len(tags_train), len(labels_train))
    print("Train distribution:", Counter(labels_train) )
    
    if (sys.argv and len(sys.argv) > 1):
        nb_epoch =  int( sys.argv[1] )
    else:
        nb_epoch = 10
    
    # fit model # 模型拟合处理
    """
    print ("主要参数：",
    sentences_train, 
    chars_train, 
    tags_train, 
    labels_train,
    config_cb.BATCH_SIZE, 
    nb_epoch, 
    config_cb.KEEP_PROB,
    config_cb.WORD_KEEP_PROB, 
    config_cb.TAG_KEEP_PROB
    ) # 调试用
    """
    nb_scores = model.fit_all(
        sentences_train, chars_train, tags_train, labels_train,
        config_cb.BATCH_SIZE, 
        nb_epoch, keep_prob=config_cb.KEEP_PROB,
        word_keep_prob=config_cb.WORD_KEEP_PROB, tag_keep_prob=config_cb.TAG_KEEP_PROB)
    
    with codecs.open(config_cb.TRAIN_RESULT_PATH + '/train_all_loss.csv', 'w', encoding='utf-8') as file_w:
        file_w.write("num_epoch,train_loss,p_train,f_train\n")
        for num, scores in enumerate(nb_scores):
            file_w.write('%d,%f,%f,%f\n' % (num+1, scores[0],scores[1],scores[2]))
    #fit_all(self, sentences_train, chars_train, tags_train, labels_train,
    #        batch_size=64, nb_epoch=40, keep_prob=1.0, word_keep_prob=1.0,
    #        tag_keep_prob=1.0, seed=137):

if __name__ == '__main__':
    t0 = time()
    # predict test data
    train_total()
    print('Done in %ds!' % (time()-t0))