# Traditional Chinese (繁體中文) i18n Setup

## Overview

The frontend now supports Traditional Chinese (繁體中文) alongside English (en-US) through a comprehensive internationalization (i18n) setup.

## Files Created

### Configuration
- `next-i18next.config.js` - i18n configuration for Next.js

### Translation Files

**English (en-US):**
- `public/locales/en-US/common.json` - Common UI strings
- `public/locales/en-US/home.json` - Home page strings

**Traditional Chinese (zh-TW):**
- `public/locales/zh-TW/common.json` - Common UI strings (繁體中文)
- `public/locales/zh-TW/home.json` - Home page strings (繁體中文)

## Translation Coverage

### Common Strings
- Header/Navigation
- Footer
- Basic actions (Save, Cancel, Delete, etc.)
- Semester labels (Fall/Spring/Summer)
- Department names

### Home Page Strings
- Page title and subtitle
- Filter labels and placeholders
- Results display
- Error messages
- Action confirmations

## Quick Reference

### Department Names (Chinese)
- CS → 資訊工程學系 (Computer Science)
- MATH → 數學系 (Mathematics)
- PHY → 物理系 (Physics)
- EE → 電機工程學系 (Electrical Engineering)
- CHEM → 化學系 (Chemistry)

### Semester Names (Chinese)
- Fall → 上學期 (Fall Semester)
- Spring → 下學期 (Spring Semester)
- Summer → 暑期 (Summer Session)

## Next Steps for Full Implementation

### 1. Install next-i18next Package
```bash
cd frontend
npm install next-i18next i18next i18next-browser-languagedetector i18next-http-backend
```

### 2. Update next.config.js
```javascript
const { i18n } = require('./next-i18next.config');

module.exports = {
  i18n,
  // ... rest of config
};
```

### 3. Create _app.tsx Wrapper
```typescript
import { appWithTranslation } from 'next-i18next';
import i18nConfig from '../next-i18next.config';

function MyApp({ Component, pageProps }) {
  return <Component {...pageProps} />;
}

export default appWithTranslation(MyApp, i18nConfig);
```

### 4. Use Translations in Components
```typescript
import { useTranslation } from 'next-i18next';

export default function MyComponent() {
  const { t } = useTranslation('home');

  return <h1>{t('title')}</h1>;
}
```

### 5. Language Switcher Component
```typescript
import { useRouter } from 'next/router';

export function LanguageSwitcher() {
  const router = useRouter();

  return (
    <select
      value={router.locale}
      onChange={(e) => router.push(router.pathname, router.asPath, { locale: e.target.value })}
    >
      <option value="en-US">English</option>
      <option value="zh-TW">繁體中文</option>
    </select>
  );
}
```

## File Structure
```
frontend/
├── next-i18next.config.js
├── public/locales/
│   ├── en-US/
│   │   ├── common.json
│   │   └── home.json
│   └── zh-TW/
│       ├── common.json
│       └── home.json
└── ...
```

## Translation Keys Namespace

- `common` - Global UI strings
- `home` - Home page specific
- `course` - Course detail pages
- `schedule` - Schedule view
- `error` - Error messages

## Chinese Character Notes

- 繁體中文 (Fán tǐ Zhōng wén) = Traditional Chinese
- 上學期 = Fall semester (literally "upper semester")
- 下學期 = Spring semester (literally "lower semester")
- 暑期 = Summer session

## Best Practices

1. Keep translations organized by feature/page
2. Use consistent terminology across translations
3. Test both language versions thoroughly
4. Keep translation files in sync
5. Use language-specific date/number formatting
6. Consider RTL languages for future expansion

## Future Enhancements

- [ ] Add English (English) alternative
- [ ] Add simplified Chinese (zh-CN) support
- [ ] Implement auto-language detection
- [ ] Add Language preference to user profile
- [ ] Create translation management interface
- [ ] Add missing namespaces (course, schedule, error)
