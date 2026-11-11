import { createClient } from '@supabase/supabase-js';

const SUPABASE_URL = process.env.SUPABASE_URL || 'https://upeqrwqhdnmccyymugej.supabase.co';
const SUPABASE_KEY = process.env.SUPABASE_SERVICE_KEY || process.env.SUPABASE_ANON_KEY || 'sb_publishable_bhEfs-Ej7u-1_MAytAp-eg_bvEnTuwi';

export default async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, DELETE, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');

  if (req.method === 'OPTIONS') return res.status(200).end();

  const supabase = createClient(SUPABASE_URL, SUPABASE_KEY);

  // 1. ПОЛУЧЕНИЕ СПИСКА ДОБАВЛЕННЫХ БЛОГЕРОВ
  if (req.method === 'GET') {
    try {
      const { data, error } = await supabase
        .from('bloggers')
        .select('*')
        .order('created_at', { ascending: false });

      if (error) {
        // Если таблицы еще нет в Supabase, отдаем пустой массив без ошибки
        return res.status(200).json({ ok: true, bloggers: [], tableMissing: true });
      }

      return res.status(200).json({ ok: true, bloggers: data || [] });
    } catch (err) {
      return res.status(200).json({ ok: true, bloggers: [], error: err.message });
    }
  }

  // 2. ДОБАВЛЕНИЕ / ОБНОВЛЕНИЕ БЛОГЕРА
  if (req.method === 'POST') {
    try {
      let body = typeof req.body === 'string' ? JSON.parse(req.body) : req.body;
      const {
        handle,
        name,
        manager = 'mpb1',
        subs = '—',
        city = '—',
        profile_url,
        paid_cash = 0,
        delivery_cost = 0,
        barter_man = 0,
        barter_woman = 0,
        barter_omega = 0,
        barter_aojiru = 0,
        notes = ''
      } = body;

      if (!handle) {
        return res.status(400).json({ ok: false, error: 'Handle is required' });
      }

      const cleanHandle = String(handle).replace(/^@/, '').trim().toLowerCase();
      const utmUrl = `https://janamen1.kz/influence?utm_source=${cleanHandle}&utm_medium=${manager}&utm_campaign=ugc_barter&utm_content=reels_stories`;
      const pUrl = profile_url || `https://instagram.com/${cleanHandle}`;

      const bloggerPayload = {
        handle: cleanHandle,
        name: name || cleanHandle,
        manager,
        subs,
        city,
        profile_url: pUrl,
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

      if (error) {
        return res.status(200).json({ ok: true, fallback: true, blogger: bloggerPayload, warning: error.message });
      }

      return res.status(200).json({ ok: true, blogger: data?.[0] || bloggerPayload });
    } catch (err) {
      return res.status(500).json({ ok: false, error: err.message });
    }
  }

  // 3. УДАЛЕНИЕ БЛОГЕРА
  if (req.method === 'DELETE') {
    try {
      const handle = req.query.handle || req.body?.handle;
      if (!handle) return res.status(400).json({ ok: false, error: 'Handle required' });

      const cleanHandle = String(handle).replace(/^@/, '').trim().toLowerCase();
      const { error } = await supabase
        .from('bloggers')
        .delete()
        .eq('handle', cleanHandle);

      if (error) {
        return res.status(200).json({ ok: true, fallback: true, warning: error.message });
      }

      return res.status(200).json({ ok: true, deleted: cleanHandle });
    } catch (err) {
      return res.status(500).json({ ok: false, error: err.message });
    }
  }

  return res.status(405).json({ error: 'Method not allowed' });
}
