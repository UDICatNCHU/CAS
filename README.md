# CAS
考量上下文字詞共現關系的短文斷詞流程 (context aware segmentation:CAS)


## 環境說明： python 3 以上
## 請先安裝 jieba 套件
## 請準備共現詞詞典，詞典格式範例如下：
'''  ## 共現詞1 共現詞2 共現次數
美國總統選舉 代表 2
美國總統選舉 候選人 4
美國總統選舉 共和黨 5
臺灣 女子 3
臺灣 學校 9
....
'''

## 載入 cas 函式
import udic_lab_CAS as cas

## 載入共現詞詞典
## 輸入參數說明：LoadKCM_Dict(共現詞詞典完整路徑)
termDict = cas.LoadKCM_Dict(KCM_fPath)

## 執行斷詞
## 輸入參數說明：input_single_sentence(輸入短句,共現詞詞典)
result = cas.input_single_sentence(inString,termDict)
print('CAS: %s' % '|'.join(result))
