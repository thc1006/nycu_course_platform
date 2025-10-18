/**
 * SEO Component - Optimized for Search Engines and Social Sharing
 *
 * Features:
 * - Dynamic meta tags for each page
 * - Open Graph tags for social media
 * - Twitter Card support
 * - Structured data (JSON-LD)
 * - Optimized for Google, Bing, and social platforms
 */

import React from 'react';
import Head from 'next/head';
import { useRouter } from 'next/router';

interface SEOProps {
  title?: string;
  description?: string;
  keywords?: string[];
  ogImage?: string;
  ogType?: 'website' | 'article';
  canonical?: string;
  noindex?: boolean;
  structuredData?: object;
}

const SEO: React.FC<SEOProps> = ({
  title = 'NYCU 選課平台 - 70,000+ 門課程 | 陽明交大課程查詢系統',
  description = '陽明交大 (NYCU) 官方選課平台，提供超過 70,000 門課程查詢、課表規劃、課程評價。支援9個學期課程資料，即時更新課程時間、教室、學分資訊。智慧篩選、快速搜尋，讓選課更簡單！',
  keywords = [
    '陽明交大',
    'NYCU',
    '選課',
    '課程查詢',
    '課表',
    '交大課程',
    '陽明課程',
    '選課系統',
    '課程時間表',
    '學分查詢',
    'NYCU courses',
    'course registration',
    'timetable',
    '交通大學',
    '陽明大學',
    '國立陽明交通大學',
  ],
  ogImage = '/og-image.png',
  ogType = 'website',
  canonical,
  noindex = false,
  structuredData,
}) => {
  const router = useRouter();
  const siteUrl = process.env.NEXT_PUBLIC_SITE_URL || 'https://courses.nycu.edu.tw';
  const currentUrl = `${siteUrl}${router.asPath}`;
  const canonicalUrl = canonical || currentUrl;

  // Generate full title
  const fullTitle = title.includes('NYCU') ? title : `${title} | NYCU 選課平台`;

  // Default Open Graph image
  const ogImageUrl = ogImage.startsWith('http') ? ogImage : `${siteUrl}${ogImage}`;

  // Default structured data for Organization
  const defaultStructuredData = {
    '@context': 'https://schema.org',
    '@type': 'EducationalOrganization',
    name: 'NYCU 選課平台',
    alternateName: '陽明交通大學選課系統',
    url: siteUrl,
    logo: `${siteUrl}/logo.png`,
    description: description,
    address: {
      '@type': 'PostalAddress',
      addressLocality: '新竹市',
      addressRegion: '台灣',
      addressCountry: 'TW',
    },
    contactPoint: {
      '@type': 'ContactPoint',
      contactType: 'Customer Service',
      availableLanguage: ['zh-TW', 'en'],
    },
  };

  const finalStructuredData = structuredData || defaultStructuredData;

  return (
    <Head>
      {/* Primary Meta Tags */}
      <title>{fullTitle}</title>
      <meta name="title" content={fullTitle} />
      <meta name="description" content={description} />
      <meta name="keywords" content={keywords.join(', ')} />

      {/* Canonical URL */}
      <link rel="canonical" href={canonicalUrl} />

      {/* Robots */}
      {noindex ? (
        <meta name="robots" content="noindex, nofollow" />
      ) : (
        <meta name="robots" content="index, follow, max-snippet:-1, max-image-preview:large, max-video-preview:-1" />
      )}

      {/* Viewport & Mobile */}
      <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=5.0" />
      <meta name="theme-color" content="#6366f1" />
      <meta name="mobile-web-app-capable" content="yes" />
      <meta name="apple-mobile-web-app-capable" content="yes" />
      <meta name="apple-mobile-web-app-status-bar-style" content="default" />
      <meta name="apple-mobile-web-app-title" content="NYCU 選課" />

      {/* Language */}
      <meta httpEquiv="content-language" content="zh-TW" />
      <link rel="alternate" hrefLang="zh-TW" href={currentUrl} />
      <link rel="alternate" hrefLang="en" href={currentUrl.replace('/zh-TW/', '/en-US/')} />
      <link rel="alternate" hrefLang="x-default" href={currentUrl} />

      {/* Open Graph / Facebook */}
      <meta property="og:type" content={ogType} />
      <meta property="og:url" content={currentUrl} />
      <meta property="og:title" content={fullTitle} />
      <meta property="og:description" content={description} />
      <meta property="og:image" content={ogImageUrl} />
      <meta property="og:image:width" content="1200" />
      <meta property="og:image:height" content="630" />
      <meta property="og:image:alt" content={fullTitle} />
      <meta property="og:site_name" content="NYCU 選課平台" />
      <meta property="og:locale" content="zh_TW" />
      <meta property="og:locale:alternate" content="en_US" />

      {/* Twitter Card */}
      <meta name="twitter:card" content="summary_large_image" />
      <meta name="twitter:url" content={currentUrl} />
      <meta name="twitter:title" content={fullTitle} />
      <meta name="twitter:description" content={description} />
      <meta name="twitter:image" content={ogImageUrl} />
      <meta name="twitter:image:alt" content={fullTitle} />
      <meta name="twitter:creator" content="@NYCU_Taiwan" />
      <meta name="twitter:site" content="@NYCU_Taiwan" />

      {/* Additional Meta Tags for Better Indexing */}
      <meta name="author" content="National Yang Ming Chiao Tung University" />
      <meta name="publisher" content="NYCU" />
      <meta name="copyright" content="© 2025 National Yang Ming Chiao Tung University" />
      <meta name="application-name" content="NYCU 選課平台" />
      <meta name="msapplication-TileColor" content="#6366f1" />
      <meta name="msapplication-config" content="/browserconfig.xml" />

      {/* Favicons */}
      <link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png" />
      <link rel="icon" type="image/png" sizes="16x16" href="/favicon-16x16.png" />
      <link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png" />
      <link rel="manifest" href="/site.webmanifest" />
      <link rel="mask-icon" href="/safari-pinned-tab.svg" color="#6366f1" />

      {/* Structured Data (JSON-LD) */}
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{
          __html: JSON.stringify(finalStructuredData),
        }}
      />

      {/* Preconnect to improve performance */}
      <link rel="preconnect" href="https://fonts.googleapis.com" />
      <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
      <link rel="dns-prefetch" href="https://timetable.nycu.edu.tw" />
      <link rel="dns-prefetch" href="https://portal.nycu.edu.tw" />

      {/* RSS Feed (if applicable) */}
      <link rel="alternate" type="application/rss+xml" title="NYCU 課程更新" href="/feed.xml" />
    </Head>
  );
};

export default SEO;
