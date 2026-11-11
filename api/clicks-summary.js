import { createClient } from '@supabase/supabase-js';

const supabaseUrl = process.env.SUPABASE_URL || 'https://upeqrwqhdnmccyymugej.supabase.co';
const supabaseKey = process.env.SUPABASE_SERVICE_KEY || process.env.SUPABASE_ANON_KEY || 'sb_publishable_bhEfs-Ej7u-1_MAytAp-eg_bvEnTuwi';
const supabase = createClient(supabaseUrl, supabaseKey);

export default async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, OPTIONS');
  res.setHeader('Cache-Control', 'public, max-age=10, stale-while-revalidate=30');

  if (req.method === 'OPTIONS') return res.status(200).end();

  try {
    const { from, to } = req.query || {};

    let query = supabase
      .from('clicks')
      .select('utm_content, utm_source, utm_medium, landing_page, created_at')
      .order('created_at', { ascending: false })
      .limit(10000);

    if (from) query = query.gte('created_at', from);
    if (to) query = query.lte('created_at', to);

    const { data, error } = await query;
    if (error) {
      // Если таблица еще не создана, возвращаем пустой результат без падения
      return res.status(200).json({ ok: true, clicks: [], total: 0, byContent: {} });
    }

    const byContent = {};
    for (const c of (data || [])) {
      const cnt = c.utm_content || 'none';
      if (cnt !== 'none' && cnt !== '') {
        byContent[cnt] = (byContent[cnt] || 0) + 1;
      }
    }

    return res.status(200).json({
      ok: true,
      total: (data || []).length,
      byContent,
      clicks: data || []
    });
  } catch (err) {
    return res.status(200).json({ ok: true, clicks: [], total: 0, byContent: {}, error: err.message });
  }
}
