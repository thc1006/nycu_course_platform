const { i18n } = require('./next-i18next.config');

/**
 * @type {import('next').NextConfig}
 */
const nextConfig = {
  i18n,
  reactStrictMode: true,
  typescript: {
    ignoreBuildErrors: true
  },
  eslint: {
    ignoreDuringBuilds: true
  },
  webpack: (config, { isServer }) => {
    config.optimization.usedExports = false;
    return config;
  },
  async rewrites() {
    // No rewrites needed - nginx handles /api/* proxying in production
    // All traffic should go through nginx (port 80/443)
    return [];
  }
};

module.exports = nextConfig;