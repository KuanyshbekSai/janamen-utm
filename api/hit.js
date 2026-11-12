import crypto from 'crypto';
import { insertClick, cleanClickId } from './_lib/clicks.js';

const SUPABASE_URL = process.env.SUPABASE_URL || 'https://upeqrwqhdnmccyymugej.supabase.co';
const SUPABASE_KEY = process.env.SUPABASE_SERVICE_KEY || process.env.SUPABASE_ANON_KEY || 'sb_publishable_bhEfs-Ej7u-1_MAytAp-eg_bvEnTuwi';

export default async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') return res.status(200).end();

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

    const source = (payload.source || payload.utm_source || payload.src || 'direct').trim();
    const medium = (payload.medium || payload.utm_medium || payload.med || 'none').trim();
    const campaign = (payload.campaign || payload.utm_campaign || payload.cmp || 'none').trim();
    const term = (payload.term || payload.utm_term || payload.trm || 'none').trim();
    const content = (payload.content || payload.utm_content || payload.cnt || 'none').trim();
    const page = (payload.page || payload.landing_page || '/').trim();

    // Если medium это менеджер (mpb1..mpb4) или source это имя блогера
    let blogger = (payload.blogger || '').trim();
    if (!blogger) {
      if (medium.toLowerCase().startsWith('mpb') && source !== 'direct' && source !== 'instagram' && source !== 'tiktok') {
        blogger = source;
      } else if (content && !['none', 'reels_stories', 'stories', 'reels'].includes(content.toLowerCase())) {
        blogger = content;
      } else if (campaign && !['none', 'ugc_barter', 'leads'].includes(campaign.toLowerCase())) {
        blogger = campaign;
      } else {
        blogger = source;
      }
    }

    const ip = req.headers['x-forwarded-for'] || req.socket?.remoteAddress || '';
    const ipHash = ip ? crypto.createHash('md5').update(ip).digest('hex').slice(0, 16) : null;
    const userAgent = (req.headers['user-agent'] || '').slice(0, 255);
    const referrer = (payload.referrer || req.headers['referer'] || 'direct').slice(0, 255);

    // Сквозной номер клика: трекер Tilda передаёт его, чтобы связать клик с заявкой в AmoCRM.
    // dup=1 — клик уже записан короткой ссылкой /go, второй раз не считаем.
    const clickId = cleanClickId(payload.click_id || payload.jm_cid);
    const isDup = String(payload.dup || '') === '1';

    let r = { ok: true };
    if (!isDup) {
      r = await insertClick(SUPABASE_URL, SUPABASE_KEY, {
        utm_source: source,
        utm_medium: medium,
        utm_campaign: campaign,
        utm_content: content,
        utm_term: term,
        landing_page: page,
        blogger: blogger || 'none',
        referrer: referrer,
        user_agent: userAgent,
        ip_hash: ipHash,
        click_id: clickId,
        created_at: new Date().toISOString()
      });
    }

    const TRANSPARENT_1PX_GIF = Buffer.from('R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7', 'base64');
    if (req.method === 'GET') {
      res.setHeader('Content-Type', 'image/gif');
      res.setHeader('Cache-Control', 'no-store, no-cache, must-revalidate, proxy-revalidate, max-age=0');
      return res.status(200).send(TRANSPARENT_1PX_GIF);
    }

    return res.status(200).json({ ok: r.ok, blogger: blogger, timestamp: new Date().toISOString() });
  } catch (err) {
    return res.status(200).json({ ok: false, error: err.message });
  }
}
