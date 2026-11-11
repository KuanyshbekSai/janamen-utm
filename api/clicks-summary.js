const SUPABASE_URL = process.env.SUPABASE_URL || 'https://upeqrwqhdnmccyymugej.supabase.co';
const SUPABASE_KEY = process.env.SUPABASE_SERVICE_KEY || process.env.SUPABASE_ANON_KEY || 'sb_publishable_bhEfs-Ej7u-1_MAytAp-eg_bvEnTuwi';

export default async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, OPTIONS');
  res.setHeader('Cache-Control', 'public, max-age=5, stale-while-revalidate=15');

  if (req.method === 'OPTIONS') return res.status(200).end();

  try {
    const url = `${SUPABASE_URL}/rest/v1/clicks?select=utm_content,utm_source,utm_medium,utm_campaign,landing_page,blogger,created_at&order=created_at.desc&limit=10000`;
    
    const r = await fetch(url, {
      headers: {
        'apikey': SUPABASE_KEY,
        'Authorization': `Bearer ${SUPABASE_KEY}`
      }
    });

    if (!r.ok) {
      // Таблица еще не создана или пустая
      return res.status(200).json({ ok: true, clicks: [], total: 0, byContent: {}, byCampaign: {}, byBlogger: {}, bySource: {} });
    }

    const data = await r.json();
    const byContent = {};
    const byMedium = {};
    const byPage = {};
    const bySource = {};
    const byCampaign = {};
    const byBlogger = {};

    for (const c of (data || [])) {
      const cnt = (c.utm_content || '').trim();
      const med = (c.utm_medium || '').trim();
      const p = (c.landing_page || '').trim();
      const src = (c.utm_source || '').trim();
      const cmp = (c.utm_campaign || '').trim();
      const blg = (c.blogger || '').trim();

      if (cnt && cnt !== 'none') byContent[cnt] = (byContent[cnt] || 0) + 1;
      if (med && med !== 'none') byMedium[med] = (byMedium[med] || 0) + 1;
      if (p && p !== 'none') byPage[p] = (byPage[p] || 0) + 1;
      if (src && src !== 'none') bySource[src] = (bySource[src] || 0) + 1;
      if (cmp && cmp !== 'none') byCampaign[cmp] = (byCampaign[cmp] || 0) + 1;
      if (blg && blg !== 'none') byBlogger[blg] = (byBlogger[blg] || 0) + 1;
    }

    return res.status(200).json({
      ok: true,
      total: (data || []).length,
      byContent,
      byMedium,
      byPage,
      bySource,
      byCampaign,
      byBlogger,
      clicks: data || []
    });
  } catch (err) {
    return res.status(200).json({ ok: true, clicks: [], total: 0, byContent: {}, byBlogger: {}, error: err.message });
  }
}
