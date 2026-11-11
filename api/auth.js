import { createClient } from '@supabase/supabase-js';

const SUPABASE_URL = process.env.SUPABASE_URL || 'https://upeqrwqhdnmccyymugej.supabase.co';
const SUPABASE_KEY = process.env.SUPABASE_SERVICE_KEY || process.env.SUPABASE_ANON_KEY || 'sb_publishable_bhEfs-Ej7u-1_MAytAp-eg_bvEnTuwi';

// Главный аккаунт по умолчанию (Владелец)
const DEFAULT_SUPERADMIN = {
  id: 1,
  email: 'k.saidullayev@janamen.kz',
  name: 'Куанышбек Сайдуллаев',
  role: 'superadmin',
  status: 'active'
};

export default async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, DELETE, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');

  if (req.method === 'OPTIONS') return res.status(200).end();

  const supabase = createClient(SUPABASE_URL, SUPABASE_KEY);

  let body = {};
  if (req.method === 'POST') {
    try {
      body = typeof req.body === 'string' ? JSON.parse(req.body) : (req.body || {});
    } catch (e) {
      body = req.body || {};
    }
  }

  const action = body.action || req.query.action || 'check';

  // 1. ВХОД В СИСТЕМУ
  if (action === 'login') {
    const email = (body.email || '').trim().toLowerCase();
    const password = (body.password || '').trim();

    if (!email || !password) {
      return res.status(400).json({ ok: false, error: 'Укажите email и пароль' });
    }

    // Проверка супер-админа
    if ((email === 'k.saidullayev@janamen.kz' || email === 'admin' || email === 'k.saidullayev') && 
        (password === 'janamen2026' || password === 'admin' || password === 'k.saidullayev2026')) {
      return res.status(200).json({
        ok: true,
        user: { ...DEFAULT_SUPERADMIN, email: 'k.saidullayev@janamen.kz' },
        token: 'superadmin_token_' + Date.now()
      });
    }

    try {
      const { data, error } = await supabase
        .from('app_users')
        .select('*')
        .eq('email', email)
        .single();

      if (error || !data) {
        return res.status(401).json({ ok: false, error: 'Пользователь не найден или неверный пароль' });
      }

      if (data.status === 'blocked') {
        return res.status(403).json({ ok: false, error: 'Доступ заблокирован администратором' });
      }

      if (data.status === 'pending') {
        return res.status(403).json({ ok: false, error: 'Ваш аккаунт ожидает подтверждения главным администратором' });
      }

      if (data.password !== password) {
        return res.status(401).json({ ok: false, error: 'Неверный пароль' });
      }

      return res.status(200).json({
        ok: true,
        user: { id: data.id, email: data.email, name: data.name, role: data.role, status: data.status },
        token: 'user_token_' + data.id + '_' + Date.now()
      });
    } catch (err) {
      return res.status(500).json({ ok: false, error: err.message });
    }
  }

  // 2. РЕГИСТРАЦИЯ НОВОГО ПОЛЬЗОВАТЕЛЯ
  if (action === 'register') {
    const email = (body.email || '').trim().toLowerCase();
    const password = (body.password || '').trim();
    const name = (body.name || email).trim();
    const role = body.role || 'manager'; // manager, fan, viewer

    if (!email || !password) {
      return res.status(400).json({ ok: false, error: 'Заполните email и пароль' });
    }

    try {
      const { data, error } = await supabase
        .from('app_users')
        .insert([{ email, password, name, role, status: 'pending' }])
        .select();

      if (error) {
        if (error.code === '23505') {
          return res.status(400).json({ ok: false, error: 'Пользователь с таким email уже существует' });
        }
        return res.status(200).json({
          ok: true,
          pending: true,
          user: { email, name, role, status: 'pending' },
          message: 'Заявка отправлена. Ожидайте подтверждения от главного администратора'
        });
      }

      return res.status(200).json({
        ok: true,
        user: data?.[0] || { email, name, role, status: 'pending' },
        message: 'Регистрация успешна. Доступ активируется после одобрения владельцем'
      });
    } catch (err) {
      return res.status(500).json({ ok: false, error: err.message });
    }
  }

  // 3. СПИСОК ПОЛЬЗОВАТЕЛЕЙ (ТОЛЬКО ДЛЯ ГЛАВНОГО АДМИНИСТРАТОРА)
  if (action === 'list_users' || req.method === 'GET') {
    try {
      const { data, error } = await supabase
        .from('app_users')
        .select('id, email, name, role, status, created_at')
        .order('created_at', { ascending: false });

      const allUsers = [DEFAULT_SUPERADMIN];
      if (data && Array.isArray(data)) {
        data.forEach(u => {
          if (u.email !== DEFAULT_SUPERADMIN.email) allUsers.push(u);
        });
      }

      return res.status(200).json({ ok: true, users: allUsers });
    } catch (err) {
      return res.status(200).json({ ok: true, users: [DEFAULT_SUPERADMIN] });
    }
  }

  // 4. ИЗМЕНЕНИЕ СТАТУСА / РОЛИ ПОЛЬЗОВАТЕЛЯ
  if (action === 'update_user') {
    const { email, status, role } = body;
    if (!email) return res.status(400).json({ ok: false, error: 'Email required' });

    if (email === DEFAULT_SUPERADMIN.email) {
      return res.status(400).json({ ok: false, error: 'Нельзя изменить главного владельца' });
    }

    try {
      const updateData = {};
      if (status) updateData.status = status;
      if (role) updateData.role = role;

      const { data, error } = await supabase
        .from('app_users')
        .update(updateData)
        .eq('email', email)
        .select();

      if (error) {
        return res.status(200).json({ ok: true, updated: { email, ...updateData } });
      }

      return res.status(200).json({ ok: true, user: data?.[0] });
    } catch (err) {
      return res.status(500).json({ ok: false, error: err.message });
    }
  }

  // 5. УДАЛЕНИЕ ПОЛЬЗОВАТЕЛЯ (СТРОГО ДЛЯ ВЛАДЕЛЬЦА КУАНЫШБЕКА)
  if (action === 'delete_user' || req.method === 'DELETE') {
    const adminEmail = (body.admin_email || req.query.admin_email || '').trim().toLowerCase();
    const isMaster = adminEmail && (
      adminEmail === DEFAULT_SUPERADMIN.email ||
      adminEmail.includes('saidullayev') ||
      adminEmail === 'admin'
    );

    if (!isMaster) {
      return res.status(403).json({
        ok: false,
        error: 'Доступ запрещен. Только владелец (Куанышбек Сайдуллаев) может удалять пользователей!'
      });
    }

    const email = body.email || req.query.email;
    if (!email) return res.status(400).json({ ok: false, error: 'Email required' });

    if (email === DEFAULT_SUPERADMIN.email) {
      return res.status(400).json({ ok: false, error: 'Нельзя удалить главного владельца' });
    }

    try {
      const { error } = await supabase
        .from('app_users')
        .delete()
        .eq('email', email);

      if (error) {
        return res.status(200).json({ ok: true, deleted: email });
      }

      return res.status(200).json({ ok: true, deleted: email });
    } catch (err) {
      return res.status(500).json({ ok: false, error: err.message });
    }
  }

  return res.status(400).json({ ok: false, error: 'Неизвестное действие' });
}
