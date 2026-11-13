import crypto from 'crypto';
import { insertClick, newClickId } from './_lib/clicks.js';

const SUPABASE_URL = process.env.SUPABASE_URL || 'https://upeqrwqhdnmccyymugej.supabase.co';
const SUPABASE_KEY = process.env.SUPABASE_SERVICE_KEY || process.env.SUPABASE_ANON_KEY || 'sb_publishable_bhEfs-Ej7u-1_MAytAp-eg_bvEnTuwi';

export default async function handler(req, res) {
  try {
    const q = req.query || {};
    
    // Целевая страница: ?to=<полный адрес> (ссылки лид-магнитов) или ?p=/путь на janamen1.kz
    let target = q.to || q.url || '';
    if (!target) {
      const pagePath = q.p || q.page || '/organika';
      const cleanPath = pagePath.startsWith('/') ? pagePath : '/' + pagePath;
      target = `https://janamen1.kz${cleanPath}`;
    }
    let urlObj = new URL(target, 'https://janamen1.kz');
    // Перенаправляем только на свои сайты — иначе ссылку можно использовать для фишинга
    if (!/(^|\.)janamen(1|health)?\.kz$/i.test(urlObj.hostname)) urlObj = new URL('https://janamen1.kz/organika');
    const has = (k) => (urlObj.searchParams.get(k) || '').trim();

    // UTM: явный параметр короткой ссылки > уже есть в адресе ?to= > значение по умолчанию
    const pick = (keys, fromUrl, def) => {
      for (const k of keys) if (q[k] && String(q[k]).trim()) return String(q[k]).trim();
      return has(fromUrl) || def;
    };
    // Блогер / Креатив
    const blogger = pick(['b', 'blogger', 'utm_content', 'cnt'], 'utm_content', '');
    // Менеджер / Канал
    const medium = pick(['m', 'med', 'utm_medium'], 'utm_medium', 'influence');
    // Площадка / Источник
    const source = pick(['s', 'src', 'utm_source'], 'utm_source', 'instagram');
    // Кампания
    const campaign = pick(['c', 'cmp', 'utm_campaign'], 'utm_campaign', blogger ? 'blogger_' + blogger : 'influence');
    const term = pick(['t', 'trm', 'utm_term'], 'utm_term', '');

    // Собираем итоговый URL с сохранением UTM для сайта и AmoCRM
    if (source) urlObj.searchParams.set('utm_source', source);
    if (medium) urlObj.searchParams.set('utm_medium', medium);
    if (campaign) urlObj.searchParams.set('utm_campaign', campaign);
    if (blogger) urlObj.searchParams.set('utm_content', blogger);
    if (term) urlObj.searchParams.set('utm_term', term);

    // Сквозной номер клика: уходит на сайт в ?jm_cid=, трекер Tilda кладёт его в скрытое поле формы,
    // и заявка в AmoCRM связывается с этим кликом
    const clickId = newClickId();
    urlObj.searchParams.set('jm_cid', clickId);

    const finalUrl = urlObj.toString();

    // Определяем IP и хэшируем его для защиты приватности
    const ip = req.headers['x-forwarded-for'] || req.socket?.remoteAddress || '';
    const ipHash = ip ? crypto.createHash('md5').update(ip).digest('hex').slice(0, 16) : null;
    const userAgent = (req.headers['user-agent'] || '').slice(0, 255);
    const referrer = (req.headers['referer'] || req.headers['referrer'] || 'direct').slice(0, 255);

    // Записываем клик (ждём запись: после ответа функция Vercel может быть остановлена)
    await insertClick(SUPABASE_URL, SUPABASE_KEY, {
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
      click_id: clickId,
      created_at: new Date().toISOString()
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
