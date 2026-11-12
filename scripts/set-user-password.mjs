#!/usr/bin/env node
// Создаёт или обновляет пользователя портала с новым паролем (хэш scrypt).
// Читает SUPABASE_URL и SUPABASE_SERVICE_KEY из окружения или файла .env.
//
// Пример:
//   node scripts/set-user-password.mjs k.saidullayev@janamen.kz superadmin "Куанышбек Сайдуллаев"
//   node scripts/set-user-password.mjs anelzhan@janamen.kz manager "Анельжан" mpb1
// Пароль спрашивается в терминале (не попадает в историю команд).
import fs from 'fs';
import path from 'path';
import readline from 'readline';
import { fileURLToPath } from 'url';
import { createClient } from '@supabase/supabase-js';
import { hashPassword, ROLES } from '../api/_lib/auth.js';

const root = path.join(path.dirname(fileURLToPath(import.meta.url)), '..');
const envFile = path.join(root, '.env');
if (fs.existsSync(envFile)) {
  for (const line of fs.readFileSync(envFile, 'utf8').split('\n')) {
    const m = /^\s*([A-Z0-9_]+)\s*=\s*(.*)\s*$/.exec(line);
    if (m && !process.env[m[1]]) process.env[m[1]] = m[2].replace(/^['"]|['"]$/g, '');
  }
}

const [email, role = 'manager', name, managerCode] = process.argv.slice(2);
if (!email || !ROLES.includes(role)) {
  console.error(`Использование: node scripts/set-user-password.mjs <email> <${ROLES.join('|')}> [имя] [mpbN]`);
  process.exit(1);
}
if (!process.env.SUPABASE_URL || !process.env.SUPABASE_SERVICE_KEY) {
  console.error('Нужны SUPABASE_URL и SUPABASE_SERVICE_KEY (в окружении или .env)');
  process.exit(1);
}

function askHidden(question) {
  return new Promise((resolve) => {
    const rl = readline.createInterface({ input: process.stdin, output: process.stdout, terminal: true });
    rl._writeToOutput = (s) => { if (s.includes(question)) rl.output.write(s); };
    rl.question(question, (answer) => { rl.close(); process.stdout.write('\n'); resolve(answer); });
  });
}

const password = await askHidden('Новый пароль (мин. 8 символов): ');
if (password.length < 8) { console.error('Пароль слишком короткий'); process.exit(1); }
const again = await askHidden('Повторите пароль: ');
if (password !== again) { console.error('Пароли не совпадают'); process.exit(1); }

const supabase = createClient(process.env.SUPABASE_URL, process.env.SUPABASE_SERVICE_KEY);
const row = {
  email: email.trim().toLowerCase(),
  password: hashPassword(password),
  name: name || email,
  role,
  manager_code: managerCode || null,
  status: 'active'
};
const { error } = await supabase.from('app_users').upsert(row, { onConflict: 'email' });
if (error) { console.error('Ошибка Supabase:', error.message); process.exit(1); }
console.log(`✓ Пользователь ${row.email} (${role}) сохранён и активен`);
