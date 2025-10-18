# 🔴 NYCU 選課平台 - 問題分析與修復方案

**分析時間**: 2025-10-17
**狀態**: 需要修復

---

## 📊 當前狀況分析

### ✅ 已正確實現

1. **NYCU 課程基本資料**
   - ✅ 已載入 33,554 門 NYCU 真實課程
   - ✅ 課程名稱、教師、學系等基本資訊完整
   - ✅ 學年度、學期資料正確
   - ✅ API 正常運作

2. **前端功能**
   - ✅ 所有頁面正常顯示
   - ✅ 課程瀏覽、搜尋、篩選功能正常
   - ✅ 課表管理功能正常
   - ✅ 繁體中文介面完整

3. **Backend API**
   - ✅ FastAPI 服務正常運行 (localhost:8000)
   - ✅ 所有端點回應正常 (2-23ms)
   - ✅ 資料庫查詢正常

---

## ❌ 發現的問題

### 問題 1: 課程大綱內容未正確整合 🔴 **高優先級**

**現象**:
```json
{
  "syllabus": "Content available",
  "syllabus_zh": "Content available"
}
```

**問題分析**:
- 課程大綱欄位只顯示 "Content available" 佔位符
- 實際大綱內容（from `/scraper/data/course_outlines/outlines_all.json`）未導入

**影響**:
- 使用者無法查看課程詳細大綱
- 課程詳情頁面功能不完整
- 缺少重要的課程資訊

**資料位置**:
- 課程資料: `/home/thc1006/dev/nycu_course_platform/data/real_courses_nycu/courses_all_semesters.json` (34MB) ✅ 已導入
- 課程大綱: `/home/thc1006/dev/nycu_course_platform/scraper/data/course_outlines/outlines_all.json` (5.9MB) ❌ 未導入

**修復腳本**:
- ✅ 存在: `/home/thc1006/dev/nycu_course_platform/backend/import_syllabi.py`
- ⚠️ 狀態: 未執行或執行失敗

---

### 問題 2: 外部無法訪問服務 🔴 **高優先級**

**現象**:
- 服務只能從 localhost 訪問
- 外部網路無法連接到平台

**問題分析**:
1. **nginx 配置問題**:
   - nginx.conf 配置為 Docker 容器模式
   - upstream 指向: `frontend:3000` 和 `backend:8000` (Docker 服務名)
   - 但實際服務運行在: `localhost:3000` 和 `localhost:8000`

2. **服務運行模式不匹配**:
   - 現況: 本地開發模式（npm run dev, uvicorn）
   - 需求: 生產部署模式（Docker Compose）

3. **Docker 容器未運行**:
   ```bash
   $ docker ps -a | grep nycu
   # 無輸出 - 沒有容器在運行
   ```

**影響**:
- 外部使用者無法訪問平台
- nginx 反向代理無法連接到服務
- HTTPS 域名 nymu.com.tw 無法使用

**可用資源**:
- ✅ docker-compose.yml 已配置
- ✅ Dockerfile.backend 已建立
- ✅ Dockerfile.frontend 已建立
- ✅ nginx.conf 已配置（針對 Docker）
- ✅ SSL 憑證已設置（nymu.com.tw）

---

## 🔧 修復方案

### 方案 A: 完整 Docker 部署（推薦用於生產環境）

**優點**:
- ✅ 支援外部訪問
- ✅ 使用 nginx 反向代理
- ✅ 支援 HTTPS (nymu.com.tw)
- ✅ 服務隔離與容器化
- ✅ 易於擴展和管理

**步驟**:

1. **停止本地開發服務**:
   ```bash
   # 停止 frontend
   pkill -f "next-server"

   # 停止 backend
   pkill -f "uvicorn"
   ```

2. **確保資料庫檔案存在**:
   ```bash
   ls -lh /home/thc1006/dev/nycu_course_platform/backend/courses.db
   # 應該看到資料庫檔案
   ```

3. **導入課程大綱（修復問題 1）**:
   ```bash
   cd /home/thc1006/dev/nycu_course_platform
   source backend/venv/bin/activate
   python backend/import_syllabi.py
   ```

4. **建立 Docker 映像**:
   ```bash
   cd /home/thc1006/dev/nycu_course_platform
   docker-compose build
   ```

5. **啟動 Docker 服務**:
   ```bash
   docker-compose up -d
   ```

6. **驗證服務狀態**:
   ```bash
   docker-compose ps
   docker-compose logs -f
   ```

7. **測試訪問**:
   - 本地: http://localhost
   - HTTPS: https://nymu.com.tw

**預期結果**:
- ✅ 外部可訪問
- ✅ 課程大綱顯示完整
- ✅ HTTPS 正常運作

---

### 方案 B: 修改 nginx 配置（臨時方案，僅用於測試）

**適用場景**: 想要保持本地開發模式但需要測試外部訪問

**步驟**:

1. **修改 nginx.conf 的 upstream 配置**:
   ```nginx
   # 修改前:
   upstream frontend {
       server frontend:3000;
   }

   upstream backend {
       server backend:8000;
       keepalive 32;
   }

   # 修改後:
   upstream frontend {
       server host.docker.internal:3000;
   }

   upstream backend {
       server host.docker.internal:8000;
       keepalive 32;
   }
   ```

2. **重啟 nginx**:
   ```bash
   docker restart nycu-nginx
   # 或
   sudo systemctl restart nginx
   ```

**缺點**:
- ⚠️ 僅適用於開發測試
- ⚠️ 需要本地服務持續運行
- ⚠️ 不適合生產環境

---

## 📋 完整修復檢查清單

### 階段 1: 資料完整性修復

- [ ] 1.1 驗證課程資料已載入
  ```bash
  curl "http://localhost:8000/api/courses/?limit=1"
  ```

- [ ] 1.2 檢查課程大綱資料檔案
  ```bash
  ls -lh /home/thc1006/dev/nycu_course_platform/scraper/data/course_outlines/outlines_all.json
  ```

- [ ] 1.3 執行大綱匯入腳本
  ```bash
  cd /home/thc1006/dev/nycu_course_platform
  source backend/venv/bin/activate
  python backend/import_syllabi.py
  ```

- [ ] 1.4 驗證大綱已匯入
  ```bash
  curl "http://localhost:8000/api/courses/1" | grep -v "Content available"
  # 應該看到實際的大綱內容，而非 "Content available"
  ```

### 階段 2: Docker 部署

- [ ] 2.1 停止本地開發服務
  ```bash
  pkill -f "next-server"
  pkill -f "uvicorn"
  ```

- [ ] 2.2 確認資料庫檔案位置
  ```bash
  ls -lh /home/thc1006/dev/nycu_course_platform/backend/courses.db
  ```

- [ ] 2.3 建立 Docker 映像
  ```bash
  cd /home/thc1006/dev/nycu_course_platform
  docker-compose build
  ```

- [ ] 2.4 啟動服務
  ```bash
  docker-compose up -d
  ```

- [ ] 2.5 檢查容器狀態
  ```bash
  docker-compose ps
  ```

- [ ] 2.6 檢查日誌
  ```bash
  docker-compose logs -f backend
  docker-compose logs -f frontend
  docker-compose logs -f nginx
  ```

### 階段 3: 功能驗證

- [ ] 3.1 測試本地訪問
  ```bash
  curl http://localhost/api/courses/?limit=1
  ```

- [ ] 3.2 測試課程詳情 API
  ```bash
  curl http://localhost/api/courses/1 | python3 -m json.tool
  ```

- [ ] 3.3 檢查大綱內容
  - 訪問: http://localhost/course/1
  - 確認大綱區塊顯示實際內容

- [ ] 3.4 測試外部訪問（如果有域名）
  ```bash
  curl https://nymu.com.tw
  ```

- [ ] 3.5 測試完整使用者流程
  - [ ] 首頁加載
  - [ ] 課程瀏覽
  - [ ] 課程搜尋
  - [ ] 課程詳情（含大綱）
  - [ ] 加入課表
  - [ ] 課表管理

---

## 🚨 重要注意事項

### 資料庫備份

**在執行任何操作前，務必備份資料庫**:

```bash
cp /home/thc1006/dev/nycu_course_platform/backend/courses.db \
   /home/thc1006/dev/nycu_course_platform/backend/courses.db.backup_$(date +%Y%m%d_%H%M%S)
```

### 環境變數檢查

確認 `.env` 檔案存在並正確配置:

```bash
cat /home/thc1006/dev/nycu_course_platform/backend/.env
```

### 憑證有效性

檢查 SSL 憑證是否有效:

```bash
sudo certbot certificates
```

---

## 📊 預期結果

### 修復後的狀態

**課程大綱**:
```json
{
  "syllabus": "【課程目標】This course aims to...",
  "syllabus_zh": "【課程目標】本課程旨在..."
}
```

**外部訪問**:
- ✅ https://nymu.com.tw 可訪問
- ✅ 所有 API 端點正常
- ✅ 課程大綱完整顯示

**服務架構**:
```
Internet
    ↓
[nginx:443] (HTTPS)
    ↓
[nginx:80] (HTTP redirect)
    ↓
┌─────────────┬─────────────┐
│  frontend   │   backend   │
│  (Next.js)  │  (FastAPI)  │
│   :3000     │    :8000    │
└─────────────┴─────────────┘
         ↓
    [SQLite DB]
  (33,554 courses
   with syllabi)
```

---

## 🎯 建議執行順序

### 推薦方案: 完整 Docker 部署

1. **備份資料庫** (5 分鐘)
2. **導入課程大綱** (10-15 分鐘)
3. **驗證大綱內容** (5 分鐘)
4. **停止本地服務** (1 分鐘)
5. **建立 Docker 映像** (5-10 分鐘)
6. **啟動 Docker 服務** (2 分鐘)
7. **驗證所有功能** (15 分鐘)

**總預計時間**: 約 45-60 分鐘

---

## 📞 需要的資訊

在開始修復前，請確認:

1. **域名設定**:
   - 域名 `nymu.com.tw` 是否指向此伺服器?
   - DNS A 記錄是否正確?

2. **SSL 憑證**:
   - 憑證路徑: `/etc/letsencrypt/live/nymu.com.tw/`
   - 是否有效且未過期?

3. **防火牆設定**:
   - Port 80 (HTTP) 是否開放?
   - Port 443 (HTTPS) 是否開放?

4. **使用者需求**:
   - 需要保留本地開發環境嗎?
   - 是否需要同時運行開發和生產環境?

---

**報告建立時間**: 2025-10-17 16:45 UTC
**優先級**: 🔴 高 - 需要立即處理
**影響範圍**: 功能完整性 + 外部訪問

**下一步**: 等待使用者確認後開始執行修復
