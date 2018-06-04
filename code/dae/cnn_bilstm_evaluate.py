#!/usr/bin/env python
# -*- coding: utf-8 -*-
import cnn_bilstm_load_data 
import cnn_bilstm_text_cnn
import codecs
import cnn_bilstm_config as config
from time import time
import random
from collections import Counter
import numpy as np
import tensorflow as tf
import sys

def evaluate():
    t0 = time()
    word_weights, char_weights, tag_weights = cnn_bilstm_load_data.load_embedding()
    word_voc, char_voc, tag_voc, label_voc = cnn_bilstm_load_data.load_voc()

    # load data
    sentences_test, chars_test, tags_test, labels_test = cnn_bilstm_load_data.init_data( config.TEST_PATH , word_voc, char_voc, tag_voc, label_voc)
    # init model
    print(len(labels_test))
    model = cnn_bilstm_text_cnn.DCModel(
        config.MAX_LEN, word_weights, char_weights, tag_weights, model_path = config.DIR_MODEL,
        label_voc=label_voc)

    saver = tf.train.Saver()
    flag = 0
    if int(sys.argv[1]):
        flag = 1
    if flag :
        saver.restore(model.sess, config.TRAIN_ALL_MODEL)
    else :
        saver.restore(model.sess, config.DIR_MODEL)
    
    #p_test, r_test, f_test = model.evaluate(sentences_test, chars_test ,tags_test, labels_test)
    #print('\tp_test=%f, r_test=%f, f_test=%f' % (p_test, r_test, f_test))
    p_test, r_test, f_test = model.evaluate(sentences_test, chars_test ,tags_test, labels_test)
    print('\tp_test=%f, r_test=%f, f_test=%f' % (p_test, r_test, f_test))

    print('Done in %ds!' % (time()-t0))
evaluate()