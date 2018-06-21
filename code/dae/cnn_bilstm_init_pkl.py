#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pickle
import codecs
import numpy as np
from collections import defaultdict
import cnn_bilstm_config as config_cb
import os
from time import time

def read_lines(path):
    lines = []
    with codecs.open(path, 'r', encoding='utf-8') as file:
        for line in file.readlines():
            line = line.rstrip()
            if line:
                lines.append(line)
    return lines

def create_dictionary(token_dict, dic_path, start=0, sort=False,
                      min_count=None, lower=False, overwrite=False):
    """
    构建字典，并将构建的字典写入pkl文件中
    Args:
        token_dict: dict, [token_1:count_1, token_2:count_2, ...]
        dic_path: 需要保存的路径(以pkl结尾)
        start: int, voc起始下标，默认为0
        sort: bool, 是否按频率排序, 若为False，则按items排序
        min_count: int, 词最少出现次数，低于此值的词被过滤
        lower: bool, 是否转为小写
        overwrite: bool, 是否覆盖之前的文件
    Returns:
        voc size: int
    """
    if os.path.exists(dic_path) and not overwrite:
        return 0
    voc = dict()
    if sort:
        # sort
        token_list = sorted(token_dict.items(), key=lambda d: d[1], reverse=True)
        for i, item in enumerate(token_list):
            if min_count and item[1] < min_count:
                continue
            index = i + start
            key = item[0]
            voc[key] = index
    else:  # 按items排序
        if min_count:
            items = sorted([item[0] for item in token_dict.items() if item[1] >= min_count])
        else:
            items = sorted([item[0] for item in token_dict.items()])
        for i, item in enumerate(items):
            item = item if not lower else item.lower()
            index = i + start
            voc[item] = index
    # 写入文件
    file = open(dic_path, 'wb')
    pickle.dump(voc, file)
    file.close()
    
    return len(voc.keys())

def init_voc():
    """
    初始化voc
    """
    lines = read_lines(config_cb.TRAIN_PATH)
    lines += read_lines(config_cb.TEST_PATH)
    words = []  # 句子
    pos_tags = []  # 词性标记类型
    sequence_length_dict = defaultdict(int)
    words_dict = defaultdict(int)
    char_dict = defaultdict(int)
    tags_dict = defaultdict(int)
    labels_dict = defaultdict(int)
    
    for line in lines:
    
        index = line.index(',')
        labels_dict[line[0:index]] += 1
        sentence = line[index+1:]
        # words and tags
        words_tags = sentence.split('|')
        sequence_length_dict[ len(words_tags) ] += 1
        
        for item in words_tags:
            
            try:
                r_index = item.rindex('/')
            except:
                continue
            word, tag = item[:r_index], item[r_index+1:]
            words_dict[word] += 1
            tags_dict[tag] += 1
            
            for w in word:
                #if 's' in w:
                    #print(word)
                char_dict[w.lower()] += 1
            
    # word voc
    word_size = create_dictionary(
        words_dict, config_cb.WORD_VOC_PATH, start=config_cb.WORD_VOC_START,
        min_count=0, sort=True, lower=True, overwrite=True)
    
    # char voc
    char_size = create_dictionary(
        char_dict, config_cb.CHAR_VOC_PATH, start=config_cb.CHAR_VOC_START,
        min_count=0, sort=True, lower=True, overwrite=True)
    
    # tag voc
    tag_size = create_dictionary(
        tags_dict, config_cb.TAG_VOC_PATH, start=config_cb.TAG_VOC_START,
        sort=True, lower=False, overwrite=True)
    
    # label voc
    #label_types = [str(i) for i in range(1, 7)]
    label_size = create_dictionary(
        labels_dict, config_cb.LABEL_VOC_PATH, start=0, overwrite=True)
        
    print("word_size:", word_size)
    print("char_size:", char_size)
    print("tag_size:",  tag_size)
    print("label_size", label_size)
    print('句子长度分布:')
    print(sorted(sequence_length_dict.items()))
    print('done!')
    
    return char_dict


##############################dump embedding#################################

def load_embed_from_txt(path):
    """
    读取txt文件格式的embedding
    Args:
        path: str, 路径
        start: int, 从start开始读取, default is 1
    Returns:
        embed_dict: dict
    """
    file_r = codecs.open(path, 'r', encoding='utf-8')
    line = file_r.readline()
    voc_size, vec_dim = map(int, line.split(' '))
    embedding = dict()
    line = file_r.readline()
    while line:
        items = line.split(' ')
        item = items[0]
        try:
            vec = np.array(items[1:], dtype='float32')
        except:
            print(item)
        embedding[item] = vec
        line = file_r.readline()
    return embedding, vec_dim

def init_word_embedding(path=None, overwrite=False):
    """
    初始化word embedding
    Args:
        path: 结果存放路径
    """
    if os.path.exists(path) and not overwrite:
        return
    path_pre_train = config_cb.EMBEDDING_ROOT + '/word_embedding.txt'
    if not os.path.exists(path_pre_train) :
        return
    
    with open(config_cb.WORD_VOC_PATH, 'rb') as file_r:
        voc = pickle.load(file_r)
    embedding_dict, vec_dim = load_embed_from_txt(path_pre_train)
    word_voc_size = len(voc.keys()) + config_cb.WORD_VOC_START
    embedding_matrix = np.zeros((word_voc_size, vec_dim), dtype='float32')
    for item in voc:
        if item in embedding_dict:
            embedding_matrix[voc[item], :] = embedding_dict[item]
        else:
             embedding_matrix[voc[item], :] = np.random.uniform(-0.25, 0.25, size=(vec_dim))
            
    embedding_matrix[1, :] = np.random.uniform(-0.25, 0.25, size=(vec_dim))
    with open(path, 'wb') as file_w:
        pickle.dump(embedding_matrix, file_w)
    
def init_char_embedding(path=None, overwrite=False):
    """
    初始化word embedding
    Args:
        path: 结果存放路径
    """
    if os.path.exists(path) and not overwrite:
        return
    
    path_pre_train = config_cb.EMBEDDING_ROOT  + "/char_embedding.txt"
    if not os.path.exists(path_pre_train) :
        return
    
    with open(config_cb.CHAR_VOC_PATH, 'rb') as file_r:
        voc = pickle.load(file_r)
    embedding_dict, vec_dim = load_embed_from_txt(path_pre_train)
    char_voc_size = len(voc.keys()) + config_cb.CHAR_VOC_START
    embedding_matrix = np.zeros((char_voc_size, vec_dim), dtype='float32')
    for item in voc:
        if item in embedding_dict:
            embedding_matrix[voc[item], :] = embedding_dict[item]
        else:
            embedding_matrix[voc[item], :] = np.random.uniform(-0.25, 0.25, size=(vec_dim))
    embedding_matrix[1, :] = np.random.uniform(-0.25, 0.25, size=(vec_dim))
    with open(path, 'wb') as file_w:
        pickle.dump(embedding_matrix, file_w) 
        
def init_tag_embedding(path, overwrite=False):
    """
    初始化pos tag embedding
    Args:
        path: 结果存放路径
    """
    if os.path.exists(path) and not overwrite:
        return
    with open(config_cb.TAG_VOC_PATH, 'rb') as file:
        tag_voc = pickle.load(file)
    tag_voc_size = len(tag_voc.keys()) + config_cb.TAG_VOC_START
    tag_weights = np.random.normal(
        size=(tag_voc_size, config_cb.TAG_DIM)).astype('float32')
    for i in range(config_cb.TAG_VOC_START):
        tag_weights[i, :] = 0.
    with open(path, 'wb') as file:
        pickle.dump(tag_weights, file, protocol=2)
        
def init_embedding():
    """
    初始化embedding嵌入层
    """
    if not os.path.exists(config_cb.EMBEDDING_ROOT):
        os.mkdir(config_cb.EMBEDDING_ROOT)
        
    # 初始化word_embedding
    init_word_embedding(config_cb.W2V_TRAIN_PATH, overwrite=True)
    
    # 初始化char_embedding
    init_char_embedding(config_cb.C2V_TRAIN_PATH, overwrite=True)
    
    # 初始化tag_embedding
    init_tag_embedding(config_cb.T2V_PATH, overwrite=True)

if __name__ == '__main__':
    
    t0 = time()
    init_voc() # 初始化主模型数据
    print('init_voc Done in %.1fs!' % (time()-t0))

    t0 = time()
    init_embedding()  # 初始化embedding嵌入层
    print('init_embedding Done in %.1fs!' % (time()-t0))