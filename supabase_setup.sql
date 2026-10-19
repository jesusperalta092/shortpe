-- ==========================================================
-- DramaPe - Esquema y Actualización de Analytics en Supabase
-- Ejecuta este script en el SQL Editor de tu Dashboard de Supabase:
-- https://supabase.com/dashboard/project/fpfvheperlxkbbratiqe/sql
-- ==========================================================

-- 1. Tabla Principal de Eventos de Analytics
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

-- 2. Nuevas Columnas para Geolocalización Avanzada y Telemetría de Anuncios
ALTER TABLE public.analytics_events
  ADD COLUMN IF NOT EXISTS city TEXT,
  ADD COLUMN IF NOT EXISTS region TEXT,
  ADD COLUMN IF NOT EXISTS country_name TEXT,
  ADD COLUMN IF NOT EXISTS network TEXT,
  ADD COLUMN IF NOT EXISTS ad_step INTEGER DEFAULT 1,
  ADD COLUMN IF NOT EXISTS os TEXT,
  ADD COLUMN IF NOT EXISTS browser TEXT;

-- 3. Índices de Alto Rendimiento para Consultas Rápidas en el Panel Admin
CREATE INDEX IF NOT EXISTS idx_analytics_timestamp ON public.analytics_events(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_analytics_event_type ON public.analytics_events(event_type);
CREATE INDEX IF NOT EXISTS idx_analytics_date_str ON public.analytics_events(date_str);
CREATE INDEX IF NOT EXISTS idx_analytics_slug ON public.analytics_events(slug);
CREATE INDEX IF NOT EXISTS idx_analytics_ad_events ON public.analytics_events(event_type, date_str);
CREATE INDEX IF NOT EXISTS idx_analytics_country ON public.analytics_events(country);
CREATE INDEX IF NOT EXISTS idx_analytics_city ON public.analytics_events(city);

-- 4. Seguridad de Nivel de Fila (RLS) y Políticas de Acceso
ALTER TABLE public.analytics_events ENABLE ROW LEVEL SECURITY;

DO $$ 
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_policies 
    WHERE tablename = 'analytics_events' AND policyname = 'Allow service role full access'
  ) THEN
    CREATE POLICY "Allow service role full access" 
    ON public.analytics_events 
    FOR ALL 
    TO service_role 
    USING (true) 
    WITH CHECK (true);
  END IF;
  
  IF NOT EXISTS (
    SELECT 1 FROM pg_policies 
    WHERE tablename = 'analytics_events' AND policyname = 'Allow anon insert'
  ) THEN
    CREATE POLICY "Allow anon insert" 
    ON public.analytics_events 
    FOR INSERT 
    TO anon 
    WITH CHECK (true);
  END IF;
END $$;
