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

-- Отключение RLS для прямого доступа через API
ALTER TABLE public.bloggers DISABLE ROW LEVEL SECURITY;

-- ==============================================================================
-- 2. ТАБЛИЦА ПОЛЬЗОВАТЕЛЕЙ И ДОСТУПОВ (RBAC)
-- ==============================================================================
CREATE TABLE IF NOT EXISTS public.app_users (
  id SERIAL PRIMARY KEY,
  email TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL,
  name TEXT NOT NULL,
  role TEXT DEFAULT 'manager',          -- superadmin, manager, fan, viewer
  status TEXT DEFAULT 'active',         -- active, pending, blocked
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Отключение RLS для прямого доступа через API
ALTER TABLE public.app_users DISABLE ROW LEVEL SECURITY;

-- Главный аккаунт владельца (по умолчанию)
INSERT INTO public.app_users (email, password, name, role, status)
VALUES ('k.saidullayev@janamen.kz', 'janamen2026', 'Куанышбек Сайдуллаев', 'superadmin', 'active')
ON CONFLICT (email) DO NOTHING;

