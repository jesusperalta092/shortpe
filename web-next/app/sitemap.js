import { getCatalog } from '../lib/api';

const BASE = process.env.SITE_URL || 'https://dramape.com';

export default async function sitemap() {
  const cat = await getCatalog();
  const now = new Date();

  const sections = ['drama', 'dramashorts', 'dramavibe', 'hotdrama', 'dramatube'];

  const entries = [
    {
      url: BASE + '/',
      lastModified: now,
      changeFrequency: 'always',
      priority: 1.0,
    },
  ];

  for (const s of sections) {
    entries.push({
      url: BASE + '/seccion/' + s,
      lastModified: now,
      changeFrequency: 'daily',
      priority: 0.9,
    });
  }

  for (const d of cat) {
    entries.push({
      url: BASE + '/titulo/' + d.slug,
      lastModified: now,
      changeFrequency: 'weekly',
      priority: 0.8,
    });
  }

  return entries;
}

