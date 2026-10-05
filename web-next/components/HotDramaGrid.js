'use client';
import CatalogGrid from './CatalogGrid';

export default function HotDramaGrid({ initial }) {
  return <CatalogGrid initial={initial} apiPath="/api/hotdrama" label="HotDrama" fireTag={true} />;
}
