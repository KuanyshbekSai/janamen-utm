/**
 * ============================================================
 * SupabaseSync.js — Регулярный запуск синхронизации AmoCRM -> Supabase
 * Сама синхронизация живёт на Vercel (/api/sync), здесь только расписание.
 *
 * Один короткий вызов ?auto=1 раз в 10 минут: место, до которого дошла синхронизация,
 * хранит сервер. Так скрипт укладывается в суточную квоту Google на триггеры
 * (90 минут в день на обычном аккаунте): прошлая версия догоняла по 4 минуты
 * за запуск и выбирала квоту за полдня, после чего Google переставал её запускать.
 * ============================================================
 */

var SUPABASE_SYNC_URL = 'https://janamen-utm.vercel.app/api/sync?auto=1';
var SUPABASE_SYNC_EVERY_MIN = 10;

function syncDealsToSupabase() {
  var resp = UrlFetchApp.fetch(SUPABASE_SYNC_URL, { muteHttpExceptions: true });
  var code = resp.getResponseCode();
  var body = {};
  try { body = JSON.parse(resp.getContentText()); } catch (e) {}
  if (code !== 200) {
    throw new Error('Синхронизация Supabase: HTTP ' + code + ' ' + resp.getContentText().slice(0, 300));
  }
  Logger.log('Supabase: синхронизировано ' + (body.synced || 0) + ' сделок' + (body.complete ? '' : ' (продолжит в следующий запуск)'));
  return { synced: body.synced || 0, complete: !!body.complete };
}

/**
 * Включает автосинхронизацию с Supabase каждые 10 минут.
 */
function setupSupabaseSyncTrigger() {
  deleteTriggersByHandler_('syncDealsToSupabase');
  ScriptApp.newTrigger('syncDealsToSupabase')
    .timeBased()
    .everyMinutes(SUPABASE_SYNC_EVERY_MIN)
    .create();
  var res = syncDealsToSupabase();
  try {
    SpreadsheetApp.getActiveSpreadsheet().toast(
      'Портал обновляется каждые ' + SUPABASE_SYNC_EVERY_MIN + ' мин. Сейчас синхронизировано: ' + res.synced,
      'Автосинхронизация Supabase включена', 8);
  } catch (e) {}
}

function clearSupabaseSyncTrigger() {
  deleteTriggersByHandler_('syncDealsToSupabase');
  try { SpreadsheetApp.getActiveSpreadsheet().toast('Автосинхронизация Supabase отключена', 'Триггер удалён', 5); } catch (e) {}
}
