'use client';
import CatalogGrid from './CatalogGrid';

export default function DramaTubeGrid({ initial }) {
  return <CatalogGrid initial={initial} apiPath="/api/dramatube" label="DramaTube" />;
}
