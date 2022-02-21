import os
import sys
import json
import requests
import pandas as pd
from datetime import datetime

date_format_str = '%Y/%m/%d %H:%M:%S.%f %Z'

PHStartDateStr = '2022/2/2 23:59:59.999999 UTC'
PHEndDateStr = '2022/2/20 23:59:59.999999 UTC'
PHStartDate = datetime.strptime(PHStartDateStr, date_format_str)
PHEndDate =   datetime.strptime(PHEndDateStr, date_format_str)

GHStartDateStr = '2022/2/10 23:59:59.999999 UTC'
GHEndDateStr = '2022/2/20 23:59:59.999999 UTC'
GHStartDate = datetime.strptime(GHStartDateStr, date_format_str)
GHEndDate =   datetime.strptime(GHEndDateStr, date_format_str)


FTM_APIKEY='ZHTTXJFBWI2TZBDIBTTZBK91V1VCYKMNN1'

URL='https://api.ftmscan.com/api?module=account&action=txlist&address={Address}&sort=asc&apikey={ApiKey}'





def main():
    print('> Program start')

    print('> Load address')
    addressList = pd.read_excel('address.xlsx')

    print('> Check...')


    for index, row in addressList.iterrows():
        print(row['Name'], row['HolderAddress'])
        address = row['HolderAddress'].lower()

        txList = GetTxList(address)

        # 解析Unstack
        UnstackTxList = ParseUnstack(txList, address)
        
        # 計算鉑金手與黃金手期間Unstack總數
        UnstackTxCountForPH=0
        UnstackTxCountForGH=0
        for UnstackTx in UnstackTxList:
            if UnstackTx['time']>PHStartDate and UnstackTx['time']<PHEndDate:
                UnstackTxCountForPH = UnstackTxCountForPH+1
            if UnstackTx['time']>GHStartDate and UnstackTx['time']<GHEndDate:
                UnstackTxCountForGH = UnstackTxCountForGH+1
        # print(UnstackTxCountForPH, UnstackTxCountForGH)
        addressList.loc[index,'UnstackTxCountForPH'] = UnstackTxCountForPH
        addressList.loc[index,'UnstackTxCountForGH'] = UnstackTxCountForGH
        addressList.loc[index,'UnstackTxList'] = json.dumps(UnstackTxList, default=str)

        # 解析TransferOut
        TransferOutTxList = ParseTransferOut(txList, address)

        # 計算鉑金手與黃金手期間TransferOut總數
        TransferOutCountForPH=0
        TransferOutCountForGH=0
        for TransferOutTx in TransferOutTxList:
            if TransferOutTx['time']>PHStartDate and TransferOutTx['time']<PHEndDate:
                TransferOutCountForPH = TransferOutCountForPH+1
            if TransferOutTx['time']>GHStartDate and TransferOutTx['time']<GHEndDate:
                TransferOutCountForGH = TransferOutCountForGH+1
        # print(TransferOutCountForPH, TransferOutCountForGH)
        addressList.loc[index,'TransferOutCountForPH'] = TransferOutCountForPH
        addressList.loc[index,'TransferOutCountForGH'] = TransferOutCountForGH
        addressList.loc[index,'TransferOutTxList'] = json.dumps(TransferOutTxList, default=str)

        addressList.loc[index,'MissCountForPH'] = TransferOutCountForPH+UnstackTxCountForPH
        addressList.loc[index,'MissCountForGH'] = TransferOutCountForGH+UnstackTxCountForGH


    print(addressList)
    addressList.to_excel('output.xlsx')



## ----

def GetTxList(Address):
    response = json.loads(requests.get(URL.format(Address=Address, ApiKey=FTM_APIKEY)).text)
    # print(response)
    if response['status']=='1':
        return response['result']
    else:
        return None

def ParseUnstack(TxList, FromAddress):
    UnstackTxList = []

    ## 解析 Unstack
    MethodId = '0x9ebea88c'
    ContractAddress = '0x319995e79c662479d42c054fdab0415a6404190d'
    
    for tx in TxList:
        if 'input' in tx and tx['input'].lower().startswith(MethodId):
            if ('from' in tx and tx['from'].lower()==FromAddress) and ('to' in tx and tx['to'].lower()==ContractAddress):
                time = datetime.utcfromtimestamp(int(tx['timeStamp']))
                # print(time)
                # print(tx['input'].lower()[10:-64])
                value = int(tx['input'].lower()[10:-64], 16)/1000000000
                # print(value)

                UnstackTx = {}
                UnstackTx['method'] = 'Unstack'
                UnstackTx['time'] = time
                UnstackTx['value'] = value
                UnstackTx['hash'] = tx['hash']

                UnstackTxList.append(UnstackTx)

        else:
            None

    return UnstackTxList


def ParseTransferOut(TxList, FromAddress):
    TransferOutTxList = []

    ## 解析TransferOut
    MethodId = '0xa9059cbb'
    ContractAddress = '0xc59a271f7625f2195c1c38f8720da00a52a72b10'
    
    for tx in TxList:
        if 'input' in tx and tx['input'].lower().startswith(MethodId):
            if ('from' in tx and tx['from'].lower()==FromAddress) and ('to' in tx and tx['to'].lower()==ContractAddress):
                time = datetime.utcfromtimestamp(int(tx['timeStamp']))
                # print(time)
                # print(tx['input'].lower()[-63:])
                value = int(tx['input'].lower()[-63:], 16)/1000000000
                # print(value)

                TransferOutTx = {}
                TransferOutTx['method'] = 'TransferOut'
                TransferOutTx['time'] = time
                TransferOutTx['value'] = value
                TransferOutTx['hash'] = tx['hash']

                TransferOutTxList.append(TransferOutTx)

        else:
            None

    return TransferOutTxList






## ----




if __name__ == "__main__":
    main()