-- ==============================================================================
-- Миграция 002: общие настройки портала, атрибуция каналов и сквозной номер клика.
-- Выполнить один раз: Supabase → SQL Editor → вставить → Run. Повторный запуск безопасен.
-- ==============================================================================

-- 1. Общие настройки (зарплаты фан-аккаунтов, план лидов) — одинаковые у всех сотрудников
CREATE TABLE IF NOT EXISTS public.app_settings (
  key TEXT PRIMARY KEY,
  value JSONB NOT NULL,
  updated_at TIMESTAMPTZ DEFAULT NOW()
);
-- Читается и пишется только через /api/settings (серверный ключ)
ALTER TABLE public.app_settings ENABLE ROW LEVEL SECURITY;

-- 2. Канал отдела по сделке (блогер / фан-аккаунт / лид-магнит / SMM), считает /api/sync
ALTER TABLE public.deals ADD COLUMN IF NOT EXISTS attr JSONB;

-- 3. Сквозной номер клика: клик → заявка → продажа
ALTER TABLE public.deals ADD COLUMN IF NOT EXISTS click_id TEXT;
ALTER TABLE public.clicks ADD COLUMN IF NOT EXISTS click_id TEXT;
CREATE INDEX IF NOT EXISTS deals_click_id_idx ON public.deals (click_id);
CREATE INDEX IF NOT EXISTS clicks_click_id_idx ON public.clicks (click_id);

-- 4. Ускоряет догрузку свежих сделок в портал
CREATE INDEX IF NOT EXISTS deals_updated_at_idx ON public.deals (updated_at);
CREATE INDEX IF NOT EXISTS deals_created_at_idx ON public.deals (created_at);

-- Обновить кэш схемы API, чтобы новые колонки стали видны сразу
NOTIFY pgrst, 'reload schema';
