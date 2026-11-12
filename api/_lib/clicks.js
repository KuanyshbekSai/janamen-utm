// Запись клика в Supabase. Пока миграция (колонка click_id) не применена — пишем без неё.
import crypto from 'crypto';

export function newClickId() {
  return crypto.randomBytes(9).toString('base64url'); // 12 символов, достаточно уникально
}

export function cleanClickId(v) {
  const s = String(v || '').trim();
  return /^[A-Za-z0-9_-]{4,64}$/.test(s) ? s : null;
}

export async function insertClick(supabaseUrl, key, row) {
  const post = (r) => fetch(`${supabaseUrl}/rest/v1/clicks`, {
    method: 'POST',
    headers: {
      'apikey': key,
      'Authorization': `Bearer ${key}`,
      'Content-Type': 'application/json',
      'Prefer': 'return=minimal'
    },
    body: JSON.stringify([r])
  });
  let res = await post(row);
  if (!res.ok && 'click_id' in row) {
    const text = await res.text().catch(() => '');
    if (text.includes('click_id')) {
      const { click_id, ...legacy } = row;
      res = await post(legacy);
    }
  }
  return res;
}
