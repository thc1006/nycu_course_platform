# NDHU 東華查課拉 - 完整技術規格報告
**Platform URL**: https://ndhu-course.dstw.dev/
**Analysis Date**: 2025-10-17
**Purpose**: 為 NYCU 課程平台提供完整的設計與功能復刻參考

---

## 目錄
1. [平台概述](#平台概述)
2. [技術架構](#技術架構)
3. [設計系統](#設計系統)
4. [頁面結構與功能](#頁面結構與功能)
5. [組件庫詳細規格](#組件庫詳細規格)
6. [互動行為與動畫](#互動行為與動畫)
7. [響應式設計](#響應式設計)
8. [數據結構推測](#數據結構推測)
9. [實現建議](#實現建議)

---

## 平台概述

### 品牌定位
- **平台名稱**: NDHU 東華查課拉
- **標語**: "東華大學最蝦趴的課程查詢平台！查課拉～查課拉～"
- **核心價值**: 輕鬆查課程、快速排課表，讓選課之路順暢無阻
- **品牌個性**: 輕鬆、友善、有趣（使用🦐✨等表情符號強化親和力）
- **Footer Slogan**: "讓選課變得更簡單 · 讓學習變得更有趣"

### 核心功能
1. **課程瀏覽** (首頁 `/`)
   - 學期選擇器
   - 課程列表展示
   - 課程搜尋與篩選

2. **課表管理** (`/schedule`)
   - 個人課表展示
   - 視覺化時間表
   - 課程新增/移除

---

## 技術架構

### 前端框架
```
Framework: Next.js (App Router)
Language: TypeScript
Styling: Tailwind CSS v4.0.14
Build Tool: Webpack
```

### 字體系統
```css
Primary Font: Geist (100-900 weight range)
- Geist Sans (主要文字)
- Geist Mono (程式碼/等寬字體)

Fallback Font Stack:
- Geist Fallback (local Arial)
- system-ui
- "Segoe UI"
- Roboto
- Helvetica
- Arial
- sans-serif
- "Apple Color Emoji"
- "Segoe UI Emoji"
```

### 圖標系統
使用 **Lucide Icons** (SVG 圖標庫)
- stroke-width: 2
- 尺寸: 16px (w-4 h-4) 或 20px (w-5 h-5)

---

## 設計系統

### 色彩系統 (Tailwind CSS Color Palette)

#### 主色調 (Primary)
```
Indigo 色系 (主要品牌色)
--color-indigo-50:  oklch(.962 .018 272.314)  // #EEF2FF
--color-indigo-100: oklch(.93 .034 272.788)   // #E0E7FF
--color-indigo-200: oklch(.87 .065 274.039)   // #C7D2FE
--color-indigo-300: oklch(.785 .115 274.713)  // #A5B4FC
--color-indigo-500: oklch(.585 .233 277.117)  // #6366F1
--color-indigo-600: oklch(.511 .262 276.966)  // #4F46E5 ⭐ 主按鈕色
--color-indigo-700: oklch(.457 .24 277.023)   // #4338CA
--color-indigo-800: oklch(.398 .195 277.366)  // #3730A3
--color-indigo-900: oklch(.359 .144 278.697)  // #312E81
```

#### 輔助色
```
Emerald 色系 (成功/活躍狀態)
--color-emerald-400: oklch(.765 .177 163.223)  // #34D399
--color-emerald-500: oklch(.696 .17 162.48)    // #10B981
--color-emerald-600: oklch(.596 .145 163.225)  // #059669

Rose/Red 色系 (強調色)
--color-rose-500:    oklch(.645 .246 16.439)   // #F43F5E ⭐ 愛心圖示
--color-red-500:     oklch(.637 .237 25.331)   // #EF4444
--color-red-600:     oklch(.577 .245 27.325)   // #DC2626
--color-red-700:     oklch(.505 .213 27.518)   // #B91C1C
```

#### 中性色 (Neutral)
```
Gray 色系 (主要文字和背景)
--color-gray-50:  oklch(.985 .002 247.839)   // #F9FAFB ⭐ 頁面背景
--color-gray-100: oklch(.967 .003 264.542)   // #F3F4F6
--color-gray-200: oklch(.928 .006 264.531)   // #E5E7EB
--color-gray-300: oklch(.872 .01 258.338)    // #D1D5DB
--color-gray-400: oklch(.707 .022 261.325)   // #9CA3AF
--color-gray-500: oklch(.551 .027 264.364)   // #6B7280
--color-gray-600: oklch(.446 .03 256.802)    // #4B5563 ⭐ 次要文字
--color-gray-700: oklch(.373 .034 259.733)   // #374151
--color-gray-800: oklch(.278 .033 256.848)   // #1F2937
--color-gray-900: oklch(.21 .034 264.665)    // #111827 ⭐ 主要文字

Slate 色系 (深色模式專用)
--color-slate-200: oklch(.929 .013 255.508)  // #E2E8F0
--color-slate-300: oklch(.869 .022 252.894)  // #CBD5E1
--color-slate-400: oklch(.704 .04 256.788)   // #94A3B8
--color-slate-500: oklch(.554 .046 257.417)  // #64748B
--color-slate-600: oklch(.446 .043 257.281)  // #475569
--color-slate-700: oklch(.372 .044 257.287)  // #334155
--color-slate-900: oklch(.208 .042 265.755)  // #0F172A
```

### 透明度使用規則
```css
/* 導航欄背景 */
bg-white/10         /* 10% 透明白色 + 模糊效果 */
dark:bg-gray-700/10

/* Footer 背景 */
bg-white/90
dark:bg-slate-900/90

/* 邊框 */
border-gray-200/50
border-slate-200/60
dark:border-slate-700/40

/* 分隔線 */
bg-slate-300/60
dark:bg-slate-600/60
```

### 字體大小與行高
```css
/* Tailwind CSS 預設值 */
--text-xs:   .75rem    (12px)  line-height: calc(1/.75)      = 1
--text-sm:   .875rem   (14px)  line-height: calc(1.25/.875)  = 1.428
--text-base: 1rem      (16px)  line-height: calc(1.5/1)      = 1.5
--text-lg:   1.125rem  (18px)  line-height: calc(1.75/1.125) = 1.556
--text-xl:   1.25rem   (20px)  line-height: calc(1.75/1.25)  = 1.4
--text-3xl:  1.875rem  (30px)  line-height: calc(2.25/1.875) = 1.2
--text-4xl:  2.25rem   (36px)  line-height: calc(2.5/2.25)   = 1.111
```

### 字重 (Font Weight)
```css
--font-weight-light:     300   (font-light)
--font-weight-medium:    500   (font-medium)   ⭐ 常用
--font-weight-semibold:  600   (font-semibold)
--font-weight-bold:      700   (font-bold)     ⭐ 標題
```

### 間距系統
```css
/* Base spacing unit: 0.25rem = 4px */
--spacing: .25rem

/* 常用間距 */
gap-2  → 8px   (元素間小間距)
gap-3  → 12px
gap-4  → 16px  ⭐ 最常用
gap-6  → 24px
gap-8  → 32px

space-x-2  → 水平間距 8px
space-x-3  → 水平間距 12px
space-y-3  → 垂直間距 12px
space-y-6  → 垂直間距 24px

px-4   → 水平 padding 16px ⭐ 常用
py-2   → 垂直 padding 8px
py-3   → 垂直 padding 12px
py-12  → 垂直 padding 48px (footer)
```

### 圓角 (Border Radius)
```css
--radius-sm:   .25rem   (4px)
--radius-md:   .375rem  (6px)
--radius-lg:   .5rem    (8px)
--radius-xl:   .75rem   (12px)  ⭐ 按鈕和卡片常用
--radius-2xl:  1rem     (16px)

rounded-full → 999px (圓形)
```

### 陰影 (Shadows)
```css
/* 主要使用的陰影 */
shadow-sm  → 0 1px 3px 0 rgba(0,0,0,.1), 0 1px 2px -1px rgba(0,0,0,.1)
shadow-md  → 0 4px 6px -1px rgba(0,0,0,.1), 0 2px 4px -2px rgba(0,0,0,.1)
shadow-lg  → 0 10px 15px -3px rgba(0,0,0,.1), 0 4px 6px -4px rgba(0,0,0,.1)
```

### 模糊效果 (Backdrop Blur)
```css
--blur-sm:  8px
--blur-md:  12px   ⭐ 導航欄使用
--blur-xl:  24px

/* 使用方式 */
backdrop-blur-md
backdrop-blur-xl
```

### 動畫
```css
/* 預設動畫 */
--animate-spin:  spin 1s linear infinite           (載入動畫)
--animate-pulse: pulse 2s cubic-bezier(.4,0,.6,1)  (愛心/指示點)

/* Transition */
--default-transition-duration: .15s
--default-transition-timing-function: cubic-bezier(.4,0,.2,1)

/* 使用範例 */
transition-all duration-200  /* 按鈕 hover 效果 */
```

---

## 頁面結構與功能

### 全域佈局結構
```
<html lang="zh-TW">
  <body class="antialiased min-h-screen flex flex-col">
    <nav>    <!-- 固定頂部導航 -->
    <main class="flex-1">  <!-- 主要內容區域，自動擴展 -->
    <footer class="mt-auto">  <!-- 底部，自動推到底部 -->
  </body>
</html>
```

### 導航欄 (Navigation)
```html
<nav class="bg-white/10 dark:bg-gray-700/10 backdrop-blur-md border-b border-gray-200/50 sticky top-0 z-50">
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
    <div class="flex justify-between items-center h-16">

      <!-- Logo 區域 -->
      <a href="/" class="flex items-center space-x-3">
        <div class="relative">
          <!-- 主圖標: 9x9 indigo-600 圓角方框 + Sparkles SVG -->
          <div class="w-9 h-9 bg-indigo-600 rounded-xl flex items-center justify-center shadow-lg">
            <svg class="lucide lucide-sparkles w-5 h-5 text-white">...</svg>
          </div>
          <!-- 右上角活躍指示點 -->
          <div class="absolute -top-1 -right-1 w-3 h-3 bg-emerald-400 rounded-full animate-pulse"></div>
        </div>
        <div class="flex flex-col">
          <span class="text-lg font-bold text-gray-900">NDHU Course</span>
          <span class="text-xs text-gray-500 -mt-1">東華查課拉</span>
        </div>
      </a>

      <!-- 導航連結 -->
      <div class="flex items-center space-x-2">
        <a href="/">
          <div class="relative flex items-center space-x-2 px-4 py-2 rounded-xl
                      transition-all duration-200
                      [當前頁面]: bg-indigo-50 text-indigo-700 shadow-sm
                      [其他頁面]: text-gray-600 hover:bg-gray-50 hover:text-gray-900">
            <svg class="lucide lucide-book-open w-4 h-4"></svg>
            <span class="text-sm font-medium">瀏覽課表</span>
            <!-- 當前頁面專用背景層 -->
            <div class="absolute inset-0 bg-indigo-100/50 rounded-xl -z-10"></div>
          </div>
        </a>
        <a href="/schedule">
          <div class="...">
            <svg class="lucide lucide-calendar w-4 h-4"></svg>
            <span class="text-sm font-medium">我的課表</span>
          </div>
        </a>
      </div>

    </div>
  </div>
</nav>
```

**導航欄特點**:
- 固定在頂部 (`sticky top-0 z-50`)
- 半透明背景 + 模糊效果 (`backdrop-blur-md`)
- 高度: 64px (`h-16`)
- 最大寬度容器: `max-w-7xl mx-auto`
- 響應式內距: `px-4 sm:px-6 lg:px-8`
- 活躍頁面有明顯視覺反饋 (indigo 背景)

### Footer (頁腳)
```html
<footer class="bg-white/90 dark:bg-slate-900/90 backdrop-blur-xl
               border-t border-slate-200/60 dark:border-slate-700/40
               mt-auto">
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
    <div class="text-center space-y-6">

      <!-- 主要標語 -->
      <div class="space-y-3">
        <p class="text-lg font-medium text-slate-700 dark:text-slate-200
                  flex items-center justify-center gap-2">
          Built with
          <span class="text-rose-500 animate-pulse text-xl">❤️</span>
          for NDHU students
        </p>
        <p class="text-slate-600 dark:text-slate-300 text-base font-light">
          讓選課變得更簡單 · 讓學習變得更有趣
          <span class="inline-block ml-1 text-lg">🦐✨</span>
        </p>
      </div>

      <!-- 分隔線 -->
      <div class="flex items-center justify-center">
        <div class="h-px bg-slate-300/60 dark:bg-slate-600/60 w-32"></div>
      </div>

      <!-- 版權與技術資訊 -->
      <div class="flex flex-col sm:flex-row items-center justify-center
                  gap-4 text-sm text-slate-500 dark:text-slate-400">
        <div class="flex items-center gap-2">
          <span class="text-xs">©</span>
          <span>2025 NDHU 東華查課拉</span>
        </div>
        <div class="hidden sm:block w-1 h-1 bg-slate-400/60 rounded-full"></div>
        <div class="flex items-center gap-2">
          <span class="text-xs">⚡</span>
          <span>Made with Next.js & TypeScript</span>
        </div>
      </div>

    </div>
  </div>
</footer>
```

**Footer 特點**:
- 半透明背景 + 強模糊效果 (`backdrop-blur-xl`)
- 自動推到底部 (`mt-auto`)
- 垂直 padding: 48px (`py-12`)
- 使用 Slate 色系（比 Gray 更柔和）
- 響應式佈局：手機垂直堆疊，桌面水平排列

---

## 首頁 (Browse Page) - `/`

### 頁面結構
```html
<main class="flex-1">
  <div class="min-h-screen bg-gray-50">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">

      <!-- 標題區域 -->
      <div class="text-center mb-12">
        <h1 class="text-4xl font-bold text-gray-900 mb-4">探索課程</h1>
        <p class="text-lg text-gray-600 max-w-2xl mx-auto">
          選擇學期，瀏覽課程，建立您的專屬課表
        </p>
      </div>

      <!-- 學期選擇器 -->
      <div class="mb-8">
        <div class="max-w-md mx-auto">
          <div class="relative">
            <button class="w-full flex items-center justify-between
                           px-4 py-3 bg-white border border-gray-200 rounded-xl
                           shadow-sm hover:shadow-md hover:border-gray-300
                           focus:outline-none focus:ring-2 focus:ring-indigo-500
                           focus:border-indigo-500
                           transition-all duration-200">
              <div class="flex items-center space-x-3">
                <div class="flex-shrink-0">
                  <svg class="lucide lucide-calendar w-5 h-5 text-indigo-600">...</svg>
                </div>
                <div class="text-left">
                  <div class="text-sm font-medium text-gray-900">選擇學期</div>
                  <div class="text-xs text-gray-500"></div>
                </div>
              </div>
              <div class="flex-shrink-0">
                <svg class="lucide lucide-chevron-down w-5 h-5 text-gray-400">...</svg>
              </div>
            </button>
          </div>
        </div>
      </div>

      <!-- 空狀態提示 -->
      <div class="text-center py-16">
        <div class="inline-flex items-center justify-center
                    w-16 h-16 bg-gray-100 rounded-full mb-4">
          <svg class="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <!-- Book icon path -->
          </svg>
        </div>
        <h3 class="text-lg font-semibold text-gray-900 mb-2">選擇學期開始探索</h3>
        <p class="text-gray-600">請選擇一個或多個學期以查看課程列表</p>
      </div>

    </div>
  </div>
</main>
```

### 學期選擇器規格
- **容器**: `max-w-md mx-auto` (居中，最大寬度 448px)
- **按鈕**:
  - 全寬 `w-full`
  - 內距: `px-4 py-3` (左右16px，上下12px)
  - 背景: 白色 + 灰色邊框
  - 圓角: `rounded-xl` (12px)
  - Hover: 陰影增強 + 邊框變深
  - Focus: indigo-500 ring (2px) + indigo 邊框
- **圖標**: Calendar icon (indigo-600, 20px)
- **文字**: 主標題 14px medium gray-900，副標題 12px gray-500

### 空狀態設計
- **圖標容器**: 64x64px 灰色圓形背景
- **圖標**: Book icon (32px, gray-400)
- **標題**: 18px font-semibold gray-900
- **描述**: 16px gray-600
- **垂直間距**: `py-16` (64px 上下)

---

## 課表頁面 (Schedule Page) - `/schedule`

### 載入狀態
```html
<div class="min-h-screen bg-gray-50">
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    <div class="text-center py-16">
      <!-- 載入動畫 -->
      <div class="inline-flex items-center justify-center
                  w-16 h-16 bg-indigo-100 rounded-full mb-4">
        <div class="animate-spin w-8 h-8 border-4 border-indigo-600
                    border-t-transparent rounded-full"></div>
      </div>
      <p class="text-gray-600 font-medium">載入課表中...</p>
    </div>
  </div>
</div>
```

### 載入動畫規格
- **容器**: 64x64px indigo-100 圓形背景
- **Spinner**:
  - 尺寸: 32x32px
  - 邊框: 4px indigo-600
  - 頂部邊框: 透明 (製造旋轉效果)
  - 動畫: `animate-spin` (1s linear infinite)

---

## 組件庫詳細規格

### 1. 按鈕組件 (Button)

#### Primary Button (主要按鈕)
```html
<button class="px-4 py-2 bg-indigo-600 text-white rounded-xl
               font-medium shadow-md hover:bg-indigo-700 hover:shadow-lg
               focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2
               transition-all duration-200">
  按鈕文字
</button>
```

#### Secondary Button (次要按鈕)
```html
<button class="px-4 py-2 bg-white text-gray-700 border border-gray-200 rounded-xl
               font-medium shadow-sm hover:bg-gray-50 hover:border-gray-300 hover:shadow-md
               focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500
               transition-all duration-200">
  按鈕文字
</button>
```

#### Ghost Button (幽靈按鈕)
```html
<button class="px-4 py-2 text-gray-600 rounded-xl
               font-medium hover:bg-gray-50 hover:text-gray-900
               transition-all duration-200">
  按鈕文字
</button>
```

#### Active State (活躍狀態按鈕)
```html
<button class="relative px-4 py-2 bg-indigo-50 text-indigo-700 rounded-xl
               font-medium shadow-sm
               transition-all duration-200">
  按鈕文字
  <div class="absolute inset-0 bg-indigo-100/50 rounded-xl -z-10"></div>
</button>
```

### 2. 輸入框組件 (Input)

#### 標準輸入框
```html
<input type="text"
       class="w-full px-4 py-3 bg-white border border-gray-200 rounded-xl
              text-sm font-medium text-gray-900 placeholder:text-gray-500
              focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500
              hover:border-gray-300 hover:shadow-sm
              transition-all duration-200"
       placeholder="輸入文字...">
```

### 3. 下拉選單 (Dropdown/Select)

#### 選擇器按鈕
```html
<button class="w-full flex items-center justify-between
               px-4 py-3 bg-white border border-gray-200 rounded-xl
               shadow-sm hover:shadow-md hover:border-gray-300
               focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500
               transition-all duration-200"
        tabindex="0">
  <div class="flex items-center space-x-3">
    <div class="flex-shrink-0">
      <svg class="lucide lucide-calendar w-5 h-5 text-indigo-600">...</svg>
    </div>
    <div class="text-left">
      <div class="text-sm font-medium text-gray-900">選擇學期</div>
      <div class="text-xs text-gray-500">副標題或選中的值</div>
    </div>
  </div>
  <div class="flex-shrink-0">
    <svg class="lucide lucide-chevron-down w-5 h-5 text-gray-400">...</svg>
  </div>
</button>
```

### 4. 卡片組件 (Card)

#### 基礎卡片
```html
<div class="bg-white border border-gray-200 rounded-xl shadow-sm
            hover:shadow-md hover:border-gray-300
            transition-all duration-200 p-6">
  <!-- 卡片內容 -->
</div>
```

#### 互動卡片 (可點擊)
```html
<div class="bg-white border border-gray-200 rounded-xl shadow-sm
            hover:shadow-lg hover:border-indigo-300 hover:scale-[1.02]
            cursor-pointer transition-all duration-200 p-6">
  <!-- 卡片內容 -->
</div>
```

### 5. Badge/Tag 組件

#### 狀態標籤
```html
<!-- 成功/活躍 -->
<span class="inline-flex items-center px-2.5 py-0.5 rounded-md
             text-xs font-medium bg-emerald-100 text-emerald-700">
  活躍
</span>

<!-- 警告 -->
<span class="inline-flex items-center px-2.5 py-0.5 rounded-md
             text-xs font-medium bg-amber-100 text-amber-700">
  警告
</span>

<!-- 錯誤 -->
<span class="inline-flex items-center px-2.5 py-0.5 rounded-md
             text-xs font-medium bg-red-100 text-red-700">
  錯誤
</span>

<!-- 資訊 -->
<span class="inline-flex items-center px-2.5 py-0.5 rounded-md
             text-xs font-medium bg-indigo-100 text-indigo-700">
  資訊
</span>
```

### 6. 圖標按鈕 (Icon Button)

```html
<button class="inline-flex items-center justify-center
               w-10 h-10 rounded-lg
               text-gray-600 hover:bg-gray-100 hover:text-gray-900
               focus:outline-none focus:ring-2 focus:ring-indigo-500
               transition-all duration-200">
  <svg class="w-5 h-5">...</svg>
</button>
```

### 7. 載入指示器 (Loading Spinner)

#### Spinner (旋轉動畫)
```html
<div class="inline-flex items-center justify-center
            w-16 h-16 bg-indigo-100 rounded-full">
  <div class="animate-spin w-8 h-8 border-4 border-indigo-600
              border-t-transparent rounded-full"></div>
</div>
```

#### Pulse (脈衝動畫)
```html
<div class="w-3 h-3 bg-emerald-400 rounded-full animate-pulse"></div>
```

### 8. 分隔線 (Divider)

#### 水平分隔線
```html
<div class="h-px bg-slate-300/60 dark:bg-slate-600/60 w-32"></div>
```

#### 垂直分隔線
```html
<div class="hidden sm:block w-1 h-1 bg-slate-400/60 rounded-full"></div>
```

---

## 互動行為與動畫

### Hover 效果規範

#### 按鈕 Hover
```css
/* 主要按鈕 */
hover:bg-indigo-700 hover:shadow-lg

/* 次要按鈕 */
hover:bg-gray-50 hover:border-gray-300 hover:shadow-md

/* Ghost 按鈕 */
hover:bg-gray-50 hover:text-gray-900
```

#### 卡片 Hover
```css
/* 一般卡片 */
hover:shadow-md hover:border-gray-300

/* 互動卡片 */
hover:shadow-lg hover:border-indigo-300 hover:scale-[1.02]
```

### Focus 效果規範

#### Ring Style (環形外框)
```css
focus:outline-none
focus:ring-2
focus:ring-indigo-500
focus:ring-offset-2
```

#### Border Style (邊框樣式)
```css
focus:border-indigo-500
```

### Transition 設定

#### 通用過渡
```css
transition-all duration-200
```

#### 自訂過渡
```css
/* 快速過渡 */
transition-colors duration-150

/* 中等過渡 */
transition-all duration-300

/* 慢速過渡 */
transition-all duration-500
```

### 動畫使用場景

#### 1. Spin Animation (旋轉)
- **用途**: 載入指示器
- **類別**: `animate-spin`
- **規格**: `spin 1s linear infinite`

#### 2. Pulse Animation (脈衝)
- **用途**: 活躍指示點、愛心圖示
- **類別**: `animate-pulse`
- **規格**: `pulse 2s cubic-bezier(.4,0,.6,1) infinite`

#### 3. Scale Transform (縮放)
- **用途**: 卡片互動反饋
- **類別**: `hover:scale-[1.02]`
- **規格**: 放大到 102%

---

## 響應式設計

### 斷點系統 (Breakpoints)
```css
/* Tailwind CSS 預設斷點 */
sm:  640px   /* 小型平板 */
md:  768px   /* 平板 */
lg:  1024px  /* 筆記型電腦 */
xl:  1280px  /* 桌面電腦 */
2xl: 1536px  /* 大螢幕 */
```

### 容器響應式規則
```css
/* 主容器 */
max-w-7xl mx-auto    /* 最大寬度 1280px，自動居中 */
px-4 sm:px-6 lg:px-8 /* 手機16px, 平板24px, 桌面32px */

/* 學期選擇器容器 */
max-w-md mx-auto     /* 最大寬度 448px，自動居中 */

/* 標題容器 */
max-w-2xl mx-auto    /* 最大寬度 672px，自動居中 */
```

### 文字響應式
```css
/* 標題 */
text-4xl  /* 36px - 保持固定 */

/* 副標題 */
text-lg   /* 18px - 保持固定 */

/* 正文 */
text-base /* 16px - 保持固定 */

/* 小字 */
text-sm   /* 14px - 保持固定 */
text-xs   /* 12px - 保持固定 */
```

### 佈局響應式

#### Footer 響應式
```css
/* 手機: 垂直堆疊 */
flex-col

/* 平板以上: 水平排列 */
sm:flex-row
```

#### 間距響應式
```css
/* 手機 → 平板 → 桌面 */
px-4 sm:px-6 lg:px-8
py-8 sm:py-12 lg:py-16
```

#### 顯示/隱藏響應式
```css
/* 手機隱藏，平板以上顯示 */
hidden sm:block

/* 手機顯示，平板以上隱藏 */
block sm:hidden
```

---

## 數據結構推測

### 課程資料結構
```typescript
interface Course {
  id: string                    // 課程唯一識別碼
  code: string                  // 課程代碼 (例: "CS101")
  name: string                  // 課程名稱
  instructor: string            // 授課教師
  department: string            // 開課系所
  credits: number               // 學分數
  semester: string              // 學期 (例: "113-1")
  schedule: CourseSchedule[]    // 上課時間
  location: string              // 上課地點
  capacity: number              // 人數上限
  enrolled: number              // 已選人數
  description?: string          // 課程描述
  prerequisites?: string[]      // 先修課程
  notes?: string                // 備註
}

interface CourseSchedule {
  day: number                   // 星期 (0=週日, 1=週一, ..., 6=週六)
  startTime: string             // 開始時間 "HH:mm"
  endTime: string               // 結束時間 "HH:mm"
  period: string                // 節次 (例: "1-2")
}
```

### 學期資料結構
```typescript
interface Semester {
  id: string                    // 學期 ID
  name: string                  // 學期名稱 (例: "113學年度第1學期")
  code: string                  // 學期代碼 (例: "113-1")
  startDate: string             // 開始日期 ISO 8601
  endDate: string               // 結束日期 ISO 8601
  isActive: boolean             // 是否為當前學期
}
```

### 使用者課表資料結構
```typescript
interface UserSchedule {
  userId: string                // 使用者 ID
  semester: string              // 學期
  courses: string[]             // 已選課程 ID 列表
  createdAt: string             // 建立時間
  updatedAt: string             // 更新時間
}
```

### API 端點推測
```
GET  /api/semesters           // 取得所有學期列表
GET  /api/courses             // 取得課程列表 (可帶學期參數)
GET  /api/courses/:id         // 取得單一課程詳情
GET  /api/schedule            // 取得使用者課表
POST /api/schedule/add        // 新增課程到課表
POST /api/schedule/remove     // 從課表移除課程
```

---

## 實現建議

### 1. 技術棧選擇
```
前端框架: Next.js 15+ (App Router)
語言:     TypeScript 5+
樣式:     Tailwind CSS 4+
圖標:     Lucide React
狀態管理: Zustand 或 Jotai (輕量級)
資料獲取: React Query (TanStack Query)
表單處理: React Hook Form
```

### 2. 專案結構建議
```
nycu-course-platform/
├── frontend/
│   ├── app/
│   │   ├── layout.tsx              # 全域佈局
│   │   ├── page.tsx                # 首頁 (課程瀏覽)
│   │   ├── schedule/
│   │   │   └── page.tsx            # 課表頁面
│   │   └── globals.css             # 全域樣式
│   ├── components/
│   │   ├── navigation/
│   │   │   └── Navbar.tsx          # 導航欄
│   │   ├── footer/
│   │   │   └── Footer.tsx          # 頁腳
│   │   ├── ui/
│   │   │   ├── Button.tsx          # 按鈕組件
│   │   │   ├── Card.tsx            # 卡片組件
│   │   │   ├── Input.tsx           # 輸入框
│   │   │   ├── Select.tsx          # 選擇器
│   │   │   ├── Badge.tsx           # 標籤
│   │   │   └── Spinner.tsx         # 載入動畫
│   │   ├── course/
│   │   │   ├── CourseCard.tsx      # 課程卡片
│   │   │   ├── CourseList.tsx      # 課程列表
│   │   │   └── CourseDetail.tsx    # 課程詳情
│   │   └── schedule/
│   │       ├── ScheduleGrid.tsx    # 課表網格
│   │       └── TimeSlot.tsx        # 時間槽
│   ├── lib/
│   │   ├── api.ts                  # API 請求函數
│   │   └── utils.ts                # 工具函數
│   ├── types/
│   │   └── course.ts               # TypeScript 型別定義
│   └── tailwind.config.ts          # Tailwind 配置
└── backend/
    └── ... (existing backend files)
```

### 3. 組件開發優先順序
1. **Phase 1 - 基礎組件**
   - Button
   - Input
   - Card
   - Badge
   - Spinner

2. **Phase 2 - 佈局組件**
   - Navbar
   - Footer
   - Layout

3. **Phase 3 - 功能組件**
   - SemesterSelector (學期選擇器)
   - CourseCard
   - CourseList
   - ScheduleGrid

4. **Phase 4 - 頁面組裝**
   - 首頁 (課程瀏覽)
   - 課表頁面

### 4. 樣式實現策略

#### 使用 Tailwind CSS 配置
```typescript
// tailwind.config.ts
import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        // 使用 NDHU 平台的色彩系統
        // (Tailwind 預設已包含 indigo, gray, slate 等色系)
      },
      fontFamily: {
        sans: ['var(--font-geist-sans)', 'system-ui', 'sans-serif'],
        mono: ['var(--font-geist-mono)', 'monospace'],
      },
      maxWidth: {
        '7xl': '80rem',
      },
      spacing: {
        // 已包含在 Tailwind 預設中
      },
      borderRadius: {
        // 已包含在 Tailwind 預設中
      },
      backdropBlur: {
        xs: '2px',
      },
    },
  },
  plugins: [],
}
export default config
```

#### 字體載入 (Next.js)
```typescript
// app/layout.tsx
import { GeistSans } from 'geist/font/sans'
import { GeistMono } from 'geist/font/mono'

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="zh-TW" className={`${GeistSans.variable} ${GeistMono.variable}`}>
      <body className="antialiased min-h-screen flex flex-col">
        {children}
      </body>
    </html>
  )
}
```

### 5. 深色模式實現

#### 切換按鈕 (選配功能)
```tsx
'use client'

import { useEffect, useState } from 'react'

export function ThemeToggle() {
  const [theme, setTheme] = useState('light')

  useEffect(() => {
    const savedTheme = localStorage.getItem('theme') || 'light'
    setTheme(savedTheme)
    document.documentElement.classList.toggle('dark', savedTheme === 'dark')
  }, [])

  const toggleTheme = () => {
    const newTheme = theme === 'light' ? 'dark' : 'light'
    setTheme(newTheme)
    localStorage.setItem('theme', newTheme)
    document.documentElement.classList.toggle('dark', newTheme === 'dark')
  }

  return (
    <button onClick={toggleTheme} className="...">
      {theme === 'light' ? '🌙' : '☀️'}
    </button>
  )
}
```

### 6. 關鍵差異調整建議

由於 NYCU 和 NDHU 的資料格式可能不同，需要注意以下調整點：

#### 學期格式
- NDHU 可能使用: "113學年度第1學期" 或 "113-1"
- NYCU 應根據實際資料格式調整

#### 課程代碼格式
- 不同學校的課程代碼格式可能不同
- 建議建立格式轉換函數

#### 時間節次系統
- 不同學校的上課時間可能不同
- 需要根據 NYCU 的時間表調整時間槽

#### 系所名稱
- 系所代碼和名稱需要對應 NYCU 的資料
- 建議建立對照表

### 7. 效能優化建議

#### 圖片優化
```tsx
import Image from 'next/image'

<Image
  src="/logo.png"
  alt="NYCU Course Platform"
  width={36}
  height={36}
  priority
/>
```

#### 代碼分割
```tsx
import dynamic from 'next/dynamic'

const ScheduleGrid = dynamic(() => import('@/components/schedule/ScheduleGrid'), {
  loading: () => <Spinner />,
  ssr: false,
})
```

#### 資料快取
```tsx
// 使用 React Query
import { useQuery } from '@tanstack/react-query'

function useCourses(semester: string) {
  return useQuery({
    queryKey: ['courses', semester],
    queryFn: () => fetchCourses(semester),
    staleTime: 5 * 60 * 1000, // 5 分鐘
  })
}
```

### 8. 無障礙設計 (Accessibility)

#### ARIA 標籤
```html
<button aria-label="選擇學期">...</button>
<nav aria-label="主要導航">...</nav>
```

#### 鍵盤導航
- 所有互動元素應可透過 Tab 鍵訪問
- 使用 `tabindex="0"` 確保可聚焦
- Enter/Space 鍵應觸發按鈕動作

#### 顏色對比
- 文字與背景對比度應 ≥ 4.5:1 (WCAG AA)
- 重要元素對比度應 ≥ 7:1 (WCAG AAA)

---

## 關鍵設計原則總結

### 1. 視覺一致性
- **主色調**: Indigo-600 (`#4F46E5`)
- **強調色**: Rose-500 (`#F43F5E`)
- **成功色**: Emerald-400/500
- **中性色**: Gray-50 到 Gray-900

### 2. 圓角使用
- **小元素**: `rounded-lg` (8px)
- **按鈕/卡片**: `rounded-xl` (12px)
- **容器**: `rounded-2xl` (16px)
- **圖標/狀態點**: `rounded-full` (圓形)

### 3. 間距規律
- **元素內距**: `p-4` 到 `p-6` (16px-24px)
- **元素間距**: `gap-2` 到 `gap-4` (8px-16px)
- **區塊間距**: `mb-8` 到 `mb-12` (32px-48px)

### 4. 動畫時長
- **快速反饋**: 150ms (顏色變化)
- **標準過渡**: 200ms (大多數互動)
- **緩慢過渡**: 300-500ms (佈局變化)

### 5. 陰影層次
- **靜止**: `shadow-sm` (微弱)
- **懸停**: `shadow-md` (中等)
- **活躍**: `shadow-lg` (強烈)

### 6. 文字層級
- **主標題**: `text-4xl font-bold` (36px 粗體)
- **副標題**: `text-lg` (18px)
- **正文**: `text-base` (16px)
- **輔助文字**: `text-sm` (14px)
- **標籤文字**: `text-xs` (12px)

---

## 附錄：完整色彩對照表

### Indigo 色系 (主品牌色)
| 名稱 | Tailwind | Hex Code | RGB | 用途 |
|------|----------|----------|-----|------|
| indigo-50 | bg-indigo-50 | #EEF2FF | rgb(238, 242, 255) | 淺背景 |
| indigo-100 | bg-indigo-100 | #E0E7FF | rgb(224, 231, 255) | 活躍狀態背景 |
| indigo-600 | bg-indigo-600 | #4F46E5 | rgb(79, 70, 229) | 主按鈕、圖標 |
| indigo-700 | bg-indigo-700 | #4338CA | rgb(67, 56, 202) | 按鈕 hover |

### Gray 色系 (中性色)
| 名稱 | Tailwind | Hex Code | RGB | 用途 |
|------|----------|----------|-----|------|
| gray-50 | bg-gray-50 | #F9FAFB | rgb(249, 250, 251) | 頁面背景 |
| gray-200 | border-gray-200 | #E5E7EB | rgb(229, 231, 235) | 邊框 |
| gray-400 | text-gray-400 | #9CA3AF | rgb(156, 163, 175) | 圖標 |
| gray-600 | text-gray-600 | #4B5563 | rgb(75, 85, 99) | 次要文字 |
| gray-900 | text-gray-900 | #111827 | rgb(17, 24, 39) | 主要文字 |

### Emerald 色系 (成功色)
| 名稱 | Tailwind | Hex Code | RGB | 用途 |
|------|----------|----------|-----|------|
| emerald-400 | bg-emerald-400 | #34D399 | rgb(52, 211, 153) | 活躍指示點 |
| emerald-500 | bg-emerald-500 | #10B981 | rgb(16, 185, 129) | 成功狀態 |

### Rose 色系 (強調色)
| 名稱 | Tailwind | Hex Code | RGB | 用途 |
|------|----------|----------|-----|------|
| rose-500 | text-rose-500 | #F43F5E | rgb(244, 63, 94) | 愛心圖示 |

---

## 結語

本規格書提供了 NDHU 東華查課拉平台的完整設計與技術細節，適用於：

1. **前端開發人員**: 作為實現 UI 的詳細參考
2. **設計師**: 理解設計系統和視覺規範
3. **專案經理**: 評估開發工作量和時程
4. **Claude Code**: 作為自動化開發的完整規格輸入

### 開發時注意事項
- 嚴格遵循色彩、間距、圓角等設計規範
- 保持組件的可重用性和一致性
- 注重響應式設計和無障礙功能
- 根據 NYCU 的實際資料格式進行必要調整
- 優先實現核心功能，再擴展進階功能

### 可擴展功能建議
1. 課程評價系統
2. 課程收藏功能
3. 課表匯出 (PDF/圖片)
4. 課程衝堂檢測
5. 學分計算器
6. 多學期課表比較
7. 課程通知提醒
8. 社群討論功能

**最後更新**: 2025-10-17
**版本**: 1.0.0
**維護者**: Claude Code Analysis Team
