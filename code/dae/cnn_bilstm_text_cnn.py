#!/usr/bin/env python
# -*- coding: utf-8 -*-
from tqdm import tqdm
import os
from time import time
import cnn_bilstm_config as config
import tensorflow as tf
import numpy as np
from TFNN.layers.EmbeddingLayer import Embedding
from TFNN.layers.DenseLayer import SoftmaxDense
from TFNN.layers.ConvolutionalLayer import Convolutional1D
from TFNN.utils.evaluate_util import sim_compute
from TFNN.utils.tensor_util import zero_nil_slot
import codecs
from collections import Counter
import  random
import cnn_bilstm_load_data

import sys
import time
from diy.inc_sys import * #自定义系统级功能模块

class DCModel(object):

    def __init__(self, max_len, word_weights, char_weights, tag_weights, model_path=None, label_voc=None):
        """
        Initilize model
        Args:
            max_len: int, 句子最大长度
            word_weights: np.array, shape=[|V_words|, w2v_dim]，词向量
            tag_weights: np.array, shape=[|V_tags|, t2v_dim],标记向量
            result_path: str, 模型评价结果存放路径
            label_voc: dict
        """
        tf.reset_default_graph() 
        self._model_path = model_path
        self._label_voc = label_voc
        self._label_voc_rev = dict()
        
        for key in self._label_voc:
            value = self._label_voc[key]
            self._label_voc_rev[value] = key

        # input placeholders
        self.input_sentence_ph = tf.placeholder(
            tf.int32, shape=(None, max_len), name='input_sentence_ph')
        self.input_tag_ph = tf.placeholder(tf.int32, shape=(None, max_len), name='input_tag_ph')
        self.label_ph = tf.placeholder(tf.int32, shape=(None,), name='label_ph')
        self.keep_prob_ph = tf.placeholder(tf.float32, name='keep_prob')
        self.word_keep_prob_ph = tf.placeholder(tf.float32, name='word_keep_prob')
        #self.word_keep_prob_ph = tf.placeholder(tf.float32, name='word_keep_prob')
        self.tag_keep_prob_ph = tf.placeholder(tf.float32, name='tag_keep_prob')
        
        # shape = (batch size, max length of sentence, max length of word)
        self.input_char_ph = tf.placeholder(tf.int32, shape=[None, None, None],
                        name="char_ids")
        # shape = (batch_size, max_length of sentence)
        self.word_lengths = tf.placeholder(tf.int32, shape=[None, None],
                        name="word_lengths")

        # embedding layers
        self.nil_vars = set()
        word_embed_layer = Embedding(
            params=word_weights, ids=self.input_sentence_ph,
            keep_prob=self.word_keep_prob_ph, name='word_embed_layer')
        
        tag_embed_layer = Embedding(
            params=tag_weights, ids=self.input_tag_ph,
            keep_prob=self.tag_keep_prob_ph, name='tag_embed_layer')
        
        self.nil_vars.add(word_embed_layer.params.name)
        self.nil_vars.add(tag_embed_layer.params.name)

        if config.use_chars:
            # get char embeddings matrix
            char_embed_layer = Embedding(
            params=char_weights, ids=self.input_char_ph, name='char_embed_layer')
            self.nil_vars.add(char_embed_layer.params.name)
            # put the time dimension on axis=1
            
            char_embeddings = char_embed_layer.output
            s = tf.shape(char_embeddings)
            char_embeddings = tf.reshape(char_embeddings,
                    shape=[s[0]*s[1], s[-2], config.C2V_DIM])
            word_lengths = tf.reshape(self.word_lengths, shape=[s[0]*s[1]])
            # bi lstm on chars
            cell_fw = tf.contrib.rnn.LSTMCell(128, forget_bias=1.0, #config.hidden_size_char,
                    state_is_tuple=True)
            cell_bw = tf.contrib.rnn.LSTMCell(128, forget_bias=1.0, #config.hidden_size_char,
                    state_is_tuple=True)
            _output = tf.nn.bidirectional_dynamic_rnn(
                    cell_fw, cell_bw, char_embeddings,time_major=False,
                    sequence_length=word_lengths, dtype=tf.float32)

            # read and concat output
            _, ((_, output_fw), (_, output_bw)) = _output
            output = tf.concat([output_fw, output_bw], axis=-1)

            # shape = (batch size, max sentence length, char hidden size)
            output = tf.reshape(output,
                    shape=[s[0], s[1], 2*128]) #self.config.hidden_size_char])

            other_embedding = tf.concat([output, tag_embed_layer.output], axis=-1)
        else :
            other_embedding = tag_embed_layer.output
        
        # sentence representation
        sentence_input = tf.concat(
            values=[word_embed_layer.output, other_embedding], axis=2)

        ####################
        sentence_input1  = tf.transpose(sentence_input,[0,2,1])
        conv_layer1 = Convolutional1D(
            input_data=sentence_input1, filter_length=3,
            nb_filter=1000, activation='relu', name='conv_layer')
        
        # sentence conv
        conv_layer = Convolutional1D(
            input_data=sentence_input, filter_length=3,
            nb_filter=1000, activation='relu', name='conv_layer')

        # dense layer
        conv_output = tf.concat([conv_layer.output, conv_layer1.output], axis=-1)
        dense_input_drop = tf.nn.dropout(conv_output, self.keep_prob_ph)
        self.dense_layer = SoftmaxDense(
            input_data=dense_input_drop, input_dim=conv_layer.output_dim + conv_layer1.output_dim,
            output_dim=config.NB_LABELS, name='output_layer')

        self.loss = self.dense_layer.loss(self.label_ph) + \
            0.001*tf.nn.l2_loss(self.dense_layer.weights)
        optimizer = tf.train.AdamOptimizer()  # Adam
        grads_and_vars = optimizer.compute_gradients(self.loss)
        nil_grads_and_vars = []
        for g, v in grads_and_vars:
            if v.name in self.nil_vars:
                nil_grads_and_vars.append((zero_nil_slot(g), v))
            else:
                nil_grads_and_vars.append((g, v))
        global_step = tf.Variable(0, name='global_step', trainable=False)

        # train op
        self.train_op = optimizer.apply_gradients(
            nil_grads_and_vars, name='train_op', global_step=global_step)

        # pre op
        self.pre_op = self.dense_layer.get_pre_y()
        #self.pre_ouput_op = self.dense_layer.output()
        self.proba_op = self.dense_layer.get_pre_proba()

        # summary
        gpu_options = tf.GPUOptions(visible_device_list='0', allow_growth=True)
        self.sess = tf.Session(config=tf.ConfigProto(gpu_options=gpu_options))

        # init model
        init = tf.global_variables_initializer()
        self.sess.run(init)

    def fit(self, sentences_train, chars_train, tags_train, labels_train,
            sentences_dev=None, chars_dev = None, tags_dev=None, labels_dev=None,
            sentences_test=None, chars_test = None ,tags_test=None, labels_test=None,
            batch_size=64, nb_epoch=40, keep_prob=1.0, word_keep_prob=1.0,
            tag_keep_prob=1.0, seed=137):
        """
        fit model
        Args:
            sentences_train, tags_train, labels_train: 训练数据
            sentences_dev, tags_dev, labels_dev: 开发数据
            batch_size: int, batch size
            nb_epoch: int, 迭代次数
            keep_prob: float between [0, 1], 全连接层前的dropout
            word_keep_prob: float between [0, 1], 词向量层dropout
            tag_keep_prob: float between [0, 1], 标记向量层dropout
        """
        self.saver = tf.train.Saver()
        self.nb_epoch_scores = []  # 存放nb_epoch次迭代的f值
        n_total = len( labels_train )
        nb_train = 0
        if int( n_total / batch_size) == (n_total *1.0 / batch_size):
            nb_train = int(n_total/ batch_size)
        else :
            nb_train = int(n_total / batch_size) + 1
        best_score = 0.0
        nepoch_no_imprv = 0
        for step in range(nb_epoch):
            print('Epoch %d / %d:' % (step+1, nb_epoch))
            # shuffle
            #np.random.seed(seed)
            #np.random.shuffle(sentences_train)
            #np.random.seed(seed)
            #np.random.shuffle(tags_train)
            #np.random.seed(seed)
            #np.random.shuffle(labels_train)
            #np.random.seed
            #np.random.
            # train
            total_loss = 0.
            for i in tqdm( range(nb_train) ):
                # for i in range(nb_train):
                #start =  i * batch_size % n_total
                if (i+1)*batch_size >= n_total:
                    sentences_feed = sentences_train[i * batch_size:] + sentences_train[0:(i+1) * batch_size-n_total]
                    tags_feed = tags_train[i * batch_size:] + tags_train[0:(i+1) * batch_size-n_total]
                    labels_feed = labels_train[i * batch_size:] + labels_train[0:(i+1) * batch_size-n_total]
                    char_ids = chars_train[i * batch_size:] + chars_train[0:(i+1) * batch_size-n_total]
                else :
                    sentences_feed = sentences_train[i*batch_size:(i+1)*batch_size]
                    tags_feed = tags_train[i*batch_size:(i+1)*batch_size]
                    labels_feed = labels_train[i*batch_size:(i+1)*batch_size]
                    char_ids = chars_train[i*batch_size:(i+1)*batch_size]
                
                feed_dict = {
                        self.input_sentence_ph: sentences_feed,
                        self.input_tag_ph: tags_feed,
                        self.label_ph: labels_feed,
                        self.keep_prob_ph: keep_prob,
                        self.word_keep_prob_ph: word_keep_prob,
                        self.tag_keep_prob_ph: tag_keep_prob,
                    }
                if config.use_chars:
                    char_feed, word_lengths_feed = cnn_bilstm_load_data.pad_sequences(char_ids, config.MAX_LEN, pad_tok=0,nlevels=2)
                    feed_dict[self.input_char_ph] = char_feed
                    feed_dict[self.word_lengths] = word_lengths_feed
          
                _, loss_value = self.sess.run(
                    [self.train_op, self.loss], feed_dict=feed_dict)
                total_loss += loss_value

            total_loss /= float(nb_train)

            #  计算在训练集、开发集、测试集上的性能
            p_train, r_train, f_train = self.evaluate(sentences_train,chars_train, tags_train, labels_train,batch_size=batch_size)
            p_dev, r_dev, f_dev = self.evaluate(sentences_dev, chars_dev ,tags_dev, labels_dev,batch_size=batch_size)
            p_test, r_test, f_test = self.evaluate(sentences_test, chars_test ,tags_test, labels_test,batch_size=batch_size)
            #print('\tp_test=%f, r_test=%f, f_test=%f' % (p_test, r_test, f_test))
            #pre_labels = self.predict(sentences_test, tags_test)
            #with codecs.open('./Data/result/epoch_%d.csv' % (step+1), 'w', encoding='utf-8') as file_w:
                #for num, label in enumerate(pre_labels):
                    #file_w.write('%d,%s\n' % (num+1, self._label_voc_rev[label]))
            self.nb_epoch_scores.append([total_loss,p_train, p_dev, p_test])
            print('\tloss=%f, train f=%f, dev f=%f, test f=%f' % (total_loss, p_train, p_dev, p_test))
            if p_dev > best_score:
                nepoch_no_imprv = 0
                best_score = p_dev
                self.saver.save(self.sess, self._model_path)
                print('model has saved to %s' % self._model_path)
            else :
                nepoch_no_imprv += 1
                print(nepoch_no_imprv,"epoch not improve")
                if nepoch_no_imprv >= config.PATIENT:
                    return self.nb_epoch_scores
                    #break
        return self.nb_epoch_scores

    def fit_all(self, sentences_train, chars_train, tags_train, labels_train,
            batch_size=64, nb_epoch=40, keep_prob=1.0, word_keep_prob=1.0,
            tag_keep_prob=1.0, seed=137):
        """
        fit model
        Args:
            sentences_train, tags_train, labels_train: 训练数据
            sentences_dev, tags_dev, labels_dev: 开发数据
            batch_size: int, batch size
            nb_epoch: int, 迭代次数
            keep_prob: float between [0, 1], 全连接层前的dropout
            word_keep_prob: float between [0, 1], 词向量层dropout
            tag_keep_prob: float between [0, 1], 标记向量层dropout
        """
        self.saver = tf.train.Saver()
        self.nb_epoch_scores = []  # 存放nb_epoch次迭代的f值
        n_total = len(labels_train)
        nb_train = 0
        if int( n_total / batch_size) == (n_total *1.0 / batch_size):
            nb_train = int(n_total/ batch_size)
        else :
            nb_train = int(n_total / batch_size) + 1

        for step in range(nb_epoch):
            print('Epoch %d / %d:' % (step+1, nb_epoch))
            # train
            total_loss = 0.
            for i in tqdm( range(nb_train) ):
                # for i in range(nb_train):
                #start =  i * batch_size % n_total
                if (i+1)*batch_size >= n_total:
                    sentences_feed = sentences_train[i * batch_size:] + sentences_train[0:(i+1) * batch_size-n_total]
                    tags_feed = tags_train[i * batch_size:] + tags_train[0:(i+1) * batch_size-n_total]
                    labels_feed = labels_train[i * batch_size:] + labels_train[0:(i+1) * batch_size-n_total]
                    char_ids = chars_train[i * batch_size:] + chars_train[0:(i+1) * batch_size-n_total]
                else :
                    sentences_feed = sentences_train[i*batch_size:(i+1)*batch_size]
                    tags_feed = tags_train[i*batch_size:(i+1)*batch_size]
                    labels_feed = labels_train[i*batch_size:(i+1)*batch_size]
                    char_ids = chars_train[i*batch_size:(i+1)*batch_size]
                
                feed_dict = {
                        self.input_sentence_ph: sentences_feed,
                        self.input_tag_ph: tags_feed,
                        self.label_ph: labels_feed,
                        self.keep_prob_ph: keep_prob,
                        self.word_keep_prob_ph: word_keep_prob,
                        self.tag_keep_prob_ph: tag_keep_prob,
                    }
                if config.use_chars:
                    #char_ids = chars_train[i*batch_size:(i+1)*batch_size]
                    char_feed, word_lengths_feed = cnn_bilstm_load_data.pad_sequences(char_ids, config.MAX_LEN, pad_tok=0,nlevels=2)
                    feed_dict[self.input_char_ph] = char_feed
                    feed_dict[self.word_lengths] = word_lengths_feed
          
                _, loss_value = self.sess.run(
                    [self.train_op, self.loss], feed_dict=feed_dict)
                total_loss += loss_value

            total_loss /= float(nb_train)

            #  计算在训练集、开发集、测试集上的性能
            p_train, r_train, f_train = self.evaluate(sentences_train,chars_train, tags_train, labels_train,batch_size=batch_size)
            #pre_labels = self.predict(sentences_test, tags_test)
            #with codecs.open('./Data/result/epoch_%d.csv' % (step+1), 'w', encoding='utf-8') as file_w:
                #for num, label in enumerate(pre_labels):
                    #file_w.write('%d,%s\n' % (num+1, self._label_voc_rev[label]))
            print('\tloss=%f, p_train=%f, r_train=%f, f_train=%f' % (total_loss,p_train, r_train, f_train))
            self.nb_epoch_scores.append([total_loss,p_train, f_train])
        self.saver.save(self.sess, config.TRAIN_ALL_MODEL)
        print('model has saved to %s' % config.TRAIN_ALL_MODEL)
        return self.nb_epoch_scores

    def predict(self, data_sentences, data_chars, data_tags, batch_size=50):
        """
        Args:
            data_sentences, data_tags: np.array
            batch_size: int
        Return:
            pre_labels: list
        """
        pre_labels = []
        pre_proba = []
        nb_test = 0
        
        if int(len(data_sentences)/batch_size) == (len(data_sentences)*1.0/batch_size):
            nb_test = int(len(data_sentences)/batch_size)
        else:
            nb_test = int(len(data_sentences)/batch_size) + 1
        
        
        for i in tqdm(range(nb_test)):
            
            sentences_feed = data_sentences[i*batch_size:(i+1)*batch_size]
            tags_feed = data_tags[i*batch_size:(i+1)*batch_size]
            feed_dict = {
                self.input_sentence_ph: sentences_feed,
                self.input_tag_ph: tags_feed,
                self.keep_prob_ph: 1.0,
                self.word_keep_prob_ph: 1.0,
                self.tag_keep_prob_ph: 1.0}
            if config.use_chars:
                char_ids = data_chars[i*batch_size:(i+1)*batch_size]
                char_feed, word_lengths_feed = cnn_bilstm_load_data.pad_sequences(char_ids,config.MAX_LEN, pad_tok=0,nlevels=2)
                feed_dict[self.input_char_ph] = char_feed
                feed_dict[self.word_lengths] = word_lengths_feed
            #pre_temp,pre_out = self.sess.run([self.pre_op, self.pre_ouput_op],feed_dict=feed_dict)
            pre_proba_tmp,pre_temp= self.sess.run([self.proba_op, self.pre_op],feed_dict=feed_dict)
            pre_labels += list(pre_temp)
            pre_proba += list(pre_proba_tmp)
        return pre_labels ,pre_proba

    def evaluate(self, data_sentences, data_chars, data_tags, data_labels,
                 ignore_label=None, batch_size=64, simple_compute=True):
        """
        Args:
            data_sentences, data_tags, data_labels: np.array
            ignore_label: int, 负例的编号，或者None
            simple_compute: bool, 是否画出性能详细指标表格
        Return:
            p, r, f1
        """
        pre_labels = []
        if int(len(data_labels)/batch_size) == (len(data_labels)*1.0/batch_size):
            nb_dev = int(len(data_labels)/batch_size)
        else:
            nb_dev = int(len(data_labels)/batch_size) + 1
        for i in tqdm(range(nb_dev)):
            sentences_feed = data_sentences[i*batch_size:(i+1)*batch_size]
            tags_feed = data_tags[i*batch_size:(i+1)*batch_size]
            labels_feed = data_labels[i*batch_size:(i+1)*batch_size]
            feed_dict = {
                self.input_sentence_ph: sentences_feed,
                self.input_tag_ph: tags_feed,
                self.label_ph: labels_feed,
                self.keep_prob_ph: 1.0,
                self.word_keep_prob_ph: 1.0,
                self.tag_keep_prob_ph: 1.0}
            
            if config.use_chars:
                char_ids = data_chars[i*batch_size:(i+1)*batch_size]
                char_feed, word_lengths_feed = cnn_bilstm_load_data.pad_sequences(char_ids, config.MAX_LEN ,pad_tok=0,nlevels=2)
                feed_dict[self.input_char_ph] = char_feed
                feed_dict[self.word_lengths] = word_lengths_feed
            pre_temp = self.sess.run(self.pre_op, feed_dict=feed_dict)
            pre_labels += list(pre_temp)
        right_labels = data_labels[:len(pre_labels)]
        pre, rec, f = sim_compute(pre_labels, right_labels, ignore_label=ignore_label)
        return pre, rec, f

    def clear_model(self):
        tf.reset_default_graph()  #
        self.sess.close()

