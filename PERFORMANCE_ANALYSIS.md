# NYCU 課程平台 - 本地環境性能分析和部署方案

## 一、本地環境資源分析

### 硬件配置
```
處理器: AMD EPYC 7R32 48-Core Processor（32 核可用）
內存: 15 GB 總計 | 13 GB 可用
磁盤: 50 GB 總計 | 37 GB 可用空間（可用率 74%）
```

### 軟件環境
```
操作系統: Linux 6.12.48+deb13-amd64 (Debian 13)
Docker: 28.5.1 已安裝並運行
Kubernetes: v1.34.1 已安裝並配置
Python: 3.13.5
Node.js: v22.20.0
```

### 環境評估結論
✅ **優秀** - 資源充足支持完整的開發、測試和部署流程

---

## 二、應用性能需求分析

### 2.1 後端 (FastAPI) 性能指標
**預期用戶並發**: 100-500 同時用戶
**數據量**: 5-10 年度 × 2 學期 × 3000-5000 課程 = ~15,000-50,000 課程記錄

**性能目標**:
- API 響應時間: < 200ms (P95)
- 吞吐量: > 1000 req/s
- 內存占用: < 500MB
- CPU 使用率: < 30% 正常負載

### 2.2 前端 (Next.js) 性能指標
**目標用戶**: 1000+ 並發訪問
**首頁加載時間**: < 3 秒
**課程搜尋響應**: < 500ms

**性能目標**:
- 首頁 Core Web Vitals: LCP < 2.5s, FID < 100ms, CLS < 0.1
- 包大小: < 300KB (gzipped)
- 捆綁時間: < 30 秒

### 2.3 數據爬蟲性能指標
**爬蟲目標**: 完整掃描所有年度和學期
**數據量**: 15,000-50,000 課程
**時間目標**: < 30 分鐘完成一次完整爬取
**限制**:
- 最大並發請求: 5-10
- 請求延遲: 0.5-1 秒
- 重試機制: 3 次

---

## 三、推薦的服務架構

### 3.1 開發環境 (Development)
```
┌─────────────────────────────────────────────────────────┐
│                    開發者本地機器                        │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────────────┐        ┌──────────────────┐      │
│  │  FastAPI 後端   │        │  Next.js 前端    │      │
│  │  (localhost:8000)        │  (localhost:3000)│      │
│  └──────────────────┘        └──────────────────┘      │
│           ↓                           ↓                  │
│  ┌──────────────────┐        ┌──────────────────┐      │
│  │  SQLite DB      │        │  SWR Cache       │      │
│  │  (本地)          │        │  (瀏覽器)         │      │
│  └──────────────────┘        └──────────────────┘      │
│                                                          │
└─────────────────────────────────────────────────────────┘

推薦配置:
- 後端進程: 1 (開發模式，自動重新加載)
- 工作線程: 4 (uvicorn workers)
- 前端進程: 1 (Next.js dev server)
- 數據庫: SQLite (開發時) 或 PostgreSQL (可選)
```

**優點**:
- 快速開發迭代
- 無容器開銷
- 易於調試

**本機資源占用**:
- 後端: ~150MB 內存
- 前端: ~200MB 內存
- 數據庫: ~50MB 內存
- **總計**: ~400MB 內存 (可用內存充足)

---

### 3.2 Docker 容器化 (測試/預生產)
```
┌─────────────────────────────────────────────────────────┐
│                      本機 Docker                        │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────────────┐  ┌──────────────────────────┐   │
│  │ FastAPI容器      │  │ Next.js 容器             │   │
│  │ (4核, 512MB)     │  │ (2核, 512MB)             │   │
│  └──────────────────┘  └──────────────────────────┘   │
│           ↓                      ↓                      │
│  ┌──────────────────┐  ┌──────────────────────────┐   │
│  │ PostgreSQL容器   │  │ Redis 容器 (可選)        │   │
│  │ (2核, 512MB)     │  │ (1核, 256MB)             │   │
│  └──────────────────┘  └──────────────────────────┘   │
│                                                          │
│  ┌──────────────────┐                                  │
│  │ nginx/Traefik    │                                  │
│  │ (反向代理)        │                                  │
│  └──────────────────┘                                  │
│                                                          │
└─────────────────────────────────────────────────────────┘

推薦配置 (docker-compose):
- FastAPI: 2 個容器實例 (負載均衡)
- Next.js: 1 個容器 (可按需擴展)
- PostgreSQL: 1 個容器 (單主配置)
- Redis: 1 個容器 (用於會話和緩存)
- Nginx: 1 個容器 (反向代理)
```

**優點**:
- 環境隔離
- 易於擴展
- 接近生產環境
- 便於CI/CD集成

**資源占用**:
- FastAPI × 2: 1.0GB 內存
- Next.js: 0.5GB 內存
- PostgreSQL: 0.5GB 內存
- Redis: 0.25GB 內存
- Nginx: 0.1GB 內存
- **總計**: ~2.35GB 內存 (可用內存充足)

**推薦命令**:
```bash
# 啟動所有服務
docker-compose -f docker-compose.yml up -d

# 查看日誌
docker-compose logs -f

# 擴展後端實例
docker-compose up -d --scale backend=4

# 停止所有服務
docker-compose down
```

---

### 3.3 Kubernetes 部署 (生產)
```
┌─────────────────────────────────────────────────────────┐
│                    Kubernetes 集群                      │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌─────────────────────────────────────────────────┐   │
│  │               Service Mesh (可選)                │   │
│  └─────────────────────────────────────────────────┘   │
│                     ↓                                   │
│  ┌──────────────────────┐  ┌──────────────────────┐   │
│  │ FastAPI 部署 (副本:3)│  │ Next.js 部署 (副本:2)│   │
│  │ (自動伸縮: 2-8)     │  │ (自動伸縮: 1-5)     │   │
│  └──────────────────────┘  └──────────────────────┘   │
│           ↓                         ↓                   │
│  ┌──────────────────────┐  ┌──────────────────────┐   │
│  │ PostgreSQL StatefulSet    │ PersistentVolume   │   │
│  │ (備份和高可用)             │ (數據持久化)        │   │
│  └──────────────────────┘  └──────────────────────┘   │
│                                                          │
│  ┌──────────────────────┐  ┌──────────────────────┐   │
│  │ Redis StatefulSet    │  │ Ingress Controller  │   │
│  │ (會話和緩存)          │  │ (外網訪問)           │   │
│  └──────────────────────┘  └──────────────────────┘   │
│                                                          │
│  ┌─────────────────────────────────────────────────┐   │
│  │ 監控 (Prometheus) | 日誌 (ELK) | 跟蹤 (Jaeger)  │   │
│  └─────────────────────────────────────────────────┘   │
│                                                          │
└─────────────────────────────────────────────────────────┘

推薦部署配置:
- 命名空間: production
- FastAPI:
  - 副本: 3 個基礎，自動伸縮至 8 個
  - CPU: 請求 500m, 限制 1000m
  - 內存: 請求 256Mi, 限制 512Mi

- Next.js:
  - 副本: 2 個基礎，自動伸縮至 5 個
  - CPU: 請求 250m, 限制 500m
  - 內存: 請求 256Mi, 限制 512Mi

- 數據庫:
  - 備份: 每小時自動備份
  - 高可用: 多副本配置
  - 存儲: PersistentVolume 50GB
```

**優點**:
- 高可用性
- 自動伸縮
- 自愈機制
- 優秀的監控和可觀測性

**資源占用**:
- FastAPI × 3: 1.5GB 內存
- Next.js × 2: 1.0GB 內存
- PostgreSQL: 1.0GB 內存
- Redis: 0.5GB 內存
- 監控系統: 1.0GB 內存
- **總計**: ~5GB 內存 (本機資源充足)

---

## 四、數據庫選擇建議

### 開發階段
**推薦**: SQLite (文件數據庫)
```
優點:
✅ 無需額外安裝和配置
✅ 適合小型項目和原型開發
✅ 自動持久化
✅ 易於備份

缺點:
❌ 並發寫入有限
❌ 不支持複雜的分佈式事務
```

**遷移路徑**:
```python
# 開發
DATABASE_URL=sqlite:///./nycu_courses.db

# 過渡
DATABASE_URL=sqlite:///./data/nycu_courses.db
# (改進備份策略)

# 生產
DATABASE_URL=postgresql://user:pass@db.service:5432/nycu_platform
```

### 過渡/測試階段
**推薦**: PostgreSQL (Docker 容器)
```
優點:
✅ 完整的關係型數據庫功能
✅ 支持複雜查詢
✅ 高度可靠
✅ 易於備份和恢復

缺點:
❌ 需要運維
❌ 資源占用多一點
```

### 生產階段
**推薦**: PostgreSQL + 備份策略
```
優點:
✅ 企業級數據庫
✅ 支持複雜事務
✅ 優秀的備份和恢復機制
✅ 支持副本和高可用

推薦配置:
- 主從複製
- 每小時自動備份
- 時間點恢復 (PITR)
- WAL 歸檔
```

---

## 五、推薦的開發和部署流程

### Phase 1: 本機開發 (Week 1-2)
```bash
# 1. 啟動後端
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# 2. 啟動前端（新終端）
cd frontend
npm install
npm run dev

# 3. 運行測試
cd backend && pytest --cov=app
cd frontend && npm test -- --coverage

# 4. 數據導入
python -m backend.scripts.import_data

# 數據庫: SQLite (自動創建)
```

**驗證指標**:
- ✅ 後端 API 可訪問 (localhost:8000/docs)
- ✅ 前端可加載 (localhost:3000)
- ✅ 測試通過率 > 90%
- ✅ 內存占用 < 1GB

---

### Phase 2: Docker 本機測試 (Week 2-3)
```bash
# 1. 構建 Docker 鏡像
docker-compose build

# 2. 啟動服務
docker-compose up -d

# 3. 檢查日誌
docker-compose logs -f

# 4. 運行集成測試
docker-compose exec backend pytest tests/

# 5. 性能測試
ab -n 1000 -c 100 http://localhost:80/api/courses

# 6. 清理資源
docker-compose down -v
```

**驗證指標**:
- ✅ 所有容器健康運行
- ✅ API 響應 < 200ms
- ✅ 吞吐量 > 1000 req/s
- ✅ 內存穩定 < 2.5GB

---

### Phase 3: Kubernetes 測試 (Week 3-4)
```bash
# 1. 創建命名空間
kubectl create namespace nycu-platform

# 2. 部署應用
kubectl apply -f k8s/

# 3. 檢查部署狀態
kubectl get pods -n nycu-platform
kubectl logs -n nycu-platform -l app=backend

# 4. 端口轉發測試
kubectl port-forward -n nycu-platform svc/backend 8000:8000
kubectl port-forward -n nycu-platform svc/frontend 3000:3000

# 5. 性能測試
kubectl run -n nycu-platform load-test --image=apache/ab --rm -it -- -n 5000 -c 100 http://backend:8000/api/courses

# 6. 清理
kubectl delete namespace nycu-platform
```

**驗證指標**:
- ✅ Pod 自動伸縮工作
- ✅ 滾動更新成功
- ✅ 高可用性驗證
- ✅ 故障轉移有效

---

## 六、性能優化建議

### 6.1 後端優化
```python
# 1. 啟用查詢緩存
@app.get("/api/courses")
@cache(expire=300)  # 5 分鐘緩存
async def list_courses(...):
    pass

# 2. 使用 connection pooling
SQLALCHEMY_ENGINE_KWARGS = {
    "pool_size": 20,
    "max_overflow": 40,
    "pool_recycle": 3600,
}

# 3. 添加數據庫索引
class Course(SQLModel, table=True):
    acy: int = Field(index=True)
    sem: int = Field(index=True)
    crs_no: str = Field(index=True)
    # 複合索引
    __table_args__ = (
        Index('idx_acy_sem_crs_no', 'acy', 'sem', 'crs_no'),
    )

# 4. 非同步處理
@app.post("/api/import")
async def import_data(file: UploadFile):
    # 後台任務
    background_tasks.add_task(process_import, file)
    return {"status": "processing"}
```

### 6.2 前端優化
```typescript
// 1. 代碼分割
const CourseDetail = dynamic(() => import('../components/CourseDetail'), {
  loading: () => <Loading />,
});

// 2. 圖片優化
<Image
  src={courseImage}
  alt="Course"
  width={300}
  height={200}
  quality={75}
  placeholder="blur"
/>

// 3. 虛擬化長列表
import { FixedSizeList } from 'react-window';

// 4. 預連接和預加載
<link rel="preconnect" href="https://api.example.com" />
<link rel="prefetch" href="/api/courses" />
```

### 6.3 數據庫優化
```sql
-- 索引
CREATE INDEX idx_courses_acy_sem ON courses(acy DESC, sem DESC);
CREATE INDEX idx_courses_dept ON courses(dept);
CREATE INDEX idx_courses_teacher ON courses(teacher);

-- 分區（大數據量）
CREATE TABLE courses_113_1 PARTITION OF courses
  FOR VALUES FROM (113, 1) TO (113, 2);

-- 統計信息
ANALYZE courses;
```

---

## 七、監控和告警建議

### 後端監控指標
```
1. API 響應時間 (P50, P95, P99)
   - 目標: P95 < 200ms

2. 請求吞吐量 (req/s)
   - 目標: > 1000 req/s

3. 錯誤率
   - 目標: < 0.1%

4. 數據庫連接池使用率
   - 告警: > 80%

5. 內存占用
   - 告警: > 400MB
```

### 前端監控指標
```
1. 首頁加載時間 (LCP)
   - 目標: < 2.5s

2. 互動延遲 (FID)
   - 目標: < 100ms

3. 累積佈局偏移 (CLS)
   - 目標: < 0.1

4. 頁面錯誤率
   - 告警: > 0.5%

5. 捆綁大小
   - 告警: > 500KB (gzipped)
```

### 爬蟲監控指標
```
1. 爬取速度 (課程/分鐘)
   - 目標: > 50 課程/分鐘

2. 成功率
   - 目標: > 99%

3. 重試率
   - 告警: > 5%

4. 完成時間
   - 目標: < 30 分鐘（完整爬取）
```

---

## 八、推薦的實施順序

### 第一週：本機開發完成
- [ ] 後端 API 完全實現和測試
- [ ] 前端組件完全實現和測試
- [ ] 數據爬蟲實現和測試
- [ ] SQLite 數據庫成功導入測試數據

### 第二週：Docker 測試
- [ ] docker-compose.yml 編寫完成
- [ ] 所有服務容器化
- [ ] 容器間通信驗證
- [ ] 性能基準測試

### 第三-四週：Kubernetes 部署
- [ ] K8s manifests 編寫完成
- [ ] 自動伸縮配置驗證
- [ ] 高可用性測試
- [ ] 監控和日誌系統部署

---

## 九、結論和建議

### 最佳實踐
1. **開發**: 直接使用 Python + Node.js
2. **測試**: Docker Compose 本機測試
3. **生產**: Kubernetes 部署
4. **監控**: Prometheus + Grafana
5. **日誌**: ELK Stack 或 Loki

### 資源配置總結
| 階段 | 後端 | 前端 | 數據庫 | 內存需求 |
|------|------|------|--------|---------|
| 開發 | 1 進程 | 1 進程 | SQLite | ~400MB |
| Docker | 2 容器 | 1 容器 | PostgreSQL | ~2.5GB |
| K8s | 3-8 副本 | 2-5 副本 | PostgreSQL | ~5GB |

### 本機環境評估
✅ **極佳** - 32 核 CPU + 15GB 內存足以支持所有階段
- 開發階段: 最適合
- Docker 測試: 充分資源
- K8s 部署: 可單節點部署完整功能

---

此分析基於當前本地環境配置 (15GB 可用內存, 32 核 CPU, 37GB 磁盤空間) 進行，所有建議都已針對這些資源進行優化。
