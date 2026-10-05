const BASE = process.env.SITE_URL || 'https://dramape.com';

export default function robots() {
  return {
    rules: [
      {
        userAgent: '*',
        allow: '/',
        disallow: ['/proxy/', '/api/'],
      },
      {
        userAgent: 'Googlebot',
        allow: '/',
        disallow: ['/proxy/', '/api/'],
      },
      {
        userAgent: 'Bingbot',
        allow: '/',
        disallow: ['/proxy/', '/api/'],
      },
    ],
    sitemap: BASE + '/sitemap.xml',
    host: BASE,
  };
}

