import './globals.css';

const SITE_URL = process.env.SITE_URL || 'https://dramape.com';

export const metadata = {
  metadataBase: new URL(SITE_URL),
  title: {
    default: 'DramaPe — Dramas Cortos, Doramas y Miniseries en Español HD',
    template: '%s | DramaPe',
  },
  description:
    'Mira dramas cortos, doramas, miniseries y novelas cortas completas en español gratis en HD. Transmisión rápida sin cortes para Perú, México, Colombia, Argentina, EE.UU. y toda Latinoamérica.',
  applicationName: 'DramaPe',
  keywords: [
    'DramaPe',
    'Drama Pe',
    'dramas cortos',
    'doramas en español',
    'miniseries en español',
    'novelas cortas gratis',
    'doramas peru',
    'dramas coreanos en español',
    'dramas chinos subtitulados',
    'ver dramas online gratis',
    'reelshort en español',
    'dramabox gratis',
    'shortmax en español',
    'hotdrama',
    'dramavibe',
  ],
  authors: [{ name: 'DramaPe Team', url: SITE_URL }],
  creator: 'DramaPe',
  publisher: 'DramaPe',
  category: 'Entertainment',
  formatDetection: {
    email: false,
    address: false,
    telephone: false,
  },
  alternates: {
    canonical: '/',
    languages: {
      'es-PE': '/',
      'es-MX': '/',
      'es-CO': '/',
      'es-AR': '/',
      'es-CL': '/',
      'es-US': '/',
      'es-ES': '/',
      'es-419': '/',
      'x-default': '/',
    },
  },
  openGraph: {
    type: 'website',
    siteName: 'DramaPe',
    title: 'DramaPe — Dramas Cortos, Doramas y Miniseries en Español HD',
    description:
      'Miles de dramas cortos, doramas y miniseries en español completos gratis en HD. Estrenos diarios para toda Latinoamérica y el mundo.',
    url: SITE_URL,
    locale: 'es_PE',
    alternateLocale: ['es_MX', 'es_CO', 'es_AR', 'es_CL', 'es_US', 'es_ES', 'es_419'],
    images: [
      {
        url: '/img/og-banner.jpg',
        width: 1200,
        height: 630,
        alt: 'DramaPe — Plataforma de Streaming de Dramas Cortos en Español',
      },
    ],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'DramaPe — Dramas Cortos y Miniseries en Español HD',
    description:
      'Miles de dramas cortos, doramas y miniseries en español completos gratis en HD.',
    creator: '@DramaPe',
    images: ['/img/og-banner.jpg'],
  },
  robots: {
    index: true,
    follow: true,
    nocache: false,
    googleBot: {
      index: true,
      follow: true,
      'max-video-preview': -1,
      'max-image-preview': 'large',
      'max-snippet': -1,
    },
  },
  other: {
    'geo.region': 'PE',
    'geo.placename': 'Perú',
    'geo.position': '-12.046374;-77.042793',
    'ICBM': '-12.046374, -77.042793',
    'language': 'es-PE',
    'content-language': 'es-PE, es-MX, es-CO, es-AR, es-CL, es-US, es-ES, es-419',
    'distribution': 'Global',
    'rating': 'General',
    'theme-color': '#e50914',
  },
};

export const viewport = {
  width: 'device-width',
  initialScale: 1,
  maximumScale: 5,
  themeColor: '#e50914',
};

export default function RootLayout({ children }) {
  const jsonLdWebsite = {
    '@context': 'https://schema.org',
    '@type': 'WebSite',
    name: 'DramaPe',
    alternateName: ['Drama Pe', 'DramaPe Streaming', 'DramaPe Dramas Cortos'],
    url: SITE_URL,
    inLanguage: 'es',
    description:
      'Plataforma líder de streaming de dramas cortos, doramas y miniseries en español latino para Perú y Latinoamérica.',
    potentialAction: {
      '@type': 'SearchAction',
      target: {
        '@type': 'EntryPoint',
        urlTemplate: `${SITE_URL}/buscar?q={search_term_string}`,
      },
      'query-input': 'required name=search_term_string',
    },
  };

  const jsonLdOrg = {
    '@context': 'https://schema.org',
    '@type': 'Organization',
    name: 'DramaPe',
    url: SITE_URL,
    logo: `${SITE_URL}/favicon.ico`,
    sameAs: [],
  };

  return (
    <html lang="es-PE">
      <body>
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLdWebsite) }}
        />
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLdOrg) }}
        />
        {children}
      </body>
    </html>
  );
}

