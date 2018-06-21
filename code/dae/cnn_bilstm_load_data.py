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
import pickle
import codecs
import numpy as np
from collections import defaultdict
import cnn_bilstm_config as config
from time import time
import os

def read_lines(path):
    lines = []
    with codecs.open(path, 'r', encoding='utf-8') as file:
        for line in file.readlines():
            line = line.rstrip()
            if line:
                lines.append(line)
    return lines

def load_embedding():
    """
    加载词向量、词性向量
    Return:
        word_weights: np.array
        tag_weights: np.array
    """
    # 加载词向量
    with open(config.W2V_TRAIN_PATH, 'rb') as file_r:
        word_weights = pickle.load(file_r)
    #加载char向量
    with open(config.C2V_TRAIN_PATH, 'rb') as file_r:
        char_weights = pickle.load(file_r)
    # 加载tag向量
    with open(config.T2V_PATH, 'rb') as file_r:
        tag_weights = pickle.load(file_r)
    return word_weights, char_weights, tag_weights

def load_voc():
    """
    Load voc...
    Return:
        word_voc: dict
        tag_voc: dict
        label_voc: dict
    """
    with open(config.WORD_VOC_PATH, 'rb') as file_r:
        word_voc = pickle.load(file_r)
    with open(config.CHAR_VOC_PATH, 'rb') as file_r:
        char_voc = pickle.load(file_r)
    with open(config.TAG_VOC_PATH, 'rb') as file_r:
        tag_voc = pickle.load(file_r)
    with open(config.LABEL_VOC_PATH, 'rb') as file_r:
        label_voc = pickle.load(file_r)
    return word_voc, char_voc, tag_voc, label_voc

def _pad_sequences(sequences, pad_tok, max_length):
    """
    Args:
        sequences: a generator of list or tuple
        pad_tok: the char to pad with

    Returns:
        a list of list where each sublist has same length
    """
    sequence_padded, sequence_length = [], []
    for seq in sequences:
        seq = list(seq)
        seq_ = seq[:max_length] + [pad_tok]*max(max_length - len(seq), 0)
        sequence_padded +=  [seq_]
        sequence_length += [min(len(seq), max_length)]
    return sequence_padded, sequence_length

def pad_sequences(sequences, max_len, pad_tok, nlevels=1):
    """
    Args:
        sequences: a generator of list or tuple
        pad_tok: the char to pad with
        nlevels: "depth" of padding, for the case where we have characters ids

    Returns:
        a list of list where each sublist has same length

    """
    if nlevels == 1:
        #max_length = max(map(lambda x : len(x), sequences))
        max_length = max_len
        sequence_padded, sequence_length = _pad_sequences(sequences,
                                            pad_tok, max_length)

    elif nlevels == 2:
        max_length_word = max([max(map(lambda x: len(x), seq))
                               for seq in sequences])
        sequence_padded, sequence_length = [], []
        for seq in sequences:
            # all words are same length now
            sp, sl = _pad_sequences(seq, pad_tok, max_length_word)
            sequence_padded += [sp]
            sequence_length += [sl]

        #max_length_sentence = max(map(lambda x : len(x), sequences))
        max_length_sentence = max_len
        sequence_padded, _ = _pad_sequences(sequence_padded,
                [pad_tok]*max_length_word, max_length_sentence)
        sequence_length, _ = _pad_sequences(sequence_length, 0,
                max_length_sentence)

    return sequence_padded, sequence_length

def map_item2id(items, voc, max_len, none_word=0, lower=False):
    """
    将word/pos等映射为id
    Args:
        items: list, 待映射列表
        voc: 词表
        max_len: int, 序列最大长度
        none_word: 未登录词标号,默认为0
    Returns:
        arr: np.array, dtype=int32, shape=[max_len,]
    """
    assert type(none_word) == int
    arr = np.zeros((max_len,), dtype='int32')
    min_range = min(max_len, len(items))
    for i in range(min_range):  # 若items长度大于max_len，则被截断
        item = items[i] if not lower else items[i].lower()
        arr[i] = voc[item] if item in voc else none_word
    return arr

def map_char2id(items, voc, none_word=0, lower=False):
    arr = []
    for word in items:
        tmp = []
        for j in word:
            item = j if not lower else j.lower()
            tmp.append( voc[item] if item in voc else none_word )
        arr.append(tmp)
    return arr
    
def get_sentence_arr(words_tags, word_voc, char_voc, tag_voc):
    """
    获取词序列
    Args:
        words_tags: list, 句子 and tags
        word_voc: 词表
        tag_voc: 词性标注表
    Returns:
        sentence_arr: np.array, 字符id序列
        tag_arr: np.array, 词性标记序列
    """
    words, chars, postags = [], [], []
    for item in words_tags:
        try:
            rindex = item.rindex('/')
        except:
            continue
        word = item[:rindex]
        words.append(word)
        tmp = []
        for c in word:
            tmp.append(c)
        chars.append(tmp)
        postags.append(item[rindex+1:])
    # sentence arr
    sentence_arr = map_item2id(
        words, word_voc, config.MAX_LEN, none_word = 1, lower=True)
    # pos tags arr
    postag_arr = map_item2id(
        postags, tag_voc, config.MAX_LEN, none_word = 1, lower=False)
    
    char_arr = map_char2id(chars, char_voc, none_word = 1, lower=True)
    
    return sentence_arr, char_arr, postag_arr, len(words)

def init_data(path, word_voc, char_voc, tag_voc, label_voc,run_if=0):
    """
    加载数据
    Args:
        lines: list
        word_voc: dict, 词表
        tag_voc: dict, 词性标注表
        label_voc: dict
    Returns:
        sentences: np.array
        etc.
    """
    
    # 工程执行模式判别
    if (run_if==1):
        lines = path
        data_count = 1
    else:
        lines = read_lines(path)
        data_count = len(lines)
        
    sentences = np.zeros((data_count, config.MAX_LEN), dtype='int32')
    tags = np.zeros((data_count, config.MAX_LEN), dtype='int32')
    sentence_actual_lengths = np.zeros((data_count,), dtype='int32')
    labels = np.zeros((data_count,), dtype='int32')
    chars = []
    instance_index = 0
    for i in range(data_count):
        index = lines[i].index(',')
        label = lines[i][:index]
        sentence = lines[i][index+1:]
        words_tags = sentence.split('|')
        sentence_arr, char_arr, tag_arr, actual_length = get_sentence_arr(words_tags, word_voc, char_voc, tag_voc)
        chars.append(char_arr)
        sentences[instance_index, :] = sentence_arr
        tags[instance_index, :] = tag_arr
        sentence_actual_lengths[instance_index] = actual_length
        labels[instance_index] = label_voc[label] if label in label_voc else 0
        instance_index += 1
    return sentences, chars, tags, labels

# 模块运行主程序
def run_it():

    t0 = time()
    word_weights, char_weights, tag_weights = load_embedding()
    word_voc, char_voc, tag_voc, label_voc = load_voc()
    train_sentences, train_chars, train_tags, train_labels = init_data( config.TRAIN_PATH, word_voc, char_voc, tag_voc, label_voc)
    test_sentences, test_chars, test_tags, _ = init_data( config.TEST_PATH, word_voc, char_voc, tag_voc, label_voc)
    print('cnn_bilstm_load_data Done in %ds!' % (time()-t0))

if __name__ == '__main__':

    print("")