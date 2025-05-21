# mlw_py

多國語系統管理網站 (Multilang Manage Website)

## 專案簡介

`mlw_py` 是一個用於管理多國語言翻譯的網站，提供了多種功能，包括語言管理、字串校對、檢查字串格式、上傳與下載翻譯文件等。此專案基於 Flask 框架開發，並整合了前端與後端功能。

---

## 專案結構

```
.
├── db/
│   ├── 01-init.sql          # 資料庫初始化 SQL 腳本
│   ├── 02-mlw.sql           # 多國語系統相關 SQL 腳本
├── website/
│   ├── nginx/
│   │   ├── Dockerfile       # Nginx Dockerfile
│   │   └── conf.d/
│   │       └── default.conf # Nginx 配置檔案
│   └── project/
│       └── mlw_py/
│           ├── Dockerfile-alpine # Dockerfile for Alpine
│           ├── mlw/
│           │   ├── main.py       # 主程式入口
│           │   ├── requirements.txt # Python 套件需求
│           │   ├── server.py     # 啟動伺服器
│           │   ├── config/       # 配置檔案
│           │   ├── log/          # 日誌檔案
│           │   ├── model/        # 資料模型
│           │   ├── rep/          # 報表相關
│           │   ├── routes/       # 路由
│           │   ├── services/     # 業務邏輯
│           │   ├── static/       # 靜態資源 (CSS, JS, 圖片等)
│           │   ├── templates/    # HTML 模板
│           │   └── utility/      # 工具函數
```

---

## 功能介紹

### 1. 語言管理
- 新增、修改、刪除語言。
- 支援多語言選擇與切換。

### 2. 字串校對
- 提供專案字串校對功能。
- 支援字串版本差異檢視與編輯紀錄。

### 3. 檢查字串格式
- 自動檢查字串格式是否符合規範。
- 顯示錯誤字串並提供修正建議。

### 4. 上傳與下載
- 支援 Excel 文件上傳與下載。
- 提供 SVN 字串檔案的產出與管理。

---

## 環境需求

- Docker
- Docker Compose

---

## 安裝與執行

### 使用 Docker

1. 複製專案
```bash
git clone https://github.com/ns3pw6/mlw_py.git
cd mlw_py
```

2. 啟動服務
```bash
docker-compose up --build
```

3. 停止服務
```bash
docker-compose down
```

---

## 注意事項

1. 確保 Docker 服務正在運行
2. 預設port請參考docker-compose.yml，如需修改請自行編輯
3. 首次啟動時會自動初始化資料庫(可能需要一點時間)
4. 網頁入口為: {host_ip}:{port}/mlw

---