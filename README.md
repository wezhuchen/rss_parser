# rss_parser
練習爬取新聞網站提供的rss內容並且對資料處理至所需格式。

## 資料夾架構 

```
.
├── jobs.py                                             # 主節點
├── conf                                                # 設定檔                                                
|    ├──  default.json                                    # 基本設定檔
|    └── settings.json                                    # 網站rss config
├── core                                                # 模組
|    └── parser.py                                        # rss 解析器
├── utils                                               # 共用模組  
|    ├──  jsonloader.py 
|    ├──  logger.py 
|    └──   urlrequest.py 
├── requirements.txt
└── README.md 
```

## 初始設定  
首先將相關套件進行安裝。

執行: 

```bash
pip3 install -r requirements.txt
```
