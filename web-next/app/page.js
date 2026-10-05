import { Suspense } from 'react';
import { getCatalog, getHotDrama, getDramaVibe, groupBySection } from '../lib/api';
import HomeClient from '../components/HomeClient';

export const dynamic = 'force-dynamic';

export default async function Home() {
  const [cat, hotdramaItems, dramavibeItems] = await Promise.all([
    getCatalog(),
    getHotDrama(24),
    getDramaVibe(24)
  ]);
  
  const sections = groupBySection(cat);
    
  return (
    <Suspense fallback={<div style={{ padding: 40, color: '#888' }}>Cargando…</div>}>
      <HomeClient 
        catalog={cat} 
        sections={sections} 
        hotdramaItems={hotdramaItems} 
        dramavibeItems={dramavibeItems}
      />
    </Suspense>
  );
}
