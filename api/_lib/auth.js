// Общие помощники для серверных функций: конфиг Supabase, хэширование паролей и подписанные токены.
// Файлы в папках, начинающихся с "_", Vercel не публикует как отдельные эндпоинты.
import crypto from 'crypto';

export const ROLES = ['superadmin', 'head_marketing', 'crm_integrator', 'manager', 'fan', 'viewer'];
const TOKEN_TTL_SEC = 7 * 24 * 60 * 60; // 7 дней
// Пароли, которые были опубликованы в коде. Вход с ними запрещён — нужно задать новый.
const LEAKED_PASSWORDS = new Set(['janamen2026', 'admin', '123456']);

export function getSupabaseConfig() {
  const url = process.env.SUPABASE_URL;
  const key = process.env.SUPABASE_SERVICE_KEY;
  if (!url || !key) return null;
  return { url, key };
}

function authSecret() {
  return process.env.AUTH_SECRET || null;
}

// ---------- Пароли (scrypt) ----------
export function hashPassword(password) {
  const salt = crypto.randomBytes(16);
  const hash = crypto.scryptSync(password, salt, 64);
  return `scrypt$${salt.toString('base64')}$${hash.toString('base64')}`;
}

// Возвращает { ok, needsRehash, leaked }
export function verifyPassword(password, stored) {
  if (!stored || !password) return { ok: false };
  if (stored.startsWith('scrypt$')) {
    const [, saltB64, hashB64] = stored.split('$');
    const expected = Buffer.from(hashB64, 'base64');
    const actual = crypto.scryptSync(password, Buffer.from(saltB64, 'base64'), expected.length);
    return { ok: crypto.timingSafeEqual(expected, actual) };
  }
  // Старые записи хранили пароль открытым текстом — сравниваем и просим перехэшировать.
  const a = Buffer.from(String(password));
  const b = Buffer.from(String(stored));
  const ok = a.length === b.length && crypto.timingSafeEqual(a, b);
  return { ok, needsRehash: ok, leaked: ok && LEAKED_PASSWORDS.has(password) };
}

// ---------- Токены (HMAC-SHA256) ----------
const b64u = (buf) => Buffer.from(buf).toString('base64url');

export function signToken(user) {
  const secret = authSecret();
  if (!secret) throw new Error('AUTH_SECRET не задан');
  const payload = {
    sub: user.email,
    role: user.role,
    mc: user.manager_code || null,
    exp: Math.floor(Date.now() / 1000) + TOKEN_TTL_SEC
  };
  const body = b64u(JSON.stringify(payload));
  const sig = b64u(crypto.createHmac('sha256', secret).update(body).digest());
  return `${body}.${sig}`;
}

export function verifyToken(token) {
  const secret = authSecret();
  if (!secret || !token || typeof token !== 'string') return null;
  const [body, sig] = token.split('.');
  if (!body || !sig) return null;
  const expected = crypto.createHmac('sha256', secret).update(body).digest();
  const given = Buffer.from(sig, 'base64url');
  if (given.length !== expected.length || !crypto.timingSafeEqual(given, expected)) return null;
  try {
    const payload = JSON.parse(Buffer.from(body, 'base64url').toString('utf8'));
    if (!payload.exp || payload.exp < Math.floor(Date.now() / 1000)) return null;
    return payload;
  } catch (e) {
    return null;
  }
}

export function bearer(req) {
  const h = req.headers['authorization'] || req.headers['Authorization'] || '';
  const m = /^Bearer\s+(.+)$/i.exec(h);
  return m ? m[1].trim() : null;
}

export function inferManagerCode(row) {
  if (row.manager_code) return row.manager_code;
  const e = (row.email || '').toLowerCase();
  if (e.includes('mpb1') || e.includes('anelzhan')) return 'mpb1';
  if (e.includes('mpb2') || e.includes('alina')) return 'mpb2';
  if (e.includes('mpb3') || e.includes('alua')) return 'mpb3';
  if (e.includes('mpb4') || e.includes('darina')) return 'mpb4';
  return null;
}

export function publicUser(row) {
  return {
    id: row.id,
    email: row.email,
    name: row.name,
    role: row.role,
    manager_code: inferManagerCode(row),
    status: row.status
  };
}

// Проверяет токен и актуальное состояние пользователя в базе.
// Возвращает публичный профиль или null.
export async function requireUser(req, supabase, allowedRoles = null) {
  const payload = verifyToken(bearer(req));
  if (!payload) return null;
  const { data, error } = await supabase
    .from('app_users')
    .select('*')
    .eq('email', payload.sub)
    .single();
  if (error || !data || data.status !== 'active') return null;
  if (allowedRoles && !allowedRoles.includes(data.role)) return null;
  return publicUser(data);
}

export function setCors(res, methods) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', methods);
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');
}

export function parseBody(req) {
  if (typeof req.body === 'string') {
    try { return JSON.parse(req.body); } catch (e) { return {}; }
  }
  return req.body || {};
}
