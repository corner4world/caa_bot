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
import os

#-----DIY自定义库模块引用-----
import config #系统配置参数
from diy.inc_sys import * #自定义系统级功能模块

#--------- 外部模块处理<<结束>> ---------#

path_main = config.dic_config["path_cnn_bilstm"] # 数据主路径

# --- corpus ---
TRAIN_PATH = config.dic_config["path_cnn_bilstm"] + 'corpus/training.seg.csv'
TEST_PATH = config.dic_config["path_cnn_bilstm"] + 'corpus/testing.seg.csv'

# --- voc ---
VOC_ROOT = config.dic_config["path_cnn_bilstm"] + 'voc'
if not os.path.exists(VOC_ROOT):
    os.mkdir(VOC_ROOT)
WORD_VOC_PATH = VOC_ROOT + '/word_voc.pkl'
WORD_VOC_START = 2
CHAR_VOC_PATH = VOC_ROOT + '/char_voc.pkl'
CHAR_VOC_START = 2
TAG_VOC_PATH = VOC_ROOT + '/tag_voc.pkl'
TAG_VOC_START = 2

LABEL_VOC_PATH = VOC_ROOT + '/label_voc.pkl'


# --- embedding ---
W2V_DIM = 128
C2V_DIM = 128
W2V_PATH = config.dic_config["path_cnn_bilstm"] + 'embedding/word2vec.pkl'
#W2V_PATH = config.dic_config["path_cnn_bilstm"] + 'embedding/WORD_word2vec.pkl'
EMBEDDING_ROOT = config.dic_config["path_cnn_bilstm"] + 'embedding'
if not os.path.exists(EMBEDDING_ROOT):
    os.mkdir(EMBEDDING_ROOT)
W2V_TRAIN_PATH = EMBEDDING_ROOT + '/word2v.pkl'
C2V_TRAIN_PATH = EMBEDDING_ROOT + '/char2v.pkl'
T2V_PATH = EMBEDDING_ROOT + '/tag2v.pkl'
TAG_DIM = 64

DIR_MODEL_ROOT = config.dic_config["path_cnn_bilstm"] + 'model'
if not os.path.exists(DIR_MODEL_ROOT):
    os.mkdir(DIR_MODEL_ROOT)
DIR_MODEL = DIR_MODEL_ROOT + "/best_model_new_new_two"

TRAIN_ALL_MODEL = DIR_MODEL_ROOT + "/all_data_model"

# --- training param ---
MAX_LEN = 95
BATCH_SIZE = 128
NB_LABELS = 7
NB_EPOCH = 50
KEEP_PROB = 0.5
WORD_KEEP_PROB = 0.8
TAG_KEEP_PROB = 0.8
use_chars = True 
PATIENT = 10