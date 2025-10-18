/**
 * Custom Document Component
 *
 * This component allows you to customize the HTML document structure.
 * It's rendered on the server side and is used to augment the application's
 * <html> and <body> tags.
 *
 * Features:
 * - Custom HTML structure
 * - Meta tags for SEO
 * - Font loading
 * - Theme color
 * - Language settings
 */

import { Html, Head, Main, NextScript } from 'next/document';

/**
 * Custom Document component
 *
 * @returns {JSX.Element} The HTML document structure
 */
export default function Document() {
  return (
    <Html lang="en" className="scroll-smooth">
      <Head>
        {/* Character Set */}
        <meta charSet="utf-8" />

        {/* Favicon */}
        <link rel="icon" href="/favicon.ico" />
        <link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png" />
        <link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png" />
        <link rel="icon" type="image/png" sizes="16x16" href="/favicon-16x16.png" />

        {/* Manifest for PWA */}
        <link rel="manifest" href="/site.webmanifest" />

        {/* Theme Color */}
        <meta name="theme-color" content="#2563eb" />
        <meta name="msapplication-TileColor" content="#2563eb" />

        {/* Fonts - Inter and Noto Sans TC from Google Fonts */}
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link
          href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Noto+Sans+TC:wght@300;400;500;600;700&display=swap"
          rel="stylesheet"
        />

        {/* SEO Meta Tags */}
        <meta name="description" content="Browse and search NYCU courses. Build your perfect schedule." />
        <meta name="keywords" content="NYCU, courses, schedule, university, Taiwan, course selection" />
        <meta name="author" content="NYCU Course Platform" />

        {/* Open Graph / Facebook */}
        <meta property="og:type" content="website" />
        <meta property="og:title" content="NYCU Course Platform" />
        <meta property="og:description" content="Browse and search NYCU courses. Build your perfect schedule." />
        <meta property="og:image" content="/og-image.png" />

        {/* Twitter */}
        <meta name="twitter:card" content="summary_large_image" />
        <meta name="twitter:title" content="NYCU Course Platform" />
        <meta name="twitter:description" content="Browse and search NYCU courses. Build your perfect schedule." />
        <meta name="twitter:image" content="/og-image.png" />

        {/* DNS Prefetch for external resources */}
        <link rel="dns-prefetch" href="https://fonts.googleapis.com" />
        <link rel="dns-prefetch" href="https://fonts.gstatic.com" />
      </Head>
      <body className="antialiased bg-gray-50 text-gray-900">
        <Main />
        <NextScript />

        {/* Optional: Add Analytics Script */}
        {/*
        {process.env.NODE_ENV === 'production' && (
          <>
            <script
              async
              src={`https://www.googletagmanager.com/gtag/js?id=${process.env.NEXT_PUBLIC_GA_ID}`}
            />
            <script
              dangerouslySetInnerHTML={{
                __html: `
                  window.dataLayer = window.dataLayer || [];
                  function gtag(){dataLayer.push(arguments);}
                  gtag('js', new Date());
                  gtag('config', '${process.env.NEXT_PUBLIC_GA_ID}');
                `,
              }}
            />
          </>
        )}
        */}
      </body>
    </Html>
  );
}
