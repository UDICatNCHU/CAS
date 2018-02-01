#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun 30 11:39:52 2017

@author: hua

desc: UDIC_LAB KCM segmentation.
"""

from collections import OrderedDict
import codecs
import itertools
import jieba
import os
import json
import logging


'''
比對輸入字串的文字是否包含 kcm 中出現的詞
''' 
def MatchTerm(inString,kcm_dict):
    co_list = []
    d = OrderedDict()
    matchTwoWordList = []
#    matchOneWordList = []
    for key,valueList in kcm_dict.items():
        #尋找到短句中是否有符合 key 的單詞
        if inString.find(key) >-1:
                for i in valueList:
                    # 共現的兩個單詞不可相同
                    if key != i[0]:
#                        if key not in matchOneWordList:
#                            matchOneWordList.append(key)
                        #尋找短句中是否有第二個詞
                        if inString.find(i[0]) > -1:
                            # 排除已存在順序相反的共現組合
                            if list((i[0],key,i[1])) in co_list:
                                    break;
                            else:
                                # 重複出現的共現詞只保留共現次數最多的一筆
                                d.setdefault((key,i[0]),[]).append(int(i[1]))
                                co_list.append([key,i[0],i[1]])
                                for i,j in d.items():
                                    d[i] = sorted(set(j),key=lambda x : x,reverse=True)[:1]
    for k,v in d.items():
        k += tuple(v)
        matchTwoWordList.append(k)

    matchTwoWordList = sorted(set(matchTwoWordList),key=lambda x : x[2],reverse=True)[:100]
    
    return matchTwoWordList
#    return matchTwoWordList ,matchOneWordList



#==============================================================================
# 載入 KCM 詞典
#==============================================================================
def LoadKCM_Dict(fpath):
    termDict = {}
    with codecs.open(fpath,'r', encoding='utf-8') as data:
        for line in data:
            lineList = line.split()
            if lineList[0] in termDict:
                oldList = []
                oldList = termDict[lineList[0]]
                oldList.append(tuple((lineList[1],lineList[2])))
            else:
                oldList = []
                oldList.append(tuple((lineList[1],lineList[2])))
                termDict[lineList[0]] = oldList
            if lineList[1] in termDict:
                oldList = []
                oldList = termDict[lineList[1]]
                oldList.append(tuple((lineList[0],lineList[2])))
            else:
                oldList = []
                oldList.append(tuple((lineList[0],lineList[2])))
                termDict[lineList[1]] = oldList
    return termDict



'''
篩選互斥單詞
e.g. mutexDict: {'產生': ['產生'], '事件': ['事件'], '人魚': ['人魚', '魚肉']}
'''
def ChkTermMutex(inString,matchList):
    # 依單詞長度排序
    matchList.sort(key=lambda x : len(x),reverse=True)
    # 列出所有單詞組合
    plist = [ (matchList[i],matchList[j]) for i in range(len(matchList)-1) for j in range(i+1, len(matchList))]

    mutexDict = {}

    for w1,w2 in plist:
        # 檢查詞組是否互斥
        # 如果將 w1 從句子移除, 就找不到 w2, 代表 w2 和 w1 互斥
        fString = inString.replace(w1,'')
        tmplist = []
        if fString.find(w2) == -1:
            w1_key = keys_of_value(mutexDict,w1)
            if w1_key is None or len(w1_key) == 0:
                tmplist.append(w1)
                tmplist.append(w2)
                mutexDict[w1] = list(set(tmplist))
            else:
                w2_key = keys_of_value(mutexDict,w2)
                if w2_key is None or len(w2_key) == 0:
                    tmplist = mutexDict[w1_key]
                    tmplist.append(w2)
                    mutexDict[w1] = list(set(tmplist))
    return mutexDict



'''
input:
    dict: 輸入 dict 物件
    value: 要查找的值
desc: 
    在字典中找該值是否存在，如果存在就回傳所屬的 key
'''
def keylist_of_value(dict, value):
    k_list = []
    for k in dict:
        if isinstance(dict[k], list):
            if value in dict[k]:
                k_list.append(k)
                
        else:
            if value == dict[k]:
                k_list.append(k)

    return k_list

def keys_of_value(dict, value):
    for k in dict:
        if isinstance(dict[k], list):
            if value in dict[k]:
                return k
        else:
            if value == dict[k]:
                return k

'''
篩選互斥單詞，選擇權重最高的組合
l: ('產生', '事件', '人魚')
l: ('產生', '事件', '魚肉')
fliterMaxTermWeight: {('產生', '事件', '人魚'): 517}
'''
def GetTermListWeight(inString,matchTwoList,mutexDict):
    tlist = []
    interTermList = []

    # 20170522 hua: 去除共現單詞中的互斥詞, 保留共通的部分，用 matchOneList 會有問題
    for i in matchTwoList:
        # print(i)
        interTermList.append(i[0])
        interTermList.append(i[1])

    for k,vl in mutexDict.items():
        interTermList = list(set(interTermList).difference(set(vl)))

    # print('interTermList: %s' % (interTermList))
    mutexList = []
    for k,vl in mutexDict.items():
        mutexList.append(vl)

    # print('mutexList: %s' % (mutexList))
    # 列出互斥的所有組合
    termWeight = {}
    for l in list(itertools.product(*mutexList)):
        l = l + tuple(interTermList)
        tlist.append(l)

        ## rory test
        # print('l: %s' % (str(l)))
        termWeight[l] = SetCoTerm(l,matchTwoList)

    maxTermWeight={}
    for k,v in termWeight.items():
        if v is not None or len(v) > 0:
            gweight=0
            for w in v:
                gweight += w[2]
            maxTermWeight[k]=gweight
    fliterMaxTermWeight={}
    # 同組合權重不同，只取最高權重
    for i in sorted(maxTermWeight,key=maxTermWeight.__getitem__,reverse=True)[:1]:
        fliterMaxTermWeight[i] =  maxTermWeight[i]

    return fliterMaxTermWeight

'''
input: 
    inTerm: 輸入詞
    inWeight: 共現詞和次數
desc: 取得詞是否有共現
'''
def SetCoTerm(inTerm,inWeight):
    termWeightList = []
    for x,y,z in inWeight:
        if x in inTerm and y in inTerm:
            termWeightList.append((x,y,z))
    return termWeightList     



'''
input: 
    sentence: 輸入短句
    word: 短句中的 kcm 共現詞
output:
    回傳找到詞組合中最大的詞頻 + 1
desc: 
    找出 DAG 中包含共現詞單字的詞組合，例： 
    輸入短句：水淹金山寺 
    共現詞：金山寺
    ，會找到 金、金山、金山寺、水淹金山、山寺、寺。其中取出詞頻最高的詞加 1，為回傳值。
'''
def SetUserDictWeight(sentence,word):
    max_word_weight = 0
    word_weight_dict = {}
    key = 0
    N = len(sentence)
    DAG = jieba.get_DAG(sentence)
    # print('sentence: %s, word: %s' % (sentence,word))
    bidx = sentence.index(word)
    eidx = bidx + len(word) 
    for i in range(bidx,eidx,1):
        key_list = keylist_of_value(DAG,i)
        if key_list is None or len(key_list) == 0:
            w_list = []
            key = bidx
            w_list = DAG[key]
            for j in w_list:
                if sentence[key:j+1] not in word_weight_dict:
                    # 20170617 hua: 修正自訂詞典可能會沒有字，None會造成排序 error，將詞頻補為 0 
                    w_freq = jieba.get_FREQ(sentence[key:j+1])
                    if w_freq is None:
                        w_freq = 0
                    word_weight_dict[sentence[key:j+1]] = w_freq
        else:
            for key in key_list:
                w_list = []
                w_list = DAG[key]
                for j in w_list:
                    if sentence[key:j+1] not in word_weight_dict:
                        # 20170617 hua: 修正自訂詞典可能會沒有字，None會造成排序 error，將詞頻補為 0 
                        w_freq = jieba.get_FREQ(sentence[key:j+1])
                        if w_freq is None:
                            w_freq = 0
                        word_weight_dict[sentence[key:j+1]] = w_freq

        
    topKey = sorted(word_weight_dict,key=word_weight_dict.__getitem__,reverse=True)[:1]
    
    max_word_weight = word_weight_dict[topKey[0]] + 1
    # print('dict: %s' % (word_weight_dict))

    return max_word_weight 




def input_single_sentence(input_string,kcm_dict):

    matchTwoList = []
    matchTwoList = MatchTerm(input_string,kcm_dict)

    # 20170522 hua: 如果共現詞有互斥，只選擇其中一個
    matchList=[]
    for i in matchTwoList:
        # print(i)
        matchList.append(i[0])
        matchList.append(i[1])

    mutexDict = ChkTermMutex(input_string,matchList)

    fliterMaxTermWeight = GetTermListWeight(input_string,matchTwoList,mutexDict)


    # set weight
    # 設定 jieba 自訂詞庫詞頻
    ori_freq_dict = {}
    new_freq_dict = {}
    for tuple_k in fliterMaxTermWeight.keys():
        freq_w = 0
        # 如果共現為 0 就不更新 jieba 自訂義字典檔
        if fliterMaxTermWeight[tuple_k] > 0:
            # 20170629 hua: 改用 jieba add_word , del_word 調整詞頻，避免重覆重新載入詞典
            for k_word in tuple_k:
                ## set k1 freq
                freq_w = jieba.get_FREQ(k_word)
                if freq_w is None or freq_w == 0:
                    # 取得共現單詞要設定的詞頻值
                    freq_w = SetUserDictWeight(input_string,k_word)
                    new_freq_dict[k_word]=freq_w
                else:
                    ori_freq_dict[k_word]=freq_w
                    freq_w = SetUserDictWeight(input_string,k_word)
                    new_freq_dict[k_word] = freq_w


    for k,v in new_freq_dict.items():
        jieba.add_word(k,v)


    result = jieba.cut(input_string,cut_all=False,HMM=True)
    print('test CAS: %s' % '|'.join(result))


    ## 20170629 hua: 還原成原本的 jieba 字典
    set_ori_freq = set(ori_freq_dict)
    set_new_freq = set(new_freq_dict)
    set_diff = set_new_freq - set_ori_freq
    for new_w in set_diff:
        jieba.del_word(new_w)

    for w,f in ori_freq_dict.items():
        jieba.add_word(w,f)

    # setting_list = get_resource_setting("global_config.json")
    # ## jieba cht dictionary path
    # dictPath = setting_list["jieba_dict_path"]
    # ## jieba stop words path
    # stopWordsPath = setting_list["stop_words_path"]
    # ## jieba user dictionary path 
    # userDictPath = setting_list["jieba_user_dict_path"]

    # LoadJiebaDict(dictPath,stopWordsPath,userDictPath)


    return result
