/**
 * Language Switcher Component
 *
 * Allows users to switch between English and Traditional Chinese
 * Uses Next.js useRouter to change locale without full page reload
 */

import { useRouter } from 'next/router';
import { useTranslation } from 'next-i18next';

interface LanguageSwitcherProps {
  className?: string;
}

/**
 * Language Switcher Component
 * @param className - Optional CSS classes
 * @returns JSX element for language switcher
 */
export function LanguageSwitcher({ className = '' }: LanguageSwitcherProps) {
  const router = useRouter();
  const { i18n } = useTranslation('common');

  const handleLanguageChange = (locale: string) => {
    // Navigate to the same page with the new locale
    router.push(router.pathname, router.asPath, { locale });
  };

  return (
    <div className={`flex items-center gap-2 ${className}`}>
      <label htmlFor="language-select" className="text-sm font-medium text-gray-700">
        {i18n.t && i18n.t('language') ? i18n.t('language') : 'Language'}:
      </label>
      <select
        id="language-select"
        value={router.locale || 'en-US'}
        onChange={(e) => handleLanguageChange(e.target.value)}
        className="px-3 py-1 text-sm border border-gray-300 rounded-md
                   bg-white text-gray-900
                   hover:border-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500
                   transition"
        aria-label="Select language"
      >
        <option value="en-US">English</option>
        <option value="zh-TW">繁體中文</option>
      </select>
    </div>
  );
}

export default LanguageSwitcher;
