/** @type {import('next').NextConfig} */
const PROXY = process.env.PROXY_URL || 'http://127.0.0.1:8090';

const nextConfig = {
  reactStrictMode: true,
  // Redirige las llamadas de medios al backend Python
  async rewrites() {
    return [
      { source: '/proxy/:path*', destination: PROXY + '/proxy/:path*' },
      { source: '/posters/:path*', destination: PROXY + '/posters/:path*' },
      { source: '/lib/:path*', destination: PROXY + '/lib/:path*' },
      { source: '/img/:path*', destination: PROXY + '/img/:path*' },
      { source: '/api/catalog', destination: PROXY + '/api/catalog' },
      { source: '/api/stats', destination: PROXY + '/api/stats' },
      { source: '/api/dramavibe', destination: PROXY + '/api/dramavibe' },
      { source: '/api/dramavibe/:path*', destination: PROXY + '/api/dramavibe/:path*' },
      { source: '/api/hotdrama', destination: PROXY + '/api/hotdrama' },
      { source: '/api/hotdrama/:path*', destination: PROXY + '/api/hotdrama/:path*' },
      { source: '/api/analytics/:path*', destination: PROXY + '/api/analytics/:path*' },
    ];
  },
};

module.exports = nextConfig;

