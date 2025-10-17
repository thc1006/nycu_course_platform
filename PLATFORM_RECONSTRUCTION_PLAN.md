# 🏗️ NYCU 課程平台完全重構計畫

**計畫日期:** 2025-10-17
**主要目標:**
1. ✅ 完整課程綱要資料爬蟲 (70,239 門課程 × 2 語言)
2. 🔄 前後端平台完全重構
3. 🔄 台灣繁體中文 (zh-TW) 設為主要語言

---

## 📋 第一階段：資料準備 (進行中)

### 1.1 課程綱要爬蟲 (course_outline_scraper.py)

**狀態:** 🔄 執行中 (預計 30-45 分鐘)

**目標:**
- 爬取所有 70,239 門課程的綱要資訊
- 抓取英文和繁體中文版本
- 來源: `https://timetable.nycu.edu.tw/?r=main/crsoutline&Acy={year}&Sem={sem}&CrsNo={course_no}&lang={lang}`

**參數:**
- 年份: 110-114 (5 年)
- 學期: 1-2 (9 個學期)
- 語言: zh-tw + en

**輸出:**
- 檔案: `/scraper/data/course_outlines/outlines_all.json`
- 大小: 預期 50-100 MB
- 包含: 每門課程的英文和繁體中文綱要

**監控:**
```bash
# 查看進度
tail -f /home/thc1006/dev/nycu_course_platform/scraper/data/course_outlines/outlines_all.json

# 查看日誌
tail -f /tmp/*.log | grep "outline\|course"
```

---

## 📋 第二階段：前端重構 (待開始)

### 2.1 i18n 配置改進

**目標:** 改 zh-TW 為 PRIMARY 語言

**文件修改:**
```typescript
// frontend/next-i18n-config.js
export const defaultLocale = 'zh-TW';  // 改為繁體中文
export const locales = ['zh-TW', 'en-US'];  // 主要語言優先
```

**步驟:**
1. 將 zh-TW 設定為預設語言
2. 更新所有路由以 zh-TW 為預設
3. 確保所有新用戶預設進入繁體中文版本

### 2.2 UI 元件本地化

**需要修改的元件:**

#### Header.tsx
- ✓ 語言切換器已實現
- ⏳ 調整語言選項順序 (zh-TW 優先)
- ⏳ 更新 UI 預設語言

#### CourseDetail.tsx  (lines 227-266)
- ✓ 綱要顯示已實現
- ⏳ 設定繁體中文綱要為預設顯示
- ⏳ 完善英文/繁體中文切換

#### HomePage.tsx
- ⏳ 主頁內容繁體中文化
- ⏳ 搜尋提示文本繁體中文
- ⏳ 特色功能介紹繁體中文

#### BrowsePage.tsx
- ⏳ 課程列表過濾器繁體中文
- ⏳ 搜尋欄提示繁體中文
- ⏳ 分類標籤繁體中文

#### SchedulePage.tsx
- ⏳ 課表介面繁體中文
- ⏳ 按鈕和操作文本繁體中文

### 2.3 翻譯檔案完善

**檔案:**
```
frontend/public/locales/
├── zh-TW/                    ← PRIMARY
│   ├── common.json          (✓ 已建立)
│   ├── course.json          (✓ 已建立)
│   ├── home.json            (✓ 已建立)
│   ├── schedule.json        (✓ 已建立)
│   ├── error.json           (✓ 已建立)
│   ├── browse.json          (⏳ 需新增)
│   ├── navigation.json      (⏳ 需新增)
│   └── validation.json      (⏳ 需新增)
└── en-US/                    ← SECONDARY
    ├── common.json          (✓ 已建立)
    ├── course.json          (✓ 已建立)
    ├── home.json            (✓ 已建立)
    ├── schedule.json        (✓ 已建立)
    ├── error.json           (✓ 已建立)
    ├── browse.json          (⏳ 需新增)
    ├── navigation.json      (⏳ 需新增)
    └── validation.json      (⏳ 需新增)
```

**缺失翻譯鍵 (需補充):**
- 瀏覽課程頁面相關文本
- 課程表操作相關文本
- 表單驗證訊息
- 成功/錯誤提示訊息

### 2.4 頁面流向改進

**目標:** 確保所有頁面預設顯示繁體中文

```
用戶訪問 → /browse
         ↓
    自動重定向到 /zh-TW/browse
         ↓
    顯示繁體中文介面
         ↓
    用戶可點擊語言切換至英文
```

---

## 📋 第三階段：後端重構 (待開始)

### 3.1 API 回應本地化

**目標:** API 回應包含繁體中文內容

**修改文件:** `backend/app/schemas/course.py`

```python
# 目前結構
class CourseResponse(CourseBase):
    syllabus: Optional[str]        # English
    syllabus_zh: Optional[str]     # Chinese

# 建議改進
class CourseResponse(CourseBase):
    # 根據請求語言自動選擇
    syllabus_display: str          # 根據 Accept-Language 選擇
    syllabus_zh_tw: Optional[str]  # 明確的繁體中文
    syllabus_en: Optional[str]     # 明確的英文
```

### 3.2 搜尋和過濾

**改進搜尋以支援繁體中文:**
- 支援繁體中文課程名稱搜尋
- 支援繁體中文教師名稱搜尋
- 支援繁體中文系所搜尋

### 3.3 API 端點文檔

**更新 FastAPI Swagger 文檔:**
- 所有參數說明改為繁體中文
- 所有回應範例使用繁體中文
- 改進用戶體驗

### 3.4 錯誤訊息本地化

**後端返回的錯誤訊息需支援繁體中文:**

```python
# 例如
errors = {
    "COURSE_NOT_FOUND": "找不到該課程",
    "INVALID_SEMESTER": "無效的學期",
    "DATABASE_ERROR": "資料庫錯誤，請稍後重試"
}
```

---

## 📋 第四階段：資料整合 (待開始)

### 4.1 課程綱要資料導入

**步驟:**
1. 等待 course_outline_scraper.py 完成
2. 讀取 `outlines_all.json`
3. 解析每個課程的綱要
4. 按課程號匹配資料庫記錄
5. 更新 `syllabus` 和 `syllabus_zh` 欄位

**腳本:**
```python
# scraper/import_syllabus_to_database.py (需新建)
def import_syllabus_data():
    # 1. 讀取 outlines_all.json
    # 2. 遍歷 70,239 課程
    # 3. 按 crs_no 匹配資料庫課程
    # 4. 更新 syllabus (English) 和 syllabus_zh (zh-TW)
    # 5. 批量提交
    pass
```

### 4.2 資料品質檢查

**驗證:**
- 所有 70,239 門課程已匹配
- 英文和繁體中文綱要都已導入
- 沒有重複或損壞的記錄
- 綱要內容完整有效

---

## 📋 第五階段：測試驗證 (待開始)

### 5.1 前端測試

**功能測試:**
- [ ] 訪問主頁，確認預設為繁體中文
- [ ] 搜尋課程 (繁體中文)
- [ ] 查看課程詳情，驗證繁體中文綱要顯示
- [ ] 切換至英文，驗證英文綱要顯示
- [ ] 課程表功能正常
- [ ] 所有按鈕文本為繁體中文

### 5.2 後端 API 測試

**API 端點測試:**
- [ ] GET /api/courses - 返回繁體中文 metadata
- [ ] GET /api/courses/{id} - 返回包含繁體中文綱要
- [ ] GET /api/courses/search?q=計算 - 繁體中文搜尋
- [ ] 文檔頁面 (http://localhost:8000/docs) 繁體中文

### 5.3 跨瀏覽器測試

**測試環境:**
- Chrome (latest)
- Firefox (latest)
- Safari
- Edge
- 行動裝置 (iOS Safari, Chrome Mobile)

### 5.4 效能測試

**測試項目:**
- 首頁載入時間 < 2 秒
- 課程列表載入 < 1 秒
- 搜尋回應 < 500ms
- 資料庫查詢優化

---

## 📋 第六階段：部署準備 (待開始)

### 6.1 生產環境設定

**環境變數:**
```bash
# .env.production
NEXT_PUBLIC_DEFAULT_LOCALE=zh-TW
NEXT_PUBLIC_SUPPORTED_LOCALES=zh-TW,en-US
API_BASE_URL=https://api.your-domain.com
```

### 6.2 資料庫備份

- [ ] 完整備份當前資料庫
- [ ] 建立還原計畫
- [ ] 版本控制

### 6.3 監控設定

- [ ] 設定應用監控
- [ ] 設定日誌系統
- [ ] 設定錯誤追蹤
- [ ] 設定效能監控

### 6.4 部署流程

```bash
# 1. 停止現有服務
systemctl stop nycu-course-platform

# 2. 備份資料庫
cp nycu_course_platform.db nycu_course_platform.db.backup.$(date +%s)

# 3. 部署新版本
git pull origin main
npm install  # frontend
pip install -r requirements.txt  # backend

# 4. 執行資料庫遷移
alembic upgrade head

# 5. 啟動服務
systemctl start nycu-course-platform

# 6. 驗證健康檢查
curl http://localhost:8000/health
```

---

## 📊 整體時間規劃

| 階段 | 任務 | 預期時間 | 狀態 |
|------|------|---------|------|
| 1 | 課程綱要爬蟲 | 30-45 分鐘 | 🔄 進行中 |
| 2 | 前端重構 | 2-3 小時 | ⏳ 待開始 |
| 3 | 後端重構 | 1-2 小時 | ⏳ 待開始 |
| 4 | 資料整合 | 30 分鐘 | ⏳ 待開始 |
| 5 | 測試驗證 | 1-2 小時 | ⏳ 待開始 |
| 6 | 部署準備 | 30 分鐘 | ⏳ 待開始 |
| **總計** | **完整重構** | **5-8 小時** | **35% 完成** |

---

## 🎯 立即行動項目

### 優先級 1 (立即執行)
- ✅ 完成課程綱要爬蟲 (進行中)
- ⏳ 導入綱要資料到資料庫
- ⏳ 設定 zh-TW 為預設語言

### 優先級 2 (高優先)
- ⏳ 前端 UI 本地化改進
- ⏳ 缺失翻譯鍵補充
- ⏳ API 文檔繁體中文化

### 優先級 3 (中優先)
- ⏳ 後端搜尋和過濾繁體中文
- ⏳ 錯誤訊息本地化
- ⏳ 全面測試

### 優先級 4 (低優先)
- ⏳ 效能優化
- ⏳ 監控系統
- ⏳ 生產部署

---

## 📝 檢查清單

### 爬蟲階段
- [ ] course_outline_scraper.py 執行完成
- [ ] outlines_all.json 檔案生成成功
- [ ] 包含所有 70,239 門課程
- [ ] 英文和繁體中文綱要都有

### 前端重構
- [ ] zh-TW 設為預設語言
- [ ] 所有翻譯鍵已補充
- [ ] UI 預設顯示繁體中文
- [ ] 語言切換功能正常
- [ ] 所有頁面繁體中文測試通過

### 後端重構
- [ ] API 返回繁體中文內容
- [ ] 搜尋支援繁體中文
- [ ] 錯誤訊息繁體中文
- [ ] 文檔頁面繁體中文

### 資料整合
- [ ] 綱要資料全部導入
- [ ] 資料品質驗證通過
- [ ] 資料庫備份建立

### 測試驗證
- [ ] 所有功能測試通過
- [ ] 跨瀏覽器測試通過
- [ ] 效能測試達標
- [ ] 無重大 bug

### 部署準備
- [ ] 環境變數設定完成
- [ ] 備份計畫就緒
- [ ] 監控系統配置完成
- [ ] 部署腳本測試通過

---

## 🎓 預期成果

### 完成後的平台特性

✅ **語言**
- 繁體中文為主要語言
- 英文為輔助語言
- 完整的 i18n 支持

✅ **課程資料**
- 70,239 門課程
- 完整的英文和繁體中文綱要
- 高品質的課程資訊

✅ **用戶體驗**
- 快速的搜尋和過濾
- 直觀的課程詳情頁面
- 優秀的行動設備支持

✅ **系統穩定性**
- 完整的監控和日誌
- 自動化的備份和還原
- 高可用性架構

---

**下一步:** 等待課程綱要爬蟲完成 (預計 2025-10-17 11:15)
**完成預估:** 2025-10-17 18:00 (約 7.5 小時後)

