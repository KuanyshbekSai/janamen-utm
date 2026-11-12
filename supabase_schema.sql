-- ==============================================================================
-- 1. ТАБЛИЦА БЛОГЕРОВ INFLUENCE (С УЧЕТОМ ГОНОРАРА, ДОСТАВКИ И БАРТЕРА ВИТАМИНОВ)
-- ==============================================================================
CREATE TABLE IF NOT EXISTS public.bloggers (
  id SERIAL PRIMARY KEY,
  handle TEXT UNIQUE NOT NULL,
  name TEXT,
  manager TEXT NOT NULL DEFAULT 'mpb1',
  subs TEXT DEFAULT '—',
  city TEXT DEFAULT '—',
  profile_url TEXT,
  utm_url TEXT,
  paid_cash NUMERIC DEFAULT 0,          -- Оплата деньгами (₸)
  delivery_cost NUMERIC DEFAULT 0,      -- Оплата за доставку (₸)
  barter_man INTEGER DEFAULT 0,         -- Комплекс Мужской (шт.)
  barter_woman INTEGER DEFAULT 0,       -- Комплекс Женский (шт.)
  barter_omega INTEGER DEFAULT 0,       -- Омега-3 (шт.)
  barter_aojiru INTEGER DEFAULT 0,      -- Аодзиру (шт.)
  notes TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ==============================================================================
-- 2. ТАБЛИЦА ПОЛЬЗОВАТЕЛЕЙ И ДОСТУПОВ (RBAC)
-- Пароли хранятся только в виде scrypt-хэша (формат "scrypt$<salt>$<hash>").
-- Пользователей создаёт scripts/set-user-password.mjs или владелец в портале.
-- ==============================================================================
CREATE TABLE IF NOT EXISTS public.app_users (
  id SERIAL PRIMARY KEY,
  email TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL,
  name TEXT NOT NULL,
  role TEXT DEFAULT 'manager',          -- superadmin, head_marketing, crm_integrator, manager, fan, viewer
  manager_code TEXT,                    -- mpb1..mpb4 для менеджеров блогеров
  status TEXT DEFAULT 'active',         -- active, pending, blocked
  created_at TIMESTAMPTZ DEFAULT NOW()
);

ALTER TABLE public.app_users ADD COLUMN IF NOT EXISTS manager_code TEXT;

-- ==============================================================================
-- 3. ДОСТУП: RLS ВКЛЮЧЕН, ПОЛИТИК ДЛЯ anon НЕТ.
-- Серверные функции Vercel работают через SUPABASE_SERVICE_KEY и обходят RLS.
-- Публичный ключ из портала больше не может читать пароли и бюджеты блогеров.
-- ==============================================================================
ALTER TABLE public.bloggers ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.app_users ENABLE ROW LEVEL SECURITY;
REVOKE ALL ON public.bloggers FROM anon, authenticated;
REVOKE ALL ON public.app_users FROM anon, authenticated;

-- Старые пароли открытым текстом, опубликованные в коде, сбрасываются:
-- вход с ними заблокирован сервером, задайте новые через scripts/set-user-password.mjs.
