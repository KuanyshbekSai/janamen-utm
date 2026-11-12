// Vercel Serverless Function: подтяжка сделок из AmoCRM -> Supabase
// Забирает ВСЕ сделки, изменённые за последние N часов (постранично), а не «последние 200».
// Параметры:
//   ?hours=2        — окно в часах (по умолчанию 2, максимум 24*31)
//   ?from=<unix>    — начало окна как unix-время (вместо hours), для догрузки по частям
// Вызывается по расписанию из Google Apps Script и кнопкой «Синхронизировать» в портале.
import { createClient } from '@supabase/supabase-js';

const SUPABASE_URL = process.env.SUPABASE_URL || 'https://upeqrwqhdnmccyymugej.supabase.co';
const SUPABASE_KEY = process.env.SUPABASE_SERVICE_KEY;
const AMOCRM_TOKEN = process.env.AMOCRM_TOKEN;
const AMO_BASE = 'https://janamen.amocrm.ru/api/v4';

const PAGE_SIZE = 250;            // максимум AmoCRM за один запрос
const TIME_BUDGET_MS = 8000;      // запас под ограничение времени функции Vercel
const DEFAULT_HOURS = 2;
const MAX_HOURS = 24 * 31;

function cleanStr(val, def = 'none') {
  if (!val) return def;
  const s = String(val).trim();
  return s || def;
}

// Превращает сделку AmoCRM в строку таблицы deals (логика разбора UTM без изменений)
function mapLead(d) {
  const cf = {};
  for (const c of (d.custom_fields_values || [])) {
    if (c.values && c.values.length > 0) cf[c.field_id] = String(c.values[0].value).trim();
  }

  const page = cf[849891] || cf[833007] || '';
  const q = {};
  if (page.includes('?')) {
    const queryStr = page.split('?')[1].split('#')[0];
    for (const pair of queryStr.split('&')) {
      if (pair.includes('=')) {
        const [k, v] = pair.split('=');
        if (k.toLowerCase().startsWith('utm_')) {
          try { q[k.toLowerCase()] = decodeURIComponent(v.replace(/\+/g, ' ')).trim(); } catch (_) { q[k.toLowerCase()] = v; }
        }
      }
    }
  }

  const g = (fid, key) => (cf[fid] || q[key] || '').trim();
  let src = g(679639, 'utm_source') || 'direct/none';
  let med = g(679635, 'utm_medium') || 'none';
  let cmp = g(679637, 'utm_campaign') || 'none';
  let cnt = g(679633, 'utm_content') || 'none';
  let trm = g(679641, 'utm_term') || 'none';
  let uid = g(833139, 'utm_id') || 'none';

  const tags = (d._embedded?.tags || []).map(t => t.name);
  const isWa = tags.some(t => t.includes('9828')) || page.toLowerCase().includes('iwa-9828') || page.toLowerCase().includes('9828');

  let cleanUrl = page.replace(/^https?:\/\//i, '').replace(/^www\./i, '').split('?')[0].split('#')[0];
  let path = '/';
  if (cleanUrl.includes('/')) {
    path = '/' + cleanUrl.split('/').slice(1).join('/');
  }

  if (isWa) {
    med = 'Айтым Берикович - органика';
    if (!src || src === 'direct/none') src = 'whatsapp';
    if (!cmp || cmp === 'none') cmp = 'iwa_9828';
    path = '/iwa-9828';
  }

  return {
    id: d.id,
    name: cleanStr(d.name, 'Без названия').slice(0, 255),
    created_at: d.created_at ? new Date(d.created_at * 1000).toISOString() : null,
    closed_at: d.closed_at ? new Date(d.closed_at * 1000).toISOString() : null,
    status_id: d.status_id || 0,
    pipeline_id: d.pipeline_id || 0,
    price: Number(d.price || 0),
    is_won: (d.status_id === 142),
    is_lost: (d.status_id === 143),
    utm_source: cleanStr(src, 'direct/none'),
    utm_medium: cleanStr(med, 'none'),
    utm_campaign: cleanStr(cmp, 'none'),
    utm_content: cleanStr(cnt, 'none'),
    utm_term: cleanStr(trm, 'none'),
    utm_id: cleanStr(uid, 'none'),
    landing_page: cleanStr(path, '/'),
    referrer: cleanStr(page, 'none').slice(0, 500),
    city: cleanStr(cf[855175] || cf[679621] || 'none', 'none').slice(0, 100),
    tags: tags.slice(0, 20),
    updated_at: new Date().toISOString()
  };
}

export default async function handler(req, res) {
  if (!SUPABASE_KEY || !AMOCRM_TOKEN) {
    return res.status(500).json({ error: 'Config missing: SUPABASE_SERVICE_KEY or AMOCRM_TOKEN' });
  }

  const supabase = createClient(SUPABASE_URL, SUPABASE_KEY);
  const t0 = Date.now();
  const nowSec = Math.floor(t0 / 1000);

  // Начало окна: ?from=<unix> или ?hours=N
  let fromSec;
  if (req.query.from && /^\d+$/.test(String(req.query.from))) {
    fromSec = Math.max(Number(req.query.from), nowSec - MAX_HOURS * 3600);
  } else {
    const hours = Math.min(Math.max(Number(req.query.hours) || DEFAULT_HOURS, 0.1), MAX_HOURS);
    fromSec = nowSec - Math.round(hours * 3600);
  }

  let synced = 0;
  let pages = 0;
  let lastUpdatedAt = fromSec;
  let complete = false;

  try {
    for (let page = 1; ; page++) {
      if (Date.now() - t0 > TIME_BUDGET_MS) break; // не успели — вернём курсор для продолжения

      const url = `${AMO_BASE}/leads?filter[updated_at][from]=${fromSec}&order[updated_at]=asc&limit=${PAGE_SIZE}&page=${page}`;
      const amoRes = await fetch(url, { headers: { 'Authorization': `Bearer ${AMOCRM_TOKEN}` } });

      if (amoRes.status === 204) { complete = true; break; } // AmoCRM: больше сделок нет
      if (!amoRes.ok) {
        return res.status(amoRes.status).json({ error: 'Failed to fetch from AmoCRM', page, synced });
      }

      const amoData = await amoRes.json();
      const leads = amoData._embedded?.leads || [];
      pages++;

      if (leads.length) {
        const rows = leads.map(mapLead);
        const { error } = await supabase.from('deals').upsert(rows, { onConflict: 'id' });
        if (error) throw error;
        synced += rows.length;
        lastUpdatedAt = Math.max(lastUpdatedAt, ...leads.map(l => l.updated_at || 0));
      }

      if (leads.length < PAGE_SIZE || !amoData._links?.next) { complete = true; break; }
    }

    return res.status(200).json({
      status: 'ok',
      synced,
      pages,
      complete,
      from: new Date(fromSec * 1000).toISOString(),
      // Если complete=false — вызовите ещё раз с ?from=<next_from>, чтобы догрузить остаток
      next_from: complete ? null : lastUpdatedAt,
      timestamp: new Date().toISOString()
    });
  } catch (err) {
    console.error('Sync Error:', err);
    return res.status(500).json({ error: err.message, synced });
  }
}
