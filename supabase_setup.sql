-- ==========================================================
-- DramaPe - Esquema de Base de Datos para Analytics (Supabase)
-- Ejecuta este script en el SQL Editor de tu Dashboard de Supabase:
-- https://supabase.com/dashboard/project/fpfvheperlxkbbratiqe/sql
-- ==========================================================

CREATE TABLE IF NOT EXISTS public.analytics_events (
  id BIGSERIAL PRIMARY KEY,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  timestamp BIGINT NOT NULL,
  date_str TEXT NOT NULL,
  hour_str TEXT NOT NULL,
  event_type TEXT NOT NULL, -- 'pageview', 'video_play', 'ad_click'
  path TEXT,
  slug TEXT,
  ep TEXT,
  title TEXT,
  visitor_hash TEXT NOT NULL,
  device TEXT, -- 'mobile', 'tablet', 'desktop'
  referer TEXT,
  country TEXT DEFAULT 'PE'
);

-- Índices de alto rendimiento para consultas instantáneas en el panel
CREATE INDEX IF NOT EXISTS idx_analytics_timestamp ON public.analytics_events(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_analytics_event_type ON public.analytics_events(event_type);
CREATE INDEX IF NOT EXISTS idx_analytics_date_str ON public.analytics_events(date_str);
CREATE INDEX IF NOT EXISTS idx_analytics_slug ON public.analytics_events(slug);

-- Habilitar lectura y escritura segura vía Service Role y Anon
ALTER TABLE public.analytics_events ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow service role full access" 
ON public.analytics_events 
FOR ALL 
TO service_role 
USING (true) 
WITH CHECK (true);

CREATE POLICY "Allow anon insert" 
ON public.analytics_events 
FOR INSERT 
TO anon 
WITH CHECK (true);
