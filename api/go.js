import crypto from 'crypto';

const SUPABASE_URL = process.env.SUPABASE_URL || 'https://upeqrwqhdnmccyymugej.supabase.co';
const SUPABASE_KEY = process.env.SUPABASE_SERVICE_KEY || process.env.SUPABASE_ANON_KEY || 'sb_publishable_bhEfs-Ej7u-1_MAytAp-eg_bvEnTuwi';

export default async function handler(req, res) {
  try {
    const q = req.query || {};
    
    // Блогер / Креатив
    const blogger = (q.b || q.blogger || q.utm_content || q.cnt || '').trim();
    // Менеджер / Канал
    const medium = (q.m || q.med || q.utm_medium || 'influence').trim();
    // Площадка / Источник
    const source = (q.s || q.src || q.utm_source || 'instagram').trim();
    // Кампания
    const campaign = (q.c || q.cmp || q.utm_campaign || (blogger ? 'blogger_' + blogger : 'influence')).trim();
    const term = (q.t || q.trm || q.utm_term || '').trim();

    // Целевая страница
    let target = q.to || q.url || '';
    if (!target) {
      const pagePath = q.p || q.page || '/organika';
      const cleanPath = pagePath.startsWith('/') ? pagePath : '/' + pagePath;
      target = `https://janamen1.kz${cleanPath}`;
    }

    // Собираем итоговый URL с сохранением UTM для сайта и AmoCRM
    const urlObj = new URL(target, 'https://janamen1.kz');
    if (source) urlObj.searchParams.set('utm_source', source);
    if (medium) urlObj.searchParams.set('utm_medium', medium);
    if (campaign) urlObj.searchParams.set('utm_campaign', campaign);
    if (blogger) urlObj.searchParams.set('utm_content', blogger);
    if (term) urlObj.searchParams.set('utm_term', term);

    const finalUrl = urlObj.toString();

    // Определяем IP и хэшируем его для защиты приватности
    const ip = req.headers['x-forwarded-for'] || req.socket?.remoteAddress || '';
    const ipHash = ip ? crypto.createHash('md5').update(ip).digest('hex').slice(0, 16) : null;
    const userAgent = (req.headers['user-agent'] || '').slice(0, 255);
    const referrer = (req.headers['referer'] || req.headers['referrer'] || 'direct').slice(0, 255);

    // Записываем клик в Supabase REST API без блокировки
    fetch(`${SUPABASE_URL}/rest/v1/clicks`, {
      method: 'POST',
      headers: {
        'apikey': SUPABASE_KEY,
        'Authorization': `Bearer ${SUPABASE_KEY}`,
        'Content-Type': 'application/json',
        'Prefer': 'return=minimal'
      },
      body: JSON.stringify([{
        utm_source: source,
        utm_medium: medium,
        utm_campaign: campaign,
        utm_content: blogger || 'none',
        utm_term: term || 'none',
        landing_page: urlObj.pathname,
        blogger: blogger || 'none',
        referrer: referrer,
        user_agent: userAgent,
        ip_hash: ipHash,
        created_at: new Date().toISOString()
      }])
    }).catch(err => console.warn('Click log error:', err.message));

    // Мгновенный 307 Temporary Redirect на сайт
    res.setHeader('Location', finalUrl);
    res.setHeader('Cache-Control', 'no-store, no-cache, must-revalidate, proxy-revalidate');
    return res.status(307).end();
  } catch (err) {
    console.error('Redirect handler error:', err);
    res.setHeader('Location', 'https://janamen1.kz/organika');
    return res.status(302).end();
  }
}
