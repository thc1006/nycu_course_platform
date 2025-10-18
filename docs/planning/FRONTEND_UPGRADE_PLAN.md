# NYCU 課程平台 - 前端升級計劃
**參考設計**: https://ndhu-course.dstw.dev/ (東華大學課程查詢平台)

---

## 📋 目前現狀 vs 目標設計

### 當前前端特性 ✅
- Next.js 14 + React 18 框架
- 基本課程列表顯示
- API 集成正常
- 25+ 真實課程數據
- 響應式設計基礎

### 目標設計特性 (基於 NDHU 參考) 🎯

| 特性 | 優先級 | 詳情 |
|------|--------|------|
| **深色/淺色主題** | 高 | 支援主題切換，毛玻璃效果（backdrop-blur） |
| **學期多選篩選** | 高 | 允許同時選擇多個學期查看課程 |
| **高級課程搜索** | 高 | 按課程代碼、名稱、教師、系別篩選 |
| **課程卡片 UI** | 高 | 優雅的課程信息展示卡片 |
| **個人課表功能** | 中 | 將課程添加到個人時間表 |
| **課表視覺化** | 中 | 日曆/時間表視圖顯示課程安排 |
| **多語言支持** | 中 | 中英文切換 |
| **移動端優化** | 高 | 完全響應式設計 |
| **快速導入** | 低 | 一鍵導入課程至個人課表 |

---

## 🎨 UI/UX 改進方案

### Phase 1: 核心UI升級 (1-2天)

#### 1.1 主題系統 (深色/淺色)
```
實現方式:
- 使用 next-themes 庫管理主題狀態
- 配置 Tailwind CSS 深色模式
- 毛玻璃效果 (backdrop-blur)
- 平滑主題過渡動畫
```

**影響文件**:
- `frontend/pages/_app.tsx` - 主題提供者
- `frontend/tailwind.config.js` - 主題配置
- `frontend/components/ThemeToggle.tsx` - 新建主題切換組件

#### 1.2 改進頁面佈局
```
目前結構 → 目標結構:
+---------+         +------- -----+
| Header  |         |   Header    |
|---------|   →     |  (更簡潔)   |
| Content |         |-------------|
+---------+         | 篩選面板    |
                    |-------------|
                    | 課程卡片列表|
                    +-------------|
```

**新增組件**:
- `FilterPanel.tsx` - 篩選面板
- `CourseCard.tsx` - 課程卡片（重新設計）
- `SemesterSelector.tsx` - 多選學期選擇器
- `SearchBar.tsx` - 全局搜索條

#### 1.3 課程卡片設計 (參考 NDHU)
```
┌─────────────────────────────┐
│ CS0204 | Computer Prog. I   │
│ ────────────────────────────│
│ 教師: Dr. Tom Lee            │
│ 學分: 4.0                    │
│ 時間: Tue 10:00-12:00        │
│ 教室: 大數211               │
│ ────────────────────────────│
│ [加入課表]    [查看詳情]    │
└─────────────────────────────┘
```

### Phase 2: 交互功能 (2-3天)

#### 2.1 多學期篩選
```typescript
// 新 API 端點建議
GET /api/courses/?semester_id=1,2  // 多學期查詢
GET /api/semesters/available        // 获取可用学期
```

**前端實現**:
- 選擇框/切換多個學期
- 實時篩選課程列表
- 保存用戶偏好設置

#### 2.2 搜索/篩選系統
```
篩選選項:
✓ 課程代碼 (CS0204)
✓ 課程名稱 (模糊搜索)
✓ 教師名稱 (搜索)
✓ 系別篩選 (下拉選擇)
✓ 學分範圍 (滑塊)
✓ 時間段 (多選)
```

**實現位置**:
- `components/FilterPanel.tsx`
- `lib/searchUtils.ts` - 搜索邏輯
- `hooks/useFilters.ts` - 過濾狀態管理

#### 2.3 個人課表功能
```
需要新增:
1. 個人課表存儲 (localStorage / 後端)
2. 課程添加/移除按鈕
3. 課表衝突檢測
4. 導出功能 (iCal / PDF)
```

### Phase 3: 視覺優化 (1-2天)

#### 3.1 動畫和過渡
```css
/* 卡片懸停效果 */
transition: transform 0.2s, box-shadow 0.2s;
&:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0,0,0,0.12);
}
```

#### 3.2 響應式設計
```
斷點:
- 移動 (< 640px): 單列
- 平板 (640px - 1024px): 雙列
- 桌面 (> 1024px): 三列+側邊欄
```

---

## 📂 文件結構改進

```
frontend/
├── components/
│   ├── Header/
│   │   ├── Navbar.tsx (改進)
│   │   ├── ThemeToggle.tsx (新增)
│   │   └── SearchBar.tsx (新增)
│   ├── Courses/
│   │   ├── CourseCard.tsx (重新設計)
│   │   ├── CourseList.tsx (改進)
│   │   ├── CourseDetail.tsx (新增)
│   │   └── CourseGrid.tsx (新增)
│   ├── Filters/
│   │   ├── FilterPanel.tsx (新增)
│   │   ├── SemesterSelector.tsx (新增)
│   │   └── FilterButton.tsx (新增)
│   ├── Schedule/
│   │   ├── ScheduleView.tsx (新增)
│   │   ├── TimeTable.tsx (新增)
│   │   └── ScheduleCard.tsx (新增)
│   └── Common/
│       ├── Loading.tsx
│       ├── ErrorBoundary.tsx
│       └── Modal.tsx
├── pages/
│   ├── _app.tsx (主題集成)
│   ├── index.tsx (主頁 - 重新設計)
│   ├── courses/
│   │   ├── index.tsx (課程列表)
│   │   └── [id].tsx (課程詳情)
│   └── schedule/
│       └── index.tsx (個人課表)
├── hooks/
│   ├── useTheme.ts (已有)
│   ├── useFilters.ts (新增)
│   ├── useCourses.ts (改進)
│   └── useSchedule.ts (新增)
├── lib/
│   ├── api.ts (改進)
│   ├── searchUtils.ts (新增)
│   └── scheduleUtils.ts (新增)
├── styles/
│   ├── globals.css (改進)
│   ├── theme.css (新增)
│   └── components.module.css (新增)
└── tailwind.config.js (改進)
```

---

## 🛠️ 實施步驟

### 第 1 天: 基礎升級
```bash
# 1. 安裝依賴
npm install next-themes clsx tailwind-merge

# 2. 配置主題系統
# 修改 tailwind.config.js
# 修改 pages/_app.tsx

# 3. 創建基本組件
# ThemeToggle.tsx
# FilterPanel.tsx
# CourseCard.tsx (改進)
```

### 第 2 天: 功能實現
```bash
# 1. 實現多學期篩選
# 修改 API 端點支持多學期查詢
# 實現前端篩選邏輯

# 2. 實現搜索功能
# SearchBar.tsx
# 搜索邏輯集成

# 3. 個人課表基礎
# localStorage 集成
# 課程添加/移除
```

### 第 3 天: 優化和測試
```bash
# 1. 響應式設計測試
# 移動端、平板、桌面

# 2. 性能優化
# 代碼分割
# 圖片優化
# 懶加載

# 3. 最終檢查和部署
```

---

## 💻 技術棧更新

```json
{
  "dependencies": {
    "next-themes": "^14.0.0",
    "clsx": "^2.0.0",
    "tailwind-merge": "^2.2.0",
    "react-query": "^3.39.3",
    "zustand": "^4.4.0"
  },
  "devDependencies": {
    "tailwindcss": "^3.3.0",
    "postcss": "^8.4.0",
    "autoprefixer": "^10.4.0"
  }
}
```

---

## 📱 響應式設計規範

### 斷點設置
```css
/* Tailwind 標準斷點 */
sm: 640px   /* 移動設備 */
md: 768px   /* 平板 */
lg: 1024px  /* 小桌面 */
xl: 1280px  /* 標準桌面 */
2xl: 1536px /* 大屏幕 */
```

### 課程卡片佈局
```
Mobile (< 640px):   Single column  (100% width)
Tablet (640-1024):  2-3 columns
Desktop (> 1024):   3-4 columns + sidebar
```

---

## 🚀 後續優化 (Phase 4)

- 📊 課表衝突偵測和警告
- 💾 課表導出 (iCal, PDF, Excel)
- 🔔 課程通知提醒
- ⭐ 課程評分和評論系統
- 📱 PWA 應用程序化
- 🌍 多語言完整支持
- 🤖 AI 課程推薦系統

---

## ✅ 成功標準

- [x] 實現深色/淺色主題切換
- [x] 多學期篩選功能正常
- [x] 搜索功能支持多個條件
- [x] 個人課表基礎功能
- [x] 完全響應式設計
- [x] 所有頁面加載時間 < 2 秒
- [x] Mobile Lighthouse 分數 > 90
- [x] Desktop Lighthouse 分數 > 95

---

**預計完成時間**: 3-5 個工作日
**優先級**: 高 (直接影響用戶體驗)
**技術難度**: 中
