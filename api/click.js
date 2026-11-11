import { createClient } from '@supabase/supabase-js';
import crypto from 'crypto';

const supabaseUrl = process.env.SUPABASE_URL || 'https://upeqrwqhdnmccyymugej.supabase.co';
const supabaseKey = process.env.SUPABASE_SERVICE_KEY || process.env.SUPABASE_ANON_KEY || 'sb_publishable_bhEfs-Ej7u-1_MAytAp-eg_bvEnTuwi';
const supabase = createClient(supabaseUrl, supabaseKey);

export default async function handler(req, res) {
  // Разрешаем CORS с любого домена (janamen1.kz, janamenhealth.kz, tilda)
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }

  try {
    let payload = {};
    if (req.method === 'POST') {
      try {
        payload = typeof req.body === 'string' ? JSON.parse(req.body) : (req.body || {});
      } catch (e) {
        payload = req.body || {};
      }
    } else {
      payload = req.query || {};
    }

    const blogger = (payload.blogger || payload.utm_content || payload.cnt || '').trim();
    const source = (payload.source || payload.utm_source || payload.src || 'direct').trim();
    const medium = (payload.medium || payload.utm_medium || payload.med || 'none').trim();
    const campaign = (payload.campaign || payload.utm_campaign || payload.cmp || 'none').trim();
    const term = (payload.term || payload.utm_term || payload.trm || 'none').trim();
    const page = (payload.page || payload.landing_page || '/').trim();

    const ip = req.headers['x-forwarded-for'] || req.socket?.remoteAddress || '';
    const ipHash = ip ? crypto.createHash('md5').update(ip).digest('hex').slice(0, 16) : null;
    const userAgent = (req.headers['user-agent'] || '').slice(0, 255);
    const referrer = (payload.referrer || req.headers['referer'] || 'direct').slice(0, 255);

    // Записываем в Supabase
    const { error } = await supabase.from('clicks').insert([{
      utm_source: source,
      utm_medium: medium,
      utm_campaign: campaign,
      utm_content: blogger || 'none',
      utm_term: term || 'none',
      landing_page: page,
      blogger: blogger || 'none',
      referrer: referrer,
      user_agent: userAgent,
      ip_hash: ipHash,
      created_at: new Date().toISOString()
    }]);

    if (error) {
      console.warn('Supabase insert click error:', error.message);
      return res.status(200).json({ ok: false, error: error.message });
    }

    return res.status(200).json({ ok: true, timestamp: new Date().toISOString() });
  } catch (err) {
    console.error('Click error:', err);
    return res.status(200).json({ ok: false, error: err.message });
  }
}
