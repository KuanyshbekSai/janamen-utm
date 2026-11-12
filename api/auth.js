import { createClient } from '@supabase/supabase-js';
import {
  ROLES, getSupabaseConfig, hashPassword, verifyPassword, signToken,
  requireUser, publicUser, setCors, parseBody
} from './_lib/auth.js';

// Короткие логины → email
const LOGIN_ALIASES = {
  admin: 'k.saidullayev@janamen.kz',
  'k.saidullayev': 'k.saidullayev@janamen.kz',
  rom: 'rom@janamen.kz',
  crm: 'crm@janamen.kz',
  anelzhan: 'anelzhan@janamen.kz', mpb1: 'anelzhan@janamen.kz',
  alina: 'alina@janamen.kz', mpb2: 'alina@janamen.kz',
  alua: 'alua@janamen.kz', mpb3: 'alua@janamen.kz',
  darina: 'darina@janamen.kz', mpb4: 'darina@janamen.kz'
};

const MIN_PASSWORD = 8;
const fail = (res, code, error) => res.status(code).json({ ok: false, success: false, error });

function normalizeRole(rawRole) {
  let role = String(rawRole || 'manager');
  let manager_code = null;
  if (role.startsWith('manager_mpb')) {
    manager_code = role.replace('manager_', '');
    role = 'manager';
  }
  return { role, manager_code };
}

export default async function handler(req, res) {
  setCors(res, 'GET, POST, OPTIONS');
  if (req.method === 'OPTIONS') return res.status(200).end();

  const cfg = getSupabaseConfig();
  if (!cfg || !process.env.AUTH_SECRET) {
    return fail(res, 500, 'Сервер не настроен: нужны SUPABASE_URL, SUPABASE_SERVICE_KEY и AUTH_SECRET');
  }
  const supabase = createClient(cfg.url, cfg.key);

  const body = req.method === 'POST' ? parseBody(req) : {};
  const action = body.action || req.query.action || '';

  // 1. ВХОД
  if (action === 'login') {
    const raw = String(body.email || '').trim().toLowerCase();
    const password = String(body.password || '');
    if (!raw || !password) return fail(res, 400, 'Укажите email и пароль');
    const email = LOGIN_ALIASES[raw] || raw;

    const { data, error } = await supabase.from('app_users').select('*').eq('email', email).single();
    const check = (!error && data) ? verifyPassword(password, data.password) : { ok: false };
    if (!check.ok) return fail(res, 401, 'Неверный email или пароль');

    if (check.leaked) {
      return fail(res, 403, 'Этот пароль был опубликован и больше не действует. Попросите владельца задать новый пароль.');
    }
    if (data.status === 'blocked') return fail(res, 403, 'Доступ заблокирован администратором');
    if (data.status === 'pending') return fail(res, 403, 'Ваш аккаунт ожидает подтверждения главным администратором');

    if (check.needsRehash) {
      await supabase.from('app_users').update({ password: hashPassword(password) }).eq('id', data.id);
    }

    const user = publicUser(data);
    return res.status(200).json({ ok: true, success: true, user, token: signToken(user) });
  }

  // 2. РЕГИСТРАЦИЯ (заявка, требует одобрения владельца)
  if (action === 'register') {
    const email = String(body.email || '').trim().toLowerCase();
    const password = String(body.password || '');
    const name = String(body.name || email).trim();
    const { role, manager_code } = normalizeRole(body.role);

    if (!email || !password) return fail(res, 400, 'Заполните email и пароль');
    if (password.length < MIN_PASSWORD) return fail(res, 400, `Пароль должен быть не короче ${MIN_PASSWORD} символов`);
    if (!ROLES.includes(role) || role === 'superadmin') return fail(res, 400, 'Недопустимая роль');

    const { data, error } = await supabase
      .from('app_users')
      .insert([{ email, password: hashPassword(password), name, role, manager_code, status: 'pending' }])
      .select();

    if (error) {
      if (error.code === '23505') return fail(res, 400, 'Пользователь с таким email уже существует');
      return fail(res, 500, 'Не удалось сохранить заявку');
    }
    return res.status(200).json({
      ok: true, success: true, pending: true,
      user: publicUser(data[0]),
      message: 'Заявка отправлена. Ожидайте подтверждения от главного администратора'
    });
  }

  // 3. ТЕКУЩИЙ ПОЛЬЗОВАТЕЛЬ (проверка токена)
  if (action === 'me') {
    const me = await requireUser(req, supabase);
    if (!me) return fail(res, 401, 'Сессия недействительна');
    return res.status(200).json({ ok: true, success: true, user: me });
  }

  // Всё ниже — только для активного владельца (superadmin)
  const admin = await requireUser(req, supabase, ['superadmin']);
  if (!admin) return fail(res, 403, 'Доступ запрещен. Действие доступно только владельцу.');

  // 4. СПИСОК ПОЛЬЗОВАТЕЛЕЙ
  if (action === 'list_users') {
    const { data, error } = await supabase
      .from('app_users')
      .select('id, email, name, role, manager_code, status, created_at')
      .order('created_at', { ascending: false });
    if (error) return fail(res, 500, 'Не удалось загрузить пользователей');
    return res.status(200).json({ ok: true, success: true, users: data.map(publicUser) });
  }

  // 5. СОЗДАНИЕ ПОЛЬЗОВАТЕЛЯ / СБРОС ПАРОЛЯ (сразу активен)
  if (action === 'create_user') {
    const email = String(body.email || '').trim().toLowerCase();
    const password = String(body.password || '');
    const name = String(body.name || email).trim();
    const { role, manager_code } = normalizeRole(body.role);

    if (!email || !password) return fail(res, 400, 'Укажите email и пароль');
    if (password.length < MIN_PASSWORD) return fail(res, 400, `Пароль должен быть не короче ${MIN_PASSWORD} символов`);
    if (!ROLES.includes(role)) return fail(res, 400, 'Недопустимая роль');

    const { data, error } = await supabase
      .from('app_users')
      .upsert({ email, password: hashPassword(password), name, role, manager_code, status: 'active' }, { onConflict: 'email' })
      .select();
    if (error) return fail(res, 500, 'Не удалось создать пользователя');
    return res.status(200).json({ ok: true, success: true, user: publicUser(data[0]) });
  }

  // Поиск цели по id или email
  const targetQuery = () => {
    const q = supabase.from('app_users');
    return { q, col: body.id ? 'id' : 'email', val: body.id ? Number(body.id) : String(body.email || '').trim().toLowerCase() };
  };

  // 6. ИЗМЕНЕНИЕ СТАТУСА / РОЛИ
  if (action === 'update_user') {
    const { q, col, val } = targetQuery();
    if (!val) return fail(res, 400, 'Укажите пользователя');
    if (val === admin.id || val === admin.email) return fail(res, 400, 'Нельзя изменить собственную учётную запись');

    const update = {};
    if (body.status) {
      if (!['active', 'pending', 'blocked'].includes(body.status)) return fail(res, 400, 'Недопустимый статус');
      update.status = body.status;
    }
    if (body.role) {
      const { role, manager_code } = normalizeRole(body.role);
      if (!ROLES.includes(role)) return fail(res, 400, 'Недопустимая роль');
      update.role = role;
      if (manager_code) update.manager_code = manager_code;
    }
    if (body.manager_code !== undefined) update.manager_code = body.manager_code || null;
    if (!Object.keys(update).length) return fail(res, 400, 'Нечего обновлять');

    const { data, error } = await q.update(update).eq(col, val).select();
    if (error) return fail(res, 500, 'Не удалось обновить пользователя');
    return res.status(200).json({ ok: true, success: true, user: data[0] ? publicUser(data[0]) : null });
  }

  // 7. УДАЛЕНИЕ ПОЛЬЗОВАТЕЛЯ
  if (action === 'delete_user') {
    const { q, col, val } = targetQuery();
    if (!val) return fail(res, 400, 'Укажите пользователя');
    if (val === admin.id || val === admin.email) return fail(res, 400, 'Нельзя удалить собственную учётную запись');

    const { error } = await q.delete().eq(col, val);
    if (error) return fail(res, 500, 'Не удалось удалить пользователя');
    return res.status(200).json({ ok: true, success: true, deleted: val });
  }

  return fail(res, 400, 'Неизвестное действие');
}
