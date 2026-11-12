// Общие настройки портала, одинаковые у всех сотрудников:
//   fan_salaries — зарплаты фан-аккаунтов { fanId: сумма }
//   leads_plan   — план лидов { total, organika, influence, fan }
// Хранятся в таблице app_settings (см. supabase_migration_002.sql).
import { createClient } from '@supabase/supabase-js';

const SUPABASE_URL = process.env.SUPABASE_URL || 'https://upeqrwqhdnmccyymugej.supabase.co';
const SUPABASE_KEY = process.env.SUPABASE_SERVICE_KEY;
const ALLOWED_KEYS = ['fan_salaries', 'leads_plan'];

export default async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  res.setHeader('Cache-Control', 'no-store');
  if (req.method === 'OPTIONS') return res.status(200).end();
  if (!SUPABASE_KEY) return res.status(500).json({ ok: false, error: 'SUPABASE_SERVICE_KEY not configured' });

  const supabase = createClient(SUPABASE_URL, SUPABASE_KEY);

  if (req.method === 'GET') {
    const { data, error } = await supabase.from('app_settings').select('key, value, updated_at').in('key', ALLOWED_KEYS);
    if (error) return res.status(200).json({ ok: false, settings: {}, error: error.message });
    const settings = {};
    for (const r of data || []) settings[r.key] = r.value;
    return res.status(200).json({ ok: true, settings });
  }

  if (req.method === 'POST') {
    let body = req.body || {};
    if (typeof body === 'string') { try { body = JSON.parse(body); } catch (e) { body = {}; } }
    const { key, value } = body;
    if (!ALLOWED_KEYS.includes(key)) return res.status(400).json({ ok: false, error: 'Unknown setting' });
    if (value === null || typeof value !== 'object' || JSON.stringify(value).length > 20000) {
      return res.status(400).json({ ok: false, error: 'Invalid value' });
    }
    const { error } = await supabase.from('app_settings')
      .upsert({ key, value, updated_at: new Date().toISOString() }, { onConflict: 'key' });
    if (error) return res.status(500).json({ ok: false, error: error.message });
    return res.status(200).json({ ok: true });
  }

  return res.status(405).json({ ok: false, error: 'Method not allowed' });
}
