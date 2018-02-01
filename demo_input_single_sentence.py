#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# demo_input_single_sentence.py
# @Author :  ()
# @Link   : 
# @Date   : 2018-1-30 23:09:34



import jieba
import jieba.analyse
import udic_lab_CAS as cas
import time
import codecs
import os
import logging
import json


def get_resource_path():
    return os.path.join(os.path.dirname(__file__), 'resources')

def get_resource_setting(proc_setting):
    outListPath = get_resource_path()
#    print('proc_setting: %s , outListPath: %s' % (proc_setting,outListPath))
    outListFile = os.path.join(outListPath, proc_setting)
    
    if not os.path.isfile(outListFile):
       logging.error('file {} does not exist.'.format(outListFile))
       return
    
    out_dict = {}
    with codecs.open(outListFile,'r','utf-8') as ofile:
        out_dict = json.load(ofile)
        
    return out_dict


def LoadJiebaDict(dictPath,stopWordsPath,userDictPath):
    
    ## load cht dictionary
    jieba.set_dictionary(dictPath)
    ## load user dictionary
    jieba.load_userdict(userDictPath)
    ## load user stop words
    jieba.analyse.set_stop_words(stopWordsPath)


    
    
def elapsed(start):
    return time.time() - start

#  begin process. 
try:

    setting_list = get_resource_setting("global_config.json")
    ## jieba cht dictionary path
    dictPath = setting_list["jieba_dict_path"]
    ## jieba stop words path
    stopWordsPath = setting_list["stop_words_path"]
    ## jieba user dictionary path 
    userDictPath = setting_list["jieba_user_dict_path"]
    # kcm dictionary path 
    KCM_fPath = setting_list["kcm_dict_path"]
    # KCM_fPath = '/Users/hua/udic_lab/nlp_data/kcm/test.model'
    
    termDict = {}
    print('begin load kcm dictionary:')
    start = time.time()
    termDict = cas.LoadKCM_Dict(KCM_fPath)
    print('LoadKCM_Dict load: ' + str(elapsed(start)))

    # 20170629 hua: 只載入一次詞典，後面改用 add_word, del_word 調整詞頻，加速 KCM 斷詞效率
    print('Load Jieba Dict.')
    LoadJiebaDict(dictPath,stopWordsPath,userDictPath)
    
   

    while True:
        try:
            inString = input("Please enter your string: ")

        except ValueError:
            print("Sorry, I didn't understand that.")
            continue
        except SyntaxError:
            inString = None

        if inString == 'exit':
            print("you are exit!!")
            break
        elif inString is None or inString == '':
            print("Sorry, Please input string.")
        else:
            
            print('default jieba:')
            start = time.time()
            print('jieba: %s' % '|'.join(jieba.cut(inString,cut_all=False,HMM=True)))
            print('jieba cut elapsed: ' + str(elapsed(start)))
            
            start = time.time()
            
            result = cas.input_single_sentence(inString,termDict)

            print('CAS: %s' % '|'.join(result))

            print('CAS cut elapsed: ' + str(elapsed(start)))
            continue
except IndexError as idxerr:
    print('bad index:'+ idxerr) 
except Exception as other:
    print('something error:' +  other)


