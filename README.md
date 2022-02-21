## FTMScan檢查
- 檢查錢包是否符合黃金手/白金手資格


## 使用方式
- 安裝python
- 安裝 pandas, requests ...必要套件
- 編輯 address.xlsx
- 執行 python3 main.py。會輸出output.xlsx
    - 欄位MissCountForPH>0。代表在鉑金手期間，有Unstack或TransferOut的狀況。失去鉑金手資格
    - 欄位MissCountForGH>0。代表在黃金手期間，有Unstack或TransferOut的狀況。失去黃金手資格
    - 欄位UnstackTxList，Unstack細部資訊。欄位TransferOutTxList，TransferOut細部資訊
