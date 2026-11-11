const SUPABASE_URL = process.env.SUPABASE_URL || 'https://upeqrwqhdnmccyymugej.supabase.co';
const SUPABASE_KEY = process.env.SUPABASE_SERVICE_KEY || process.env.SUPABASE_ANON_KEY || 'sb_publishable_bhEfs-Ej7u-1_MAytAp-eg_bvEnTuwi';

export default async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, OPTIONS');
  res.setHeader('Cache-Control', 'public, max-age=5, stale-while-revalidate=15');

  if (req.method === 'OPTIONS') return res.status(200).end();

  try {
    const url = `${SUPABASE_URL}/rest/v1/clicks?select=utm_content,utm_source,utm_medium,landing_page,created_at&order=created_at.desc&limit=10000`;
    
    const r = await fetch(url, {
      headers: {
        'apikey': SUPABASE_KEY,
        'Authorization': `Bearer ${SUPABASE_KEY}`
      }
    });

    if (!r.ok) {
      // Таблица еще не создана или пустая
      return res.status(200).json({ ok: true, clicks: [], total: 0, byContent: {} });
    }

    const data = await r.json();
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
