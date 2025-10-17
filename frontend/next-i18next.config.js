const path = require('path');

const i18nConfig = {
  i18n: {
    defaultLocale: 'en-US',
    locales: ['en-US', 'zh-TW'],
  },
  ns: ['common', 'home', 'course', 'schedule', 'error'],
  defaultNS: 'common',
  localePath: path.resolve('./public/locales'),
  keySeparator: '.',
  nsSeparator: ':',
};

module.exports = i18nConfig;
