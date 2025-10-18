# 🚀 NYCU Course Platform - GA 前壓力測試計劃

**創建日期**: 2025-10-18
**狀態**: 準備執行
**目標**: 確保平台在社群媒體發布後能承受預期流量

---

## 📊 目錄

1. [測試目標](#測試目標)
2. [預期流量分析](#預期流量分析)
3. [測試工具與環境](#測試工具與環境)
4. [測試場景](#測試場景)
5. [性能指標與目標](#性能指標與目標)
6. [執行步驟](#執行步驟)
7. [監控與分析](#監控與分析)
8. [問題處理流程](#問題處理流程)
9. [優化建議](#優化建議)

---

## 🎯 測試目標

### 主要目標
1. **容量規劃**: 確定系統能承受的最大併發用戶數
2. **穩定性驗證**: 在高負載下系統能保持穩定運行
3. **性能基準**: 建立各項性能指標的基準線
4. **瓶頸識別**: 找出系統性能瓶頸並提前優化
5. **恢復能力**: 測試系統在壓力下的恢復能力

### 成功標準
- ✅ 支持 500+ 併發用戶（社群媒體初期預期）
- ✅ API 響應時間 < 200ms (P95)
- ✅ 頁面加載時間 < 3s
- ✅ 錯誤率 < 0.1%
- ✅ 系統在 2 倍預期流量下仍能正常運行

---

## 📈 預期流量分析

### 社群媒體發布初期預測

| 時間段 | 預期訪客 | 併發用戶 | 峰值流量 |
|--------|----------|----------|----------|
| **第一小時** | 500-1000 | 50-100 | 150 |
| **前 24 小時** | 2000-5000 | 100-200 | 300 |
| **第一週** | 5000-10000 | 200-400 | 500 |
| **第一個月** | 10000-20000 | 300-600 | 800 |

### 流量模式
- **突發流量**: 社群媒體發布後的 1-2 小時
- **持續流量**: 選課期間（每學期開學前 1-2 週）
- **低谷期**: 非選課期間的平日夜間

### 關鍵頁面流量分布
1. **首頁** (30%): 新用戶入口
2. **課程瀏覽頁** (40%): 主要功能頁面
3. **課表頁** (20%): 已選課程查看
4. **課程詳情頁** (10%): 深度瀏覽

---

## 🛠️ 測試工具與環境

### 推薦測試工具

#### 1. **Apache JMeter** (推薦 ⭐⭐⭐⭐⭐)
- **優點**: 功能全面、圖形化界面、支持多種協議
- **用途**: API 壓力測試、複雜場景模擬
- **安裝**:
```bash
# macOS
brew install jmeter

# Linux
wget https://dlcdn.apache.org//jmeter/binaries/apache-jmeter-5.6.3.tgz
tar -xf apache-jmeter-5.6.3.tgz
cd apache-jmeter-5.6.3/bin
./jmeter
```

#### 2. **Locust** (推薦 ⭐⭐⭐⭐)
- **優點**: Python 編寫、易於編程、實時 Web UI
- **用途**: 可編程的壓力測試、分布式測試
- **安裝**:
```bash
pip install locust
```

#### 3. **k6** (推薦 ⭐⭐⭐⭐⭐)
- **優點**: 現代化、JavaScript 腳本、CLI 友好
- **用途**: CI/CD 集成、自動化測試
- **安裝**:
```bash
# macOS
brew install k6

# Linux
wget https://github.com/grafana/k6/releases/download/v0.48.0/k6-v0.48.0-linux-amd64.tar.gz
tar -xzf k6-v0.48.0-linux-amd64.tar.gz
sudo cp k6-v0.48.0-linux-amd64/k6 /usr/local/bin/
```

#### 4. **Playwright (已安裝)** ⭐⭐⭐
- **優點**: 真實瀏覽器行為、前端性能測試
- **用途**: 端到端測試、前端性能測試

#### 5. **Artillery** ⭐⭐⭐⭐
- **優點**: 簡單配置、雲端測試、開源
- **用途**: 快速壓力測試
- **安裝**:
```bash
npm install -g artillery
```

### 測試環境

#### 環境 1: 本地環境 (初步測試)
```bash
# 配置
- CPU: 模擬生產環境 (4 核心)
- RAM: 8GB
- 網絡: localhost (無延遲)
- 用途: 基準測試、快速迭代
```

#### 環境 2: Docker 環境 (推薦)
```bash
# 啟動完整環境
docker-compose up -d

# 配置
- Frontend: Next.js (生產模式)
- Backend: FastAPI (多 worker)
- Database: SQLite (或 PostgreSQL)
- Nginx: 反向代理
```

#### 環境 3: 雲端環境 (最終測試)
```bash
# 生產環境模擬
- 平台: DigitalOcean / AWS / GCP
- 配置: 與生產環境一致
- 用途: 最終驗證測試
```

---

## 🎬 測試場景

### 場景 1: 基本負載測試 (Baseline Load Test)

**目的**: 建立性能基準

**配置**:
- 虛擬用戶: 50
- 持續時間: 10 分鐘
- Ramp-up: 1 分鐘

**測試腳本** (k6):
```javascript
// tests/load/baseline.js
import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  stages: [
    { duration: '1m', target: 50 },  // Ramp-up
    { duration: '8m', target: 50 },  // Steady state
    { duration: '1m', target: 0 },   // Ramp-down
  ],
  thresholds: {
    http_req_duration: ['p(95)<200'],  // 95% 請求 < 200ms
    http_req_failed: ['rate<0.01'],     // 錯誤率 < 1%
  },
};

export default function () {
  // 測試首頁
  let res = http.get('http://localhost:3000');
  check(res, {
    'status is 200': (r) => r.status === 200,
    'response time < 500ms': (r) => r.timings.duration < 500,
  });

  sleep(1);

  // 測試 API
  res = http.get('http://localhost:8000/api/semesters');
  check(res, {
    'API status is 200': (r) => r.status === 200,
    'API response time < 200ms': (r) => r.timings.duration < 200,
  });

  sleep(2);
}
```

**執行**:
```bash
k6 run tests/load/baseline.js
```

### 場景 2: 壓力測試 (Stress Test)

**目的**: 找出系統極限

**配置**:
- 虛擬用戶: 0 → 500 (逐步增加)
- 持續時間: 20 分鐘
- Ramp-up: 5 分鐘

**測試腳本** (k6):
```javascript
// tests/load/stress.js
import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  stages: [
    { duration: '5m', target: 100 },   // 初期流量
    { duration: '5m', target: 200 },   // 正常峰值
    { duration: '5m', target: 400 },   // 高峰值
    { duration: '5m', target: 500 },   // 極限測試
    { duration: '5m', target: 0 },     // 恢復測試
  ],
  thresholds: {
    http_req_duration: ['p(95)<500'],
    http_req_failed: ['rate<0.05'],
  },
};

export default function () {
  const actions = [
    () => http.get('http://localhost:3000'),
    () => http.get('http://localhost:3000/browse'),
    () => http.get('http://localhost:3000/schedule'),
    () => http.get('http://localhost:8000/api/courses?limit=50'),
    () => http.get('http://localhost:8000/api/semesters'),
  ];

  // 隨機選擇操作
  const action = actions[Math.floor(Math.random() * actions.length)];
  const res = action();

  check(res, {
    'status is 2xx': (r) => r.status >= 200 && r.status < 300,
  });

  sleep(Math.random() * 3 + 1);  // 1-4 秒隨機間隔
}
```

### 場景 3: 峰值測試 (Spike Test)

**目的**: 模擬社群媒體突發流量

**配置**:
- 虛擬用戶: 10 → 300 → 10
- 峰值持續: 2 分鐘
- 總時長: 10 分鐘

**測試腳本** (k6):
```javascript
// tests/load/spike.js
export const options = {
  stages: [
    { duration: '2m', target: 10 },    // 正常流量
    { duration: '30s', target: 300 },  // 突發流量
    { duration: '2m', target: 300 },   // 維持高峰
    { duration: '30s', target: 10 },   // 快速降低
    { duration: '5m', target: 10 },    // 恢復觀察
  ],
};

export default function () {
  // 同場景 2 的測試邏輯
}
```

### 場景 4: 持久測試 (Endurance Test)

**目的**: 檢測內存洩漏、連接池耗盡等問題

**配置**:
- 虛擬用戶: 100
- 持續時間: 2 小時
- 穩定負載

**測試腳本** (k6):
```javascript
// tests/load/endurance.js
export const options = {
  stages: [
    { duration: '5m', target: 100 },
    { duration: '110m', target: 100 },  // 穩定 2 小時
    { duration: '5m', target: 0 },
  ],
};
```

### 場景 5: 真實用戶行為模擬

**目的**: 模擬真實用戶使用模式

**Locust 腳本**:
```python
# tests/load/user_behavior.py
from locust import HttpUser, task, between
import random

class NYCUCourseUser(HttpUser):
    wait_time = between(2, 8)  # 用戶操作間隔 2-8 秒

    def on_start(self):
        """用戶會話開始"""
        self.client.get("/")

    @task(3)
    def browse_homepage(self):
        """瀏覽首頁 (30% 機率)"""
        self.client.get("/")

    @task(4)
    def browse_courses(self):
        """瀏覽課程 (40% 機率)"""
        self.client.get("/browse")

        # 模擬搜尋
        query = random.choice(["資料結構", "微積分", "程式設計", ""])
        self.client.get(f"/api/courses?q={query}&limit=50")

    @task(2)
    def view_schedule(self):
        """查看課表 (20% 機率)"""
        self.client.get("/schedule")

    @task(1)
    def view_course_detail(self):
        """查看課程詳情 (10% 機率)"""
        course_id = random.randint(1, 1000)
        self.client.get(f"/api/courses/{course_id}")
```

**執行**:
```bash
locust -f tests/load/user_behavior.py --host=http://localhost:3000
# 打開 http://localhost:8089 進行配置和監控
```

---

## 📊 性能指標與目標

### API 性能指標

| 端點 | P50 (中位數) | P95 | P99 | 目標 |
|------|--------------|-----|-----|------|
| `GET /` | < 50ms | < 100ms | < 200ms | ✅ |
| `GET /api/semesters` | < 20ms | < 50ms | < 100ms | ✅ |
| `GET /api/courses` | < 50ms | < 150ms | < 300ms | ✅ |
| `GET /api/courses/:id` | < 30ms | < 100ms | < 200ms | ✅ |
| `POST /api/schedules` | < 100ms | < 250ms | < 500ms | ✅ |

### 前端性能指標

| 指標 | 目標 | 測量工具 |
|------|------|----------|
| **LCP** (Largest Contentful Paint) | < 2.5s | Lighthouse |
| **FID** (First Input Delay) | < 100ms | Lighthouse |
| **CLS** (Cumulative Layout Shift) | < 0.1 | Lighthouse |
| **TTI** (Time to Interactive) | < 3.5s | Lighthouse |
| **TTFB** (Time to First Byte) | < 600ms | Chrome DevTools |

### 系統資源指標

| 資源 | 正常負載 | 高負載 | 警告閾值 |
|------|----------|--------|----------|
| **CPU 使用率** | < 40% | < 70% | > 80% |
| **內存使用率** | < 50% | < 75% | > 85% |
| **磁盤 I/O** | < 30% | < 60% | > 80% |
| **網絡帶寬** | < 40% | < 70% | > 85% |
| **數據庫連接** | < 20 | < 50 | > 80 |

### 錯誤率指標

| 類型 | 目標 | 警告閾值 | 臨界閾值 |
|------|------|----------|----------|
| **HTTP 4xx** | < 0.5% | > 2% | > 5% |
| **HTTP 5xx** | < 0.1% | > 0.5% | > 1% |
| **超時錯誤** | < 0.1% | > 0.5% | > 1% |
| **總錯誤率** | < 1% | > 3% | > 5% |

---

## 🚀 執行步驟

### 階段 1: 環境準備 (1-2 天)

#### 步驟 1.1: 安裝測試工具
```bash
# 安裝 k6
brew install k6  # macOS
# 或
wget https://github.com/grafana/k6/releases/download/v0.48.0/k6-v0.48.0-linux-amd64.tar.gz
tar -xzf k6-v0.48.0-linux-amd64.tar.gz
sudo cp k6-v0.48.0-linux-amd64/k6 /usr/local/bin/

# 安裝 Locust
pip install locust

# 安裝 Artillery (可選)
npm install -g artillery
```

#### 步驟 1.2: 準備測試環境
```bash
# 啟動生產模式
cd /home/thc1006/dev/nycu_course_platform

# 使用 Docker (推薦)
docker-compose down
docker-compose up -d --build

# 或本地啟動
# 後端
cd backend
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4

# 前端 (生產構建)
cd ../frontend
npm run build
npm start
```

#### 步驟 1.3: 創建測試腳本目錄
```bash
mkdir -p tests/load
```

### 階段 2: 基準測試 (半天)

#### 步驟 2.1: 執行基準測試
```bash
# 創建基準測試腳本 (上面的 baseline.js)
k6 run tests/load/baseline.js --out json=results/baseline.json

# 分析結果
k6 inspect results/baseline.json
```

#### 步驟 2.2: 記錄基準數據
```bash
# 保存結果到文檔
k6 run tests/load/baseline.js | tee results/baseline_report.txt
```

### 階段 3: 壓力測試 (1 天)

#### 步驟 3.1: 漸進式壓力測試
```bash
# 50 用戶
k6 run tests/load/stress.js --vus 50 --duration 10m

# 100 用戶
k6 run tests/load/stress.js --vus 100 --duration 10m

# 200 用戶
k6 run tests/load/stress.js --vus 200 --duration 10m

# 500 用戶
k6 run tests/load/stress.js --vus 500 --duration 10m
```

#### 步驟 3.2: 監控系統資源
```bash
# 在測試期間監控
# 終端 1: 運行壓力測試
k6 run tests/load/stress.js

# 終端 2: 監控系統
htop  # CPU/Memory
docker stats  # Docker 容器資源
```

### 階段 4: 峰值測試 (半天)

#### 步驟 4.1: 社群媒體突發流量模擬
```bash
k6 run tests/load/spike.js --out json=results/spike.json
```

#### 步驟 4.2: 恢復能力測試
觀察系統在突發流量後的恢復情況

### 階段 5: 持久測試 (2-4 小時)

#### 步驟 5.1: 長時間穩定性測試
```bash
# 後台運行
nohup k6 run tests/load/endurance.js > results/endurance.log 2>&1 &

# 定期檢查
tail -f results/endurance.log
```

### 階段 6: 真實場景測試 (半天)

#### 步驟 6.1: 運行 Locust 測試
```bash
# 啟動 Locust
locust -f tests/load/user_behavior.py --host=http://localhost:3000

# 訪問 Web UI
open http://localhost:8089

# 配置:
# - 用戶數: 200
# - 每秒生成用戶數: 10
# - 運行時間: 30 分鐘
```

### 階段 7: 結果分析與優化 (1-2 天)

#### 步驟 7.1: 生成測試報告
```bash
# 使用 k6 生成 HTML 報告
k6 run tests/load/stress.js --out json=results/report.json
```

#### 步驟 7.2: 識別瓶頸
分析以下數據:
- 響應時間趨勢
- 錯誤率
- 系統資源使用
- 數據庫查詢性能

---

## 📈 監控與分析

### 實時監控工具

#### 1. k6 內建儀表板
```bash
# 運行測試時自動顯示
k6 run tests/load/stress.js
```

#### 2. Locust Web UI
```bash
# 訪問 http://localhost:8089
locust -f tests/load/user_behavior.py
```

#### 3. 系統監控
```bash
# CPU/Memory
htop

# Docker 容器
docker stats

# 磁盤 I/O
iostat -x 1

# 網絡流量
iftop
```

#### 4. 應用日誌
```bash
# Backend 日誌
docker-compose logs -f backend

# Frontend 日誌
docker-compose logs -f frontend

# Nginx 日誌
docker-compose logs -f nginx
```

### 關鍵監控指標

#### 應用層指標
```bash
# API 響應時間
- p50, p95, p99 延遲
- 請求成功率
- 錯誤類型分布

# 前端指標
- 頁面加載時間
- 資源加載時間
- JavaScript 執行時間
```

#### 基礎設施指標
```bash
# 系統資源
- CPU 使用率 (%)
- 內存使用率 (%)
- 磁盤 I/O (MB/s)
- 網絡帶寬 (Mbps)

# 數據庫
- 查詢執行時間
- 連接數
- 查詢緩存命中率
```

### 數據收集與分析

#### 創建監控腳本
```bash
#!/bin/bash
# tests/monitor.sh

# 監控系統資源並記錄
while true; do
    echo "=== $(date) ===" >> monitoring.log

    # CPU 和內存
    echo "CPU/Memory:" >> monitoring.log
    top -bn1 | grep "Cpu(s)" >> monitoring.log
    free -h >> monitoring.log

    # Docker 容器
    echo "Docker Stats:" >> monitoring.log
    docker stats --no-stream >> monitoring.log

    # 磁盤使用
    echo "Disk Usage:" >> monitoring.log
    df -h >> monitoring.log

    echo "" >> monitoring.log
    sleep 60  # 每分鐘記錄一次
done
```

```bash
# 在測試期間運行
chmod +x tests/monitor.sh
./tests/monitor.sh &
```

---

## 🔧 問題處理流程

### 常見問題與解決方案

#### 問題 1: API 響應時間過長

**症狀**:
- P95 響應時間 > 500ms
- 高併發下延遲增加

**診斷步驟**:
```bash
# 1. 檢查數據庫查詢性能
# 在 SQLite 中啟用查詢日誌
# backend/app/config.py
SQLALCHEMY_ECHO = True

# 2. 分析慢查詢
# 查看日誌中的查詢時間

# 3. 檢查 API 瓶頸
# 使用 FastAPI 內建的性能分析
```

**解決方案**:
1. **數據庫優化**:
   - 添加索引 (acy, sem, dept_code)
   - 優化查詢 (使用 JOIN 而不是多次查詢)
   - 啟用查詢緩存

2. **API 優化**:
   - 實施響應緩存 (Redis)
   - 啟用 gzip 壓縮
   - 使用分頁減少數據量

3. **基礎設施優化**:
   - 增加 FastAPI workers
   - 使用 CDN 緩存靜態資源

#### 問題 2: 內存洩漏

**症狀**:
- 內存使用持續增長
- 長時間運行後性能下降

**診斷步驟**:
```bash
# 監控內存使用
docker stats

# Python 內存分析
pip install memory_profiler
python -m memory_profiler backend/app/main.py
```

**解決方案**:
1. 檢查數據庫連接是否正確關閉
2. 清理未使用的緩存
3. 限制緩存大小
4. 使用連接池

#### 問題 3: 數據庫連接耗盡

**症狀**:
- "Too many connections" 錯誤
- 高併發下連接失敗

**解決方案**:
```python
# backend/app/database/session.py
from sqlmodel import create_engine

engine = create_engine(
    DATABASE_URL,
    pool_size=20,           # 連接池大小
    max_overflow=10,        # 最大溢出連接
    pool_timeout=30,        # 連接超時
    pool_pre_ping=True,     # 連接驗證
)
```

#### 問題 4: 前端性能問題

**症狀**:
- 頁面加載時間 > 3s
- LCP > 2.5s

**解決方案**:
1. **代碼分割**:
```javascript
// frontend/next.config.js
module.exports = {
  webpack: (config) => {
    config.optimization.splitChunks = {
      chunks: 'all',
    };
    return config;
  },
};
```

2. **圖片優化**:
```javascript
// 使用 Next.js Image 組件
import Image from 'next/image';
```

3. **啟用 CDN**:
```nginx
# nginx.conf
location /static/ {
    expires 1y;
    add_header Cache-Control "public, immutable";
}
```

### 緊急回滾計劃

如果測試發現嚴重問題:

1. **立即停止測試**
```bash
# 停止 k6
pkill k6

# 停止 Locust
pkill locust
```

2. **收集診斷信息**
```bash
# 系統狀態
docker-compose ps
docker stats --no-stream

# 日誌
docker-compose logs > emergency_logs.txt
```

3. **重啟服務**
```bash
docker-compose restart
```

4. **分析問題並修復**

---

## 💡 優化建議

### 數據庫優化

#### 1. 添加索引
```sql
-- backend/migrations/add_performance_indexes.sql
CREATE INDEX IF NOT EXISTS idx_course_acy_sem ON courses(acy, sem);
CREATE INDEX IF NOT EXISTS idx_course_dept ON courses(dept_code);
CREATE INDEX IF NOT EXISTS idx_course_teacher ON courses(teacher);
CREATE INDEX IF NOT EXISTS idx_course_name ON courses(name);
```

#### 2. 查詢優化
```python
# backend/app/services/course_service.py
from sqlmodel import select

# 不好的查詢 (N+1 問題)
for course in courses:
    course.semester = get_semester(course.semester_id)

# 好的查詢 (JOIN)
stmt = select(Course, Semester).join(Semester)
results = session.exec(stmt).all()
```

#### 3. 連接池配置
```python
# backend/app/database/session.py
engine = create_engine(
    DATABASE_URL,
    pool_size=20,
    max_overflow=10,
    pool_recycle=3600,      # 回收舊連接
    pool_pre_ping=True,      # 驗證連接
)
```

### API 優化

#### 1. 實施緩存
```python
# backend/app/main.py
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from redis import asyncio as aioredis

@app.on_event("startup")
async def startup():
    redis = aioredis.from_url("redis://localhost")
    FastAPICache.init(RedisBackend(redis), prefix="nycu-cache:")

# 在路由中使用
from fastapi_cache.decorator import cache

@router.get("/semesters")
@cache(expire=3600)  # 緩存 1 小時
async def get_semesters():
    return semesters
```

#### 2. 響應壓縮
```python
# backend/app/main.py
from fastapi.middleware.gzip import GZipMiddleware

app.add_middleware(GZipMiddleware, minimum_size=1000)
```

#### 3. 並發處理
```python
# 增加 uvicorn workers
uvicorn app.main:app --workers 4 --host 0.0.0.0 --port 8000
```

### 前端優化

#### 1. 啟用 Next.js 優化
```javascript
// frontend/next.config.js
module.exports = {
  swcMinify: true,
  compress: true,
  images: {
    domains: ['your-cdn-domain.com'],
    formats: ['image/avif', 'image/webp'],
  },
};
```

#### 2. 實施客戶端緩存
```typescript
// frontend/lib/api.ts
import useSWR from 'swr';

export function useCourses(query: string) {
  const { data, error } = useSWR(
    `/api/courses?${query}`,
    fetcher,
    {
      revalidateOnFocus: false,
      dedupingInterval: 60000,  // 60 秒內不重複請求
    }
  );

  return { courses: data, isLoading: !error && !data, error };
}
```

#### 3. 代碼分割
```typescript
// 動態導入
const TimetableView = dynamic(() => import('@/components/schedule/TimetableView'), {
  loading: () => <LoadingSpinner />,
  ssr: false,
});
```

### 基礎設施優化

#### 1. Nginx 配置優化
```nginx
# nginx.conf
worker_processes auto;
worker_rlimit_nofile 65535;

events {
    worker_connections 4096;
    use epoll;
}

http {
    # 啟用緩存
    proxy_cache_path /var/cache/nginx levels=1:2 keys_zone=my_cache:10m max_size=1g inactive=60m;

    # Gzip 壓縮
    gzip on;
    gzip_vary on;
    gzip_types text/plain text/css application/json application/javascript;

    # 連接優化
    keepalive_timeout 65;
    keepalive_requests 100;
}
```

#### 2. Docker 優化
```yaml
# docker-compose.yml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 1G
    environment:
      - WORKERS=4
```

---

## 📋 測試清單

### 測試前檢查
- [ ] 所有測試工具已安裝
- [ ] 測試環境已準備就緒
- [ ] 測試腳本已創建
- [ ] 監控工具已配置
- [ ] 備份數據已完成

### 測試執行
- [ ] 基準測試 (Baseline)
- [ ] 壓力測試 (Stress)
- [ ] 峰值測試 (Spike)
- [ ] 持久測試 (Endurance)
- [ ] 真實場景測試

### 測試後檢查
- [ ] 測試結果已記錄
- [ ] 性能瓶頸已識別
- [ ] 優化方案已實施
- [ ] 重新測試驗證
- [ ] 測試報告已完成

---

## 📊 預期結果與成功標準

### 最低要求 (必須達成)
- ✅ 支持 200 併發用戶，錯誤率 < 1%
- ✅ API P95 響應時間 < 300ms
- ✅ 頁面加載時間 < 3.5s
- ✅ 系統在 1.5 倍預期流量下穩定運行

### 理想目標 (力爭達成)
- ⭐ 支持 500 併發用戶，錯誤率 < 0.1%
- ⭐ API P95 響應時間 < 200ms
- ⭐ 頁面加載時間 < 2.5s
- ⭐ 系統在 2 倍預期流量下穩定運行

### 優秀表現 (超越預期)
- 🏆 支持 1000 併發用戶
- 🏆 API P95 響應時間 < 150ms
- 🏆 頁面加載時間 < 2s
- 🏆 零停機時間

---

## 📝 測試報告模板

測試完成後，創建報告 `docs/deployment/STRESS_TEST_RESULTS_YYYY-MM-DD.md`:

```markdown
# 壓力測試結果報告

**測試日期**: YYYY-MM-DD
**測試人員**: Your Name
**環境**: Docker / 雲端 / 本地

## 測試摘要
- 測試持續時間: X 小時
- 最大併發用戶: XXX
- 總請求數: XXX,XXX
- 成功率: XX.X%

## 性能指標
| 指標 | 結果 | 目標 | 狀態 |
|------|------|------|------|
| P95 響應時間 | XXms | <200ms | ✅/❌ |
| 錯誤率 | X.X% | <0.1% | ✅/❌ |
| ...

## 發現的問題
1. 問題描述
2. 影響範圍
3. 解決方案

## 優化建議
1. ...
2. ...

## 結論
系統是否準備好 GA: ✅ 是 / ❌ 否
```

---

## 🎯 總結

這個壓力測試計劃涵蓋了：
1. ✅ 多種測試場景 (基準、壓力、峰值、持久)
2. ✅ 完整的測試工具和腳本
3. ✅ 詳細的性能指標和目標
4. ✅ 系統監控和問題診斷
5. ✅ 優化建議和最佳實踐

按照這個計劃執行，您將能夠：
- 了解系統的真實承載能力
- 提前發現並修復性能瓶頸
- 為社群媒體發布做好充分準備
- 確保用戶獲得良好的使用體驗

祝測試順利！🚀
