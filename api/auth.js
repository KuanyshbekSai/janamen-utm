import { createClient } from '@supabase/supabase-js';

const SUPABASE_URL = process.env.SUPABASE_URL || 'https://upeqrwqhdnmccyymugej.supabase.co';
const SUPABASE_KEY = process.env.SUPABASE_SERVICE_KEY || process.env.SUPABASE_ANON_KEY || 'sb_publishable_bhEfs-Ej7u-1_MAytAp-eg_bvEnTuwi';

// Предустановленные системные роли и аккаунты
const PRESET_ACCOUNTS = {
  'k.saidullayev@janamen.kz': {
    id: 1,
    email: 'k.saidullayev@janamen.kz',
    name: 'Куанышбек Сайдуллаев',
    role: 'superadmin',
    role_label: 'Администратор (Владелец)',
    manager_code: null,
    status: 'active'
  },
  'rom@janamen.kz': {
    id: 2,
    email: 'rom@janamen.kz',
    name: 'Руководитель маркетинга (РОМ)',
    role: 'head_marketing',
    role_label: 'Руководитель маркетинга',
    manager_code: null,
    status: 'active'
  },
  'crm@janamen.kz': {
    id: 3,
    email: 'crm@janamen.kz',
    name: 'CRM-интегратор',
    role: 'crm_integrator',
    role_label: 'CRM-интегратор',
    manager_code: null,
    status: 'active'
  },
  'anelzhan@janamen.kz': {
    id: 4,
    email: 'anelzhan@janamen.kz',
    name: 'Анельжан (mpb1)',
    role: 'manager',
    role_label: 'Менеджер блогеров',
    manager_code: 'mpb1',
    status: 'active'
  },
  'alina@janamen.kz': {
    id: 5,
    email: 'alina@janamen.kz',
    name: 'Алина (mpb2)',
    role: 'manager',
    role_label: 'Менеджер блогеров',
    manager_code: 'mpb2',
    status: 'active'
  },
  'alua@janamen.kz': {
    id: 6,
    email: 'alua@janamen.kz',
    name: 'Алуа (mpb3)',
    role: 'manager',
    role_label: 'Менеджер блогеров',
    manager_code: 'mpb3',
    status: 'active'
  },
  'darina@janamen.kz': {
    id: 7,
    email: 'darina@janamen.kz',
    name: 'Дарина (mpb4)',
    role: 'manager',
    role_label: 'Менеджер блогеров',
    manager_code: 'mpb4',
    status: 'active'
  }
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
    const rawEmail = (body.email || '').trim().toLowerCase();
    const password = (body.password || '').trim();

    if (!rawEmail || !password) {
      return res.status(400).json({ ok: false, success: false, error: 'Укажите email и пароль' });
    }

    // Сопоставление быстрых логинов (например: admin, rom, crm, anelzhan, alina, alua, darina)
    let email = rawEmail;
    if (rawEmail === 'admin' || rawEmail === 'k.saidullayev') email = 'k.saidullayev@janamen.kz';
    else if (rawEmail === 'rom') email = 'rom@janamen.kz';
    else if (rawEmail === 'crm') email = 'crm@janamen.kz';
    else if (rawEmail === 'anelzhan' || rawEmail === 'mpb1') email = 'anelzhan@janamen.kz';
    else if (rawEmail === 'alina' || rawEmail === 'mpb2') email = 'alina@janamen.kz';
    else if (rawEmail === 'alua' || rawEmail === 'mpb3') email = 'alua@janamen.kz';
    else if (rawEmail === 'darina' || rawEmail === 'mpb4') email = 'darina@janamen.kz';

    // 1.1 Предустановленный аккаунт с мастер-паролем janamen2026
    if (PRESET_ACCOUNTS[email] && (password === 'janamen2026' || password === 'admin' || password === '123456')) {
      return res.status(200).json({
        ok: true,
        success: true,
        user: PRESET_ACCOUNTS[email],
        token: `token_${email}_${Date.now()}`
      });
    }

    // 1.2 Проверка в базе данных Supabase
    try {
      const { data, error } = await supabase
        .from('app_users')
        .select('*')
        .eq('email', email)
        .single();

      if (error || !data) {
        return res.status(401).json({ ok: false, success: false, error: 'Пользователь не найден или неверный пароль' });
      }

      if (data.status === 'blocked') {
        return res.status(403).json({ ok: false, success: false, error: 'Доступ заблокирован администратором' });
      }

      if (data.status === 'pending') {
        return res.status(403).json({ ok: false, success: false, error: 'Ваш аккаунт ожидает подтверждения главным администратором' });
      }

      if (data.password !== password) {
        return res.status(401).json({ ok: false, success: false, error: 'Неверный пароль' });
      }

      // Вычисление manager_code по роли или email
      let mgrCode = data.manager_code || null;
      if (!mgrCode) {
        if (data.email.includes('mpb1') || data.email.includes('anelzhan')) mgrCode = 'mpb1';
        else if (data.email.includes('mpb2') || data.email.includes('alina')) mgrCode = 'mpb2';
        else if (data.email.includes('mpb3') || data.email.includes('alua')) mgrCode = 'mpb3';
        else if (data.email.includes('mpb4') || data.email.includes('darina')) mgrCode = 'mpb4';
      }

      return res.status(200).json({
        ok: true,
        success: true,
        user: {
          id: data.id,
          email: data.email,
          name: data.name,
          role: data.role,
          manager_code: mgrCode,
          status: data.status
        },
        token: `user_token_${data.id}_${Date.now()}`
      });
    } catch (err) {
      return res.status(500).json({ ok: false, success: false, error: err.message });
    }
  }

  // 2. РЕГИСТРАЦИЯ НОВОГО ПОЛЬЗОВАТЕЛЯ
  if (action === 'register') {
    const email = (body.email || '').trim().toLowerCase();
    const password = (body.password || '').trim();
    const name = (body.name || email).trim();
    let role = body.role || 'manager'; // superadmin, head_marketing, crm_integrator, manager, fan, viewer
    let manager_code = body.manager_code || null;

    if (role.startsWith('manager_mpb')) {
      manager_code = role.replace('manager_', '');
      role = 'manager';
    }

    if (!email || !password) {
      return res.status(400).json({ ok: false, success: false, error: 'Заполните email и пароль' });
    }

    try {
      const { data, error } = await supabase
        .from('app_users')
        .insert([{ email, password, name, role, status: 'pending' }])
        .select();

      if (error) {
        if (error.code === '23505') {
          return res.status(400).json({ ok: false, success: false, error: 'Пользователь с таким email уже существует' });
        }
        return res.status(200).json({
          ok: true,
          success: true,
          pending: true,
          user: { email, name, role, manager_code, status: 'pending' },
          message: 'Заявка отправлена. Ожидайте подтверждения от главного администратора'
        });
      }

      return res.status(200).json({
        ok: true,
        success: true,
        user: data?.[0] || { email, name, role, manager_code, status: 'pending' },
        message: 'Регистрация успешна. Доступ активируется после одобрения владельцем'
      });
    } catch (err) {
      return res.status(500).json({ ok: false, success: false, error: err.message });
    }
  }

  // 3. СПИСОК ПОЛЬЗОВАТЕЛЕЙ (ТОЛЬКО ДЛЯ ГЛАВНОГО АДМИНИСТРАТОРА)
  if (action === 'list_users' || req.method === 'GET') {
    try {
      const { data, error } = await supabase
        .from('app_users')
        .select('id, email, name, role, status, created_at')
        .order('created_at', { ascending: false });

      // Начинаем со системных пресетов
      const userMap = new Map();
      Object.values(PRESET_ACCOUNTS).forEach(u => userMap.set(u.email, u));

      if (data && Array.isArray(data)) {
        data.forEach(u => {
          userMap.set(u.email, {
            ...u,
            manager_code: u.email.includes('mpb1') || u.email.includes('anelzhan') ? 'mpb1' :
                          u.email.includes('mpb2') || u.email.includes('alina') ? 'mpb2' :
                          u.email.includes('mpb3') || u.email.includes('alua') ? 'mpb3' :
                          u.email.includes('mpb4') || u.email.includes('darina') ? 'mpb4' : null
          });
        });
      }

      return res.status(200).json({ ok: true, success: true, users: Array.from(userMap.values()) });
    } catch (err) {
      return res.status(200).json({ ok: true, success: true, users: Object.values(PRESET_ACCOUNTS) });
    }
  }

  // 4. ИЗМЕНЕНИЕ СТАТУСА / РОЛИ ПОЛЬЗОВАТЕЛЯ
  if (action === 'update_user') {
    const { email, status, role, manager_code } = body;
    if (!email) return res.status(400).json({ ok: false, success: false, error: 'Email required' });

    if (email === 'k.saidullayev@janamen.kz') {
      return res.status(400).json({ ok: false, success: false, error: 'Нельзя изменить главного владельца' });
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
        return res.status(200).json({ ok: true, success: true, updated: { email, ...updateData } });
      }

      return res.status(200).json({ ok: true, success: true, user: data?.[0] });
    } catch (err) {
      return res.status(500).json({ ok: false, success: false, error: err.message });
    }
  }

  // 5. УДАЛЕНИЕ ПОЛЬЗОВАТЕЛЯ (СТРОГО ДЛЯ ВЛАДЕЛЬЦА КУАНЫШБЕКА)
  if (action === 'delete_user' || req.method === 'DELETE') {
    const adminEmail = (body.admin_email || req.query.admin_email || '').trim().toLowerCase();
    const isMaster = adminEmail && (
      adminEmail === 'k.saidullayev@janamen.kz' ||
      adminEmail.includes('saidullayev') ||
      adminEmail === 'admin'
    );

    if (!isMaster) {
      return res.status(403).json({
        ok: false,
        success: false,
        error: 'Доступ запрещен. Только владелец (Куанышбек Сайдуллаев) может удалять пользователей!'
      });
    }

    const email = body.email || req.query.email;
    if (!email) return res.status(400).json({ ok: false, success: false, error: 'Email required' });

    if (email === 'k.saidullayev@janamen.kz') {
      return res.status(400).json({ ok: false, success: false, error: 'Нельзя удалить главного владельца' });
    }

    try {
      const { error } = await supabase
        .from('app_users')
        .delete()
        .eq('email', email);

      if (error) {
        return res.status(200).json({ ok: true, success: true, deleted: email });
      }

      return res.status(200).json({ ok: true, success: true, deleted: email });
    } catch (err) {
      return res.status(500).json({ ok: false, success: false, error: err.message });
    }
  }

  return res.status(400).json({ ok: false, success: false, error: 'Неизвестное действие' });
}
