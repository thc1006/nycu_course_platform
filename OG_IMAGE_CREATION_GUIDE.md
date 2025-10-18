# 🎨 Open Graph 縮圖製作指南

**完成日期:** 2025-10-18
**目的:** 為社交媒體分享創建吸引人的縮圖

---

## 📐 標準規格

### Facebook / LinkedIn Open Graph:
- **尺寸:** 1200 x 630 像素 (1.91:1 比例)
- **最小尺寸:** 600 x 315 像素
- **最大檔案大小:** 8 MB (建議 < 1 MB)
- **格式:** PNG, JPG, GIF (建議 PNG)
- **檔名:** `og-image.png`
- **位置:** `/public/og-image.png`

### Twitter Card:
- **尺寸:** 1200 x 628 像素 (summary_large_image)
- **或:** 800 x 418 像素 (summary)
- **比例:** 1.91:1 或 2:1
- **格式:** PNG, JPG, WebP

### LinkedIn:
- **尺寸:** 1200 x 627 像素
- **比例:** 1.91:1
- **建議:** 使用與 Facebook 相同的圖片

---

## 🛠️ 使用 Canva 製作 (推薦)

### 步驟 1: 建立設計
```
1. 訪問 Canva.com
2. 點擊 "建立設計"
3. 選擇 "自訂尺寸" → 1200 x 630 像素
4. 或搜尋 "Open Graph" 模板
```

### 步驟 2: 設計內容
```
📋 設計清單:
□ 背景色: #6366f1 (Indigo) 漸層
□ Logo: NYCU 校徽或平台 icon (左上角)
□ 主標題: "NYCU 選課平台" (大字, 粗體)
□ 副標題: "70,000+ 門課程 | 智慧選課系統"
□ 特色圖示: 📚 📅 🎓 ⚡
□ URL: courses.nycu.edu.tw (底部)
□ 裝飾元素: 幾何圖形或漸層
```

### 步驟 3: 匯出圖片
```
1. 點擊右上角 "分享"
2. 選擇 "下載"
3. 格式選 "PNG" (高品質)
4. 下載檔案
```

---

## 🎨 設計範本 (複製即用)

### 方案 A: 簡潔專業風
```
┌──────────────────────────────────────┐
│ 🏛️ NYCU Logo                    [Icon]│
│                                      │
│                                      │
│        NYCU 選課平台                 │
│        陽明交大課程查詢系統            │
│                                      │
│    📚 70,000+ 門課程                 │
│    📅 9 個學期完整資料                │
│    ⚡ 智慧篩選 快速搜尋              │
│                                      │
│    courses.nycu.edu.tw              │
└──────────────────────────────────────┘

顏色: 白底 + Indigo (#6366f1) 文字
風格: 乾淨、現代、專業
```

### 方案 B: 漸層活潑風
```
┌──────────────────────────────────────┐
│  [漸層背景: Indigo → Purple]           │
│                                      │
│  ✨ NYCU Logo                        │
│                                      │
│      NYCU 選課平台                   │
│      讓選課變得更簡單                  │
│                                      │
│  📚 課程查詢  📅 課表規劃            │
│  🎓 即時更新  ⚡ 智慧推薦            │
│                                      │
│  courses.nycu.edu.tw                │
└──────────────────────────────────────┘

顏色: 漸層背景 + 白色文字
風格: 現代、活潑、科技感
```

### 方案 C: 資訊豐富風
```
┌──────────────────────────────────────┐
│ NYCU 選課平台            [校徽 Logo]  │
│                                      │
│  陽明交通大學課程查詢系統              │
│                                      │
│  ┌─────┐  ┌─────┐  ┌─────┐         │
│  │70K+ │  │ 9個 │  │即時 │         │
│  │課程 │  │學期 │  │更新 │         │
│  └─────┘  └─────┘  └─────┘         │
│                                      │
│  ✓ 智慧篩選  ✓ 快速搜尋              │
│  ✓ 課表規劃  ✓ 課程評價              │
│                                      │
│  立即查詢 → courses.nycu.edu.tw     │
└──────────────────────────────────────┘

顏色: 淺灰底 + Indigo 強調
風格: 資訊清晰、專業可信
```

---

## 📱 使用 Figma 製作 (進階)

### 步驟 1: 建立框架
```figma
1. 新增 Frame: 1200 x 630
2. 命名: "OG Image - NYCU Courses"
3. 設定背景色或漸層
```

### 步驟 2: 添加圖層
```figma
圖層結構:
├── Background (填充色或漸層)
├── Decorations (幾何形狀, 選填)
├── Logo (NYCU 校徽)
├── Title (主標題文字)
├── Subtitle (副標題)
├── Features (特色列表)
└── URL (網址文字)
```

### 步驟 3: 匯出設定
```figma
Export Settings:
- Format: PNG
- Scale: 2x (高解析度)
- Include: "og-image"
```

---

## 🖼️ 線上工具快速生成

### 1. Bannerbear (自動化)
```
Website: https://www.bannerbear.com/
用途: API 自動生成 OG 圖片
適合: 需要動態生成縮圖
價格: 免費層 30 張/月
```

### 2. Cloudinary (動態 OG)
```
Service: Image Transformations
用途: URL-based 動態生成
範例:
/w_1200,h_630,c_fill,g_center/
og-template.png
```

### 3. OG Image Generator (免費)
```
Website: https://og-image.xyz/
用途: 快速生成簡單 OG 圖
限制: 樣式較陽春
```

---

## 🎯 設計原則

### 文字可讀性:
```
✅ DO:
- 使用高對比度 (白字配深底)
- 字體大小至少 60px (標題)
- 行距 1.3-1.5
- 限制文字行數 (3-4 行)

❌ DON'T:
- 使用細字體
- 文字太多
- 低對比度
- 花俏裝飾字型
```

### 視覺層次:
```
重要性排序:
1. Logo/品牌 (建立認知)
2. 主標題 (傳達價值)
3. 副標題/數據 (支持論點)
4. 圖示/裝飾 (視覺吸引)
5. URL (行動呼籲)
```

### 安全區域:
```
保持重要內容在安全區內:
- 上下左右各留 50px 邊距
- 避免文字貼邊
- Logo 有足夠呼吸空間
```

---

## 🔍 測試縮圖效果

### Facebook Sharing Debugger:
```
URL: https://developers.facebook.com/tools/debug/

步驟:
1. 輸入網址
2. 點 "Scrape Again"
3. 檢查預覽
4. 確認圖片顯示正確
5. 查看警告訊息
```

### Twitter Card Validator:
```
URL: https://cards-dev.twitter.com/validator

步驟:
1. 輸入網址
2. 查看卡片預覽
3. 確認圖片比例
4. 測試 mobile/desktop 顯示
```

### LinkedIn Post Inspector:
```
URL: https://www.linkedin.com/post-inspector/

步驟:
1. 輸入網址
2. 檢查預覽
3. 清除快取 (如需要)
4. 重新抓取
```

---

## 📦 範例素材資源

### 免費圖示:
- **Lucide Icons:** https://lucide.dev/ (MIT)
- **Heroicons:** https://heroicons.com/ (MIT)
- **Iconify:** https://iconify.design/ (多種授權)

### 免費字體:
- **Noto Sans TC:** Google Fonts (繁中)
- **Inter:** Google Fonts (英文)
- **Taipei Sans TC:** 台北黑體 (免費商用)

### 免費圖庫:
- **Unsplash:** https://unsplash.com/
- **Pexels:** https://www.pexels.com/
- **Pixabay:** https://pixabay.com/

---

## 🚀 部署步驟

### 1. 準備檔案:
```bash
# 壓縮 PNG 圖片 (減少檔案大小)
# 使用 TinyPNG: https://tinypng.com/
# 或 ImageOptim (Mac)

# 檔案位置:
/public/og-image.png          # 主縮圖
/public/og-image-square.png   # 正方形版本 (選填)
/public/twitter-card.png      # Twitter 專用 (選填)
```

### 2. 更新 Meta 標籤:
```typescript
// 在 SEO 組件或 _app.tsx
<meta property="og:image" content="/og-image.png" />
<meta property="og:image:width" content="1200" />
<meta property="og:image:height" content="630" />
```

### 3. 測試:
```bash
# 本地測試
http://localhost:3000/og-image.png

# 生產環境
https://courses.nycu.edu.tw/og-image.png
```

### 4. 刷新快取:
```
訪問 Facebook Debugger 並點擊 "Scrape Again"
等待 24-48 小時讓快取更新
```

---

## 🎨 顏色參考

### NYCU 品牌色:
```css
Primary (Indigo):   #6366f1
Secondary (Purple): #8b5cf6
Accent (Teal):      #14b8a6
Success (Green):    #10b981
Warning (Amber):    #f59e0b
Error (Red):        #ef4444
```

### 漸層建議:
```css
/* Gradient 1: Indigo to Purple */
background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);

/* Gradient 2: Indigo to Teal */
background: linear-gradient(135deg, #6366f1 0%, #14b8a6 100%);

/* Gradient 3: Light Indigo */
background: linear-gradient(135deg, #e0e7ff 0%, #c7d2fe 100%);
```

---

## ✅ 檢查清單

縮圖製作完成確認:
- [ ] 尺寸正確 (1200 x 630)
- [ ] 檔案大小 < 1 MB
- [ ] 格式為 PNG 或 JPG
- [ ] 文字清晰易讀
- [ ] Logo 顯示清楚
- [ ] 顏色對比度足夠
- [ ] 已壓縮優化
- [ ] 放置於 `/public/` 目錄
- [ ] Meta 標籤已更新
- [ ] Facebook Debugger 測試通過
- [ ] Twitter Validator 測試通過
- [ ] Mobile 顯示正常

---

## 📊 效果追蹤

### 追蹤指標:
```
1. 點擊率 (CTR): 社交媒體分享點擊數
2. 分享次數: Facebook/Twitter 分享統計
3. 曝光量: 社交媒體觸及人數
4. 參與度: 按讚、留言、轉發
```

### 優化建議:
```
如果 CTR 低:
→ 測試不同標題
→ 調整視覺層次
→ 使用更吸引人的數據

如果分享少:
→ 檢查預覽是否正確
→ 標題是否夠吸引人
→ 圖片是否有錯誤
```

---

## 🔄 定期更新

### 何時更新縮圖:
- 重大功能上線
- 用戶數量里程碑 (10萬、50萬)
- 季節性活動 (開學、選課週)
- 品牌重塑
- A/B 測試新設計

### 版本控制:
```
/public/og-images/
├── og-image-v1.png      (舊版備份)
├── og-image-v2.png      (測試版)
└── og-image.png         (現用版)
```

---

**最後更新:** 2025-10-18
**下次審核:** 2025-11-18 (每月檢視)
