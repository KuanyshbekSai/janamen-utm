// Vercel Serverless Function: Webhook от AmoCRM -> Supabase
import { createClient } from '@supabase/supabase-js';

const SUPABASE_URL = process.env.SUPABASE_URL || 'https://upeqrwqhdnmccyymugej.supabase.co';
const SUPABASE_KEY = process.env.SUPABASE_SERVICE_KEY;
const AMOCRM_TOKEN = process.env.AMOCRM_TOKEN;

function cleanStr(val, def = 'none') {
  if (!val) return def;
  const s = String(val).trim();
  return s || def;
}

export default async function handler(req, res) {
  if (req.method !== 'POST' && req.method !== 'GET') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  // Ответ на GET/Ping проверку от AmoCRM
  if (req.method === 'GET') {
    return res.status(200).json({ status: 'ok', service: 'Jana Men AmoCRM Webhook' });
  }

  if (!SUPABASE_KEY) {
    return res.status(500).json({ error: 'SUPABASE_SERVICE_KEY not configured' });
  }

  const supabase = createClient(SUPABASE_URL, SUPABASE_KEY);

  try {
    const body = req.body || {};
    
    // Сбор ID сделок из вебхука AmoCRM
    const leadIds = new Set();
    const parseIds = (obj) => {
      if (!obj || typeof obj !== 'object') return;
      for (const k in obj) {
        if (k === 'id' && !isNaN(obj[k])) leadIds.add(Number(obj[k]));
        else parseIds(obj[k]);
      }
    };
    parseIds(body.leads);

    if (leadIds.size === 0) {
      return res.status(200).json({ status: 'ok', message: 'No leads found in payload' });
    }

    const updatedRows = [];
    for (const id of leadIds) {
      const amoRes = await fetch(`https://janamen.amocrm.ru/api/v4/leads/${id}`, {
        headers: { 'Authorization': `Bearer ${AMOCRM_TOKEN}` }
      });
      if (!amoRes.ok) continue;

      const d = await amoRes.json();
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

      const row = {
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

      updatedRows.push(row);
    }

    if (updatedRows.length > 0) {
      const { error } = await supabase.from('deals').upsert(updatedRows, { onConflict: 'id' });
      if (error) throw error;
    }

    return res.status(200).json({ status: 'ok', processed: updatedRows.length });
  } catch (err) {
    console.error('Webhook Error:', err);
    return res.status(500).json({ error: err.message });
  }
}
