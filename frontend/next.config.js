const { i18n } = require('./next-i18next.config');

/**
 * @type {import('next').NextConfig}
 */
const nextConfig = {
  i18n,
  reactStrictMode: true,
  experimental: {
    appDir: false
  },
  typescript: {
    ignoreBuildErrors: true
  },
  eslint: {
    ignoreDuringBuilds: true
  },
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'http://localhost:8000/:path*' // proxy to FastAPI backend
      }
    ];
  }
};

module.exports = nextConfig;