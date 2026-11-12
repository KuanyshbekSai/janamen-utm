import { createClient } from '@supabase/supabase-js';
import { getSupabaseConfig, requireUser, setCors, parseBody } from './_lib/auth.js';

const EDITOR_ROLES = ['superadmin', 'head_marketing', 'manager'];

export default async function handler(req, res) {
  setCors(res, 'GET, POST, DELETE, OPTIONS');
  if (req.method === 'OPTIONS') return res.status(200).end();

  const cfg = getSupabaseConfig();
  if (!cfg || !process.env.AUTH_SECRET) {
    return res.status(500).json({ ok: false, error: 'Сервер не настроен: нужны SUPABASE_URL, SUPABASE_SERVICE_KEY и AUTH_SECRET' });
  }
  const supabase = createClient(cfg.url, cfg.key);

  // Любое действие с базой блогеров (в ней суммы оплат) — только для вошедших пользователей
  const user = await requireUser(req, supabase);
  if (!user) return res.status(401).json({ ok: false, error: 'Требуется вход в систему' });

  // 1. СПИСОК БЛОГЕРОВ
  if (req.method === 'GET') {
    let query = supabase.from('bloggers').select('*').order('created_at', { ascending: false });
    if (user.role === 'manager') query = query.eq('manager', user.manager_code || '__none__');
    const { data, error } = await query;
    if (error) return res.status(200).json({ ok: true, bloggers: [], tableMissing: true });
    return res.status(200).json({ ok: true, bloggers: data || [] });
  }

  // 2. ДОБАВЛЕНИЕ / ОБНОВЛЕНИЕ БЛОГЕРА
  if (req.method === 'POST') {
    if (!EDITOR_ROLES.includes(user.role)) {
      return res.status(403).json({ ok: false, error: 'Недостаточно прав для изменения блогеров' });
    }
    const body = parseBody(req);
    const {
      handle, name, subs = '—', city = '—', profile_url,
      paid_cash = 0, delivery_cost = 0,
      barter_man = 0, barter_woman = 0, barter_omega = 0, barter_aojiru = 0,
      notes = ''
    } = body;
    let manager = body.manager || 'mpb1';

    if (!handle) return res.status(400).json({ ok: false, error: 'Handle is required' });
    if (!/^mpb\d+$/.test(manager)) return res.status(400).json({ ok: false, error: 'Недопустимый код менеджера' });

    const cleanHandle = String(handle).replace(/^@/, '').trim().toLowerCase();

    if (user.role === 'manager') {
      // Менеджер работает только со своими блогерами
      if (manager !== user.manager_code) {
        return res.status(403).json({ ok: false, error: 'Можно добавлять блогеров только в свой отдел' });
      }
      const { data: existing } = await supabase.from('bloggers').select('manager').eq('handle', cleanHandle).maybeSingle();
      if (existing && existing.manager !== user.manager_code) {
        return res.status(403).json({ ok: false, error: 'Этот блогер закреплён за другим менеджером' });
      }
    }

    const utmUrl = `https://janamen1.kz/influence?utm_source=${encodeURIComponent(cleanHandle)}&utm_medium=${manager}&utm_campaign=ugc_barter&utm_content=reels_stories`;
    const bloggerPayload = {
      handle: cleanHandle,
      name: name || cleanHandle,
      manager,
      subs,
      city,
      profile_url: profile_url || `https://instagram.com/${cleanHandle}`,
      utm_url: utmUrl,
      paid_cash: Number(paid_cash) || 0,
      delivery_cost: Number(delivery_cost) || 0,
      barter_man: Number(barter_man) || 0,
      barter_woman: Number(barter_woman) || 0,
      barter_omega: Number(barter_omega) || 0,
      barter_aojiru: Number(barter_aojiru) || 0,
      notes: notes || '',
      updated_at: new Date().toISOString()
    };

    const { data, error } = await supabase
      .from('bloggers')
      .upsert(bloggerPayload, { onConflict: 'handle' })
      .select();
    if (error) return res.status(500).json({ ok: false, error: 'Не удалось сохранить блогера' });
    return res.status(200).json({ ok: true, blogger: data?.[0] || bloggerPayload });
  }

  // 3. УДАЛЕНИЕ БЛОГЕРА — только владелец
  if (req.method === 'DELETE') {
    if (user.role !== 'superadmin') {
      return res.status(403).json({ ok: false, error: 'Доступ запрещен. Удалять записи может только владелец.' });
    }
    const body = parseBody(req);
    const handle = req.query.handle || body.handle;
    if (!handle) return res.status(400).json({ ok: false, error: 'Никнейм блогера обязателен' });

    const cleanHandle = String(handle).replace(/^@/, '').trim().toLowerCase();
    const { error } = await supabase.from('bloggers').delete().eq('handle', cleanHandle);
    if (error) return res.status(500).json({ ok: false, error: 'Не удалось удалить блогера' });
    return res.status(200).json({ ok: true, deleted: cleanHandle });
  }

  return res.status(405).json({ error: 'Method not allowed' });
}
