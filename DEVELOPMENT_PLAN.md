# NYCU Course Platform - 完整開發計劃 (TDD 方案)

## 一、專案願景和目標
- 建立完整的、可靠的、可測試的 NYCU 課程查詢平台
- 採用 TDD 原則，確保所有功能都有對應的測試
- 建立良好的檔案結構，便於維護和擴展
- 實作所有計劃中的功能（無 skip）

---

## 二、完整的檔案結構設計

### 根目錄結構
```
nycu_course_platform/
├── backend/                    # FastAPI 後端
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py            # FastAPI 應用實例
│   │   ├── config.py          # 配置管理
│   │   ├── models/            # SQLModel 數據模型
│   │   │   ├── __init__.py
│   │   │   ├── semester.py    # 學期模型
│   │   │   └── course.py      # 課程模型
│   │   ├── schemas/           # Pydantic 序列化模型
│   │   │   ├── __init__.py
│   │   │   ├── semester.py
│   │   │   └── course.py
│   │   ├── database/          # 數據庫操作層
│   │   │   ├── __init__.py
│   │   │   ├── session.py     # 數據庫連接管理
│   │   │   ├── base.py        # Base class 和公共函數
│   │   │   ├── semester.py    # 學期 CRUD 操作
│   │   │   └── course.py      # 課程 CRUD 操作
│   │   ├── routes/            # API 路由
│   │   │   ├── __init__.py
│   │   │   ├── semesters.py   # 學期端點
│   │   │   └── courses.py     # 課程端點
│   │   ├── services/          # 業務邏輯層
│   │   │   ├── __init__.py
│   │   │   ├── semester_service.py
│   │   │   └── course_service.py
│   │   └── utils/             # 工具函數
│   │       ├── __init__.py
│   │       └── exceptions.py  # 自定義異常
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── conftest.py        # pytest 配置和夾具
│   │   ├── test_database/
│   │   │   ├── __init__.py
│   │   │   ├── test_semester_db.py
│   │   │   └── test_course_db.py
│   │   ├── test_services/
│   │   │   ├── __init__.py
│   │   │   ├── test_semester_service.py
│   │   │   └── test_course_service.py
│   │   ├── test_routes/
│   │   │   ├── __init__.py
│   │   │   ├── test_semester_routes.py
│   │   │   └── test_course_routes.py
│   │   └── test_integration/
│   │       ├── __init__.py
│   │       └── test_api_flow.py
│   ├── scripts/
│   │   ├── __init__.py
│   │   ├── import_data.py     # 數據導入
│   │   ├── init_db.py         # 初始化數據庫
│   │   └── seed_db.py         # 數據庫種子數據
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── pytest.ini
│   └── .env.example
│
├── scraper/                    # 數據爬蟲
│   ├── app/
│   │   ├── __init__.py
│   │   ├── config.py          # 爬蟲配置
│   │   ├── scraper.py         # 主爬蟲邏輯
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   └── course.py      # 課程數據模型
│   │   ├── parsers/           # HTML/數據解析器
│   │   │   ├── __init__.py
│   │   │   └── course_parser.py
│   │   ├── clients/           # HTTP 客戶端
│   │   │   ├── __init__.py
│   │   │   ├── browser_client.py  # Playwright 客戶端
│   │   │   └── http_client.py     # aiohttp 客戶端
│   │   └── utils/
│   │       ├── __init__.py
│   │       ├── file_handler.py    # 文件輸出
│   │       └── logging.py
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── conftest.py
│   │   ├── test_parsers/
│   │   │   ├── __init__.py
│   │   │   └── test_course_parser.py
│   │   ├── test_clients/
│   │   │   ├── __init__.py
│   │   │   └── test_http_client.py
│   │   └── test_scraper/
│   │       ├── __init__.py
│   │       └── test_scraper_integration.py
│   ├── data/
│   │   ├── courses.json       # 輸出的課程數據
│   │   └── courses.csv
│   ├── Dockerfile
│   ├── requirements.txt
│   └── pytest.ini
│
├── frontend/                   # Next.js 前端
│   ├── public/                # 靜態資源
│   │   └── favicon.ico
│   ├── pages/
│   │   ├── _app.tsx          # Next.js 應用包裝器
│   │   ├── _document.tsx      # HTML 文檔結構（新增）
│   │   ├── index.tsx          # 首頁
│   │   ├── schedule.tsx       # 排課頁面
│   │   ├── 404.tsx            # 404 頁面（新增）
│   │   ├── 500.tsx            # 500 頁面（新增）
│   │   └── course/
│   │       └── [id].tsx       # 課程詳情頁
│   ├── components/
│   │   ├── __init__.ts        # 導出文件
│   │   ├── common/
│   │   │   ├── Header.tsx     # 頁面頭部
│   │   │   ├── Footer.tsx     # 頁面底部
│   │   │   ├── Loading.tsx    # 加載狀態
│   │   │   ├── Error.tsx      # 錯誤顯示
│   │   │   └── Spinner.tsx    # 加載轉軸
│   │   ├── course/
│   │   │   ├── CourseCard.tsx     # 課程卡片組件
│   │   │   ├── CourseList.tsx     # 課程列表容器
│   │   │   ├── CourseDetail.tsx   # 課程詳情
│   │   │   ├── CourseFilters.tsx  # 過濾器
│   │   │   └── CourseSkeleton.tsx # 骨架屏
│   │   ├── schedule/
│   │   │   ├── ScheduleGrid.tsx       # 排課表格
│   │   │   ├── CourseSlot.tsx         # 課程時段
│   │   │   ├── ScheduleActions.tsx    # 操作按鈕
│   │   │   └── ConflictWarning.tsx    # 衝突警告
│   │   └── form/
│   │       ├── SemesterSelect.tsx # 學期下拉選擇
│   │       ├── SearchInput.tsx    # 搜尋輸入框
│   │       └── DepartmentFilter.tsx
│   ├── styles/
│   │   ├── globals.css        # 全局樣式
│   │   ├── Home.module.css    # 首頁模塊樣式
│   │   ├── Schedule.module.css # 排課頁樣式
│   │   └── utils.css          # 工具類樣式
│   ├── lib/
│   │   ├── api/               # API 服務層
│   │   │   ├── __init__.ts
│   │   │   ├── client.ts      # Axios 客戶端配置
│   │   │   ├── semester.ts    # 學期 API
│   │   │   ├── course.ts      # 課程 API
│   │   │   └── types.ts       # 類型定義
│   │   ├── hooks/             # React Hooks
│   │   │   ├── __init__.ts
│   │   │   ├── useCourses.ts  # 課程數據 Hook
│   │   │   ├── useSemesters.ts # 學期數據 Hook
│   │   │   ├── useSchedule.ts  # 排課 Hook
│   │   │   └── useLocalStorage.ts
│   │   ├── utils/             # 工具函數
│   │   │   ├── __init__.ts
│   │   │   ├── formatters.ts  # 格式化函數
│   │   │   ├── validators.ts  # 驗證函數
│   │   │   └── helpers.ts     # 輔助函數
│   │   ├── constants.ts       # 常量定義
│   │   └── types.ts           # 全局類型定義
│   ├── __tests__/             # 測試文件
│   │   ├── unit/
│   │   │   ├── utils/
│   │   │   │   ├── formatters.test.ts
│   │   │   │   └── validators.test.ts
│   │   │   ├── hooks/
│   │   │   │   ├── useCourses.test.ts
│   │   │   │   └── useSemesters.test.ts
│   │   │   └── lib/
│   │   │       └── api.test.ts
│   │   ├── components/
│   │   │   ├── CourseCard.test.tsx
│   │   │   ├── CourseList.test.tsx
│   │   │   ├── Header.test.tsx
│   │   │   └── ScheduleGrid.test.tsx
│   │   ├── pages/
│   │   │   ├── index.test.tsx
│   │   │   ├── schedule.test.tsx
│   │   │   └── course/[id].test.tsx
│   │   ├── e2e/
│   │   │   ├── home.spec.ts
│   │   │   ├── course-detail.spec.ts
│   │   │   └── schedule.spec.ts
│   │   └── setup.ts           # 測試環境配置
│   ├── package.json
│   ├── tsconfig.json
│   ├── jest.config.js
│   ├── next.config.js
│   ├── tailwind.config.js
│   ├── postcss.config.js
│   ├── .env.example
│   ├── .env.local.example
│   └── Dockerfile
│
├── data/                       # 數據層
│   ├── schema.sql             # 數據庫 schema
│   ├── migrations/            # 數據庫遷移（新增）
│   │   └── 001_initial_schema.sql
│   └── seeds/                 # 種子數據（新增）
│       └── seed_data.json
│
├── docker-compose.yml         # Docker 服務編排
├── README.md                  # 項目說明
├── DEVELOPMENT_PLAN.md        # 本計劃文件
├── ARCHITECTURE.md            # 架構文檔（新增）
├── .gitignore
├── .env.example
└── Makefile                   # 開發命令快捷方式
```

---

## 三、開發階段和里程碑

### Phase 1: 基礎設置和後端核心（Week 1）
**目標**: 建立後端基礎架構和 API

#### 1.1 後端項目初始化
- [ ] 建立虛擬環境和依賴
- [ ] 設置 FastAPI 應用基礎
- [ ] 配置 pytest 和測試環境
- [ ] 編寫 conftest.py 和測試夾具

#### 1.2 數據庫層實現（TDD）
- [ ] 編寫數據庫連接測試
- [ ] 實現 SQLModel 配置
- [ ] 編寫 Semester 模型和 CRUD 測試
- [ ] 實現 Semester 數據庫操作
- [ ] 編寫 Course 模型和 CRUD 測試
- [ ] 實現 Course 數據庫操作

#### 1.3 業務邏輯層實現（TDD）
- [ ] 編寫 SemesterService 測試
- [ ] 實現 SemesterService
- [ ] 編寫 CourseService 測試
- [ ] 實現 CourseService

#### 1.4 API 路由實現（TDD）
- [ ] 編寫 /semesters 端點測試
- [ ] 實現 /semesters 端點
- [ ] 編寫 /courses 端點測試
- [ ] 實現 /courses 端點（支持過濾）
- [ ] 編寫 /courses/{id} 端點測試
- [ ] 實現 /courses/{id} 端點

#### 1.5 集成測試
- [ ] 編寫完整 API 流程測試
- [ ] 測試錯誤處理

---

### Phase 2: 數據爬蟲和導入（Week 1-2）
**目標**: 實現數據採集管道

#### 2.1 爬蟲基礎設置
- [ ] 配置 Playwright 和 aiohttp
- [ ] 設置日誌系統
- [ ] 實現配置管理

#### 2.2 解析器實現（TDD）
- [ ] 編寫課程頁面解析器測試
- [ ] 實現課程解析邏輯
- [ ] 編寫數據驗證測試

#### 2.3 爬蟲邏輯實現（TDD）
- [ ] 編寫課程號發現功能測試
- [ ] 實現課程號發現（Playwright）
- [ ] 編寫課程頁面抓取測試
- [ ] 實現課程頁面抓取（aiohttp）

#### 2.4 導入腳本實現（TDD）
- [ ] 編寫數據導入測試
- [ ] 實現 JSON 導入
- [ ] 實現去重邏輯
- [ ] 編寫種子數據

---

### Phase 3: 前端基礎和 API 集成（Week 2-3）
**目標**: 建立前端架構和 API 通信

#### 3.1 前端項目初始化
- [ ] Next.js 項目配置
- [ ] 設置 TypeScript 和 ESLint
- [ ] 配置 Tailwind CSS
- [ ] 設置 Jest 和測試環境

#### 3.2 API 服務層（TDD）
- [ ] 編寫 API 客戶端測試
- [ ] 實現 Axios 客戶端配置
- [ ] 編寫 Semester API 測試
- [ ] 實現 Semester API
- [ ] 編寫 Course API 測試
- [ ] 實現 Course API

#### 3.3 Hooks 實現（TDD）
- [ ] 編寫 useSemesters hook 測試
- [ ] 實現 useSemesters hook
- [ ] 編寫 useCourses hook 測試
- [ ] 實現 useCourses hook
- [ ] 編寫 useSchedule hook 測試
- [ ] 實現 useSchedule hook

#### 3.4 公共組件實現（TDD）
- [ ] 編寫 Loading 組件測試
- [ ] 實現 Loading 組件
- [ ] 編寫 Error 組件測試
- [ ] 實現 Error 組件
- [ ] 編寫 Header 組件測試
- [ ] 實現 Header 組件
- [ ] 編寫 Footer 組件測試
- [ ] 實現 Footer 組件

---

### Phase 4: 首頁和課程列表功能（Week 3）
**目標**: 實現核心課程瀏覽功能

#### 4.1 課程卡片組件（TDD）
- [ ] 編寫 CourseCard 測試
- [ ] 實現 CourseCard 組件
- [ ] 編寫 CourseSkeleton 測試
- [ ] 實現 CourseSkeleton 組件

#### 4.2 課程列表組件（TDD）
- [ ] 編寫 CourseList 測試
- [ ] 實現 CourseList 組件
- [ ] 編寫 CourseFilters 測試
- [ ] 實現 CourseFilters 組件

#### 4.3 首頁實現（TDD）
- [ ] 編寫首頁測試（unit）
- [ ] 實現首頁邏輯
- [ ] 編寫首頁集成測試
- [ ] 實現數據加載狀態
- [ ] 實現錯誤處理

#### 4.4 響應式設計
- [ ] 實現移動端適配
- [ ] 實現平板端適配
- [ ] 實現桌面端適配

---

### Phase 5: 課程詳情頁面（Week 3）
**目標**: 實現課程詳細信息展示

#### 5.1 課程詳情組件（TDD）
- [ ] 編寫 CourseDetail 測試
- [ ] 實現 CourseDetail 組件

#### 5.2 課程詳情頁（TDD）
- [ ] 編寫詳情頁測試（unit）
- [ ] 實現詳情頁邏輯
- [ ] 編寫詳情頁集成測試
- [ ] 實現加載狀態
- [ ] 實現錯誤處理和 404

#### 5.3 相關功能
- [ ] 實現課程分享功能
- [ ] 實現收藏功能（可選）

---

### Phase 6: 排課功能（Week 4）
**目標**: 實現課程排課和時間衝突檢測

#### 6.1 排課組件（TDD）
- [ ] 編寫 ScheduleGrid 測試
- [ ] 實現 ScheduleGrid 組件
- [ ] 編寫 CourseSlot 測試
- [ ] 實現 CourseSlot 組件
- [ ] 編寫 ConflictWarning 測試
- [ ] 實現 ConflictWarning 組件

#### 6.2 排課邏輯（TDD）
- [ ] 編寫時間衝突檢測測試
- [ ] 實現衝突檢測邏輯
- [ ] 編寫排課數據管理測試
- [ ] 實現 useSchedule hook 完整功能

#### 6.3 排課頁面（TDD）
- [ ] 編寫排課頁測試
- [ ] 實現排課頁邏輯
- [ ] 編寫排課集成測試
- [ ] 實現拖放功能
- [ ] 實現本地存儲

#### 6.4 導出功能
- [ ] 實現 iCal 導出
- [ ] 實現 CSV 導出

---

### Phase 7: 完整測試覆蓋（Week 4）
**目標**: 達到高測試覆蓋率

#### 7.1 單元測試完成度
- [ ] 後端單元測試 > 90% 覆蓋率
- [ ] 前端單元測試 > 85% 覆蓋率

#### 7.2 集成測試
- [ ] 後端完整流程測試
- [ ] 前端組件集成測試

#### 7.3 E2E 測試（使用 Playwright/Cypress）
- [ ] 首頁加載和過濾測試
- [ ] 課程詳情頁面測試
- [ ] 排課功能完整流程測試

---

### Phase 8: 優化和文檔（Week 4）
**目標**: 性能優化和文檔完成

#### 8.1 性能優化
- [ ] 分析捆綁大小
- [ ] 實現代碼分割
- [ ] 優化圖片加載
- [ ] 實現緩存策略

#### 8.2 錯誤處理
- [ ] 實現全局錯誤邊界
- [ ] 實現 HTTP 錯誤重試
- [ ] 實現超時處理

#### 8.3 文檔和部署
- [ ] 完成 API 文檔
- [ ] 編寫部署指南
- [ ] 編寫用戶說明
- [ ] 設置 CI/CD 流程

---

## 四、TDD 開發流程

### 對於每個功能，遵循以下步驟：

1. **紅色階段 (Red)**: 編寫失敗的測試
   ```
   - 根據需求編寫測試用例
   - 測試應該失敗（因為功能還未實現）
   - 驗證測試是有意義的
   ```

2. **綠色階段 (Green)**: 實現最小功能使測試通過
   ```
   - 編寫最小化代碼使測試通過
   - 不考慮優化或完美性
   - 只需要滿足測試要求
   ```

3. **重構階段 (Refactor)**: 優化和改進代碼
   ```
   - 改進代碼結構和可讀性
   - 移除重複代碼
   - 優化性能
   - 確保所有測試仍然通過
   ```

### 測試金字塔結構
```
        /\          E2E 測試 (5-10%)
       /  \         - 完整用戶流程
      /____\
     /      \       集成測試 (20-30%)
    /        \      - 跨層功能
   /____    __\
  /          \     單元測試 (60-75%)
 /____________\    - 單個函數/組件
```

---

## 五、測試命名和組織約定

### 後端測試
```
tests/
├── test_database/
│   ├── test_[model_name]_db.py        # 数据库操作测试
├── test_services/
│   ├── test_[service_name]_service.py # 业务逻辑测试
├── test_routes/
│   ├── test_[endpoint_name]_routes.py # API端点测试
└── test_integration/
    └── test_[feature_name]_flow.py    # 端到端流程测试
```

### 前端測試
```
__tests__/
├── unit/
│   ├── utils/test_[util_name].test.ts
│   ├── hooks/test_[hook_name].test.ts
│   └── lib/test_[lib_name].test.ts
├── components/
│   └── test_[component_name].test.tsx
├── pages/
│   └── test_[page_name].test.tsx
└── e2e/
    └── [feature_name].spec.ts
```

### 測試函數命名
```
describe('[模塊/組件名稱]', () => {
  describe('[功能描述]', () => {
    it('should [預期行為] when [條件]', () => {
      // Arrange
      // Act
      // Assert
    });
  });
});
```

---

## 六、開發工具和命令

### 後端命令
```bash
# 安裝依賴
cd backend && pip install -r requirements.txt

# 運行測試
pytest
pytest -v                      # 詳細輸出
pytest --cov=app               # 覆蓋率報告
pytest -k "test_name"          # 運行特定測試

# 運行應用
uvicorn app.main:app --reload --port 8000

# 生成數據庫
python -m backend.scripts.init_db

# 導入數據
python -m backend.scripts.import_data
```

### 前端命令
```bash
# 安裝依賴
cd frontend && npm install

# 開發服務器
npm run dev

# 運行測試
npm test
npm test -- --coverage        # 覆蓋率報告
npm test -- --watch           # 監視模式

# 構建
npm run build

# 檢查
npm run lint
```

### 爬蟲命令
```bash
# 安裝依賴
cd scraper && pip install -r requirements.txt

# 運行爬蟲
python -m scraper.app.scraper

# 運行測試
pytest
```

---

## 七、定義"完成"的標準

一個功能只有在滿足以下所有條件時才算完成：

1. ✅ 所有單元測試編寫完成且通過
2. ✅ 所有集成測試編寫完成且通過
3. ✅ 代碼覆蓋率 > 80%
4. ✅ 代碼已通過 linting 和格式化檢查
5. ✅ 文檔已更新
6. ✅ 相關的 E2E 測試編寫完成且通過
7. ✅ 代碼經過 peer review（如適用）

---

## 八、進度追蹤

使用 Todo 列表進行實時進度追蹤：
- ⏳ 待處理 (pending): 尚未開始
- 🔄 進行中 (in_progress): 正在開發
- ✅ 已完成 (completed): 全部完成

---

## 九、預期時間表

- **總開發時間**: 3-4 周
- **Phase 1**: 3-4 天
- **Phase 2**: 3-4 天
- **Phase 3**: 3-4 天
- **Phase 4**: 2-3 天
- **Phase 5**: 2 天
- **Phase 6**: 3-4 天
- **Phase 7**: 2-3 天
- **Phase 8**: 2-3 天

---

## 十、持續集成 (CI) 計劃

將設置以下檢查：
- ✅ 單元測試通過
- ✅ 代碼覆蓋率 > 80%
- ✅ Linting 通過
- ✅ 類型檢查通過
- ✅ 安全掃描通過

---

此計劃遵循 TDD 原則，確保代碼質量和可維護性。
每個功能都將有完整的測試覆蓋，不會有任何功能被 skip。
