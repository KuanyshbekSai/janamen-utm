/**
 * ============================================================
 * SupabaseSync.js — Регулярный запуск синхронизации AmoCRM -> Supabase
 * Сама синхронизация живёт на Vercel (/api/sync), здесь только расписание.
 * ============================================================
 */

var SUPABASE_SYNC_URL = 'https://janamen-utm.vercel.app/api/sync';
var SUPABASE_SYNC_EVERY_MIN = 10;   // как часто запускать
var SUPABASE_SYNC_WINDOW_HOURS = 1; // окно с запасом: пропущенный запуск не теряет сделки

/**
 * Вызывает /api/sync и догружает остаток, если за один вызов не успело.
 * @param {number=} hours окно в часах (по умолчанию SUPABASE_SYNC_WINDOW_HOURS)
 */
function syncDealsToSupabase(hours) {
  // Триггер передаёт сюда объект события, поэтому число берём только если оно явно задано
  var h = (typeof hours === 'number' && hours > 0) ? hours : SUPABASE_SYNC_WINDOW_HOURS;
  var url = SUPABASE_SYNC_URL + '?hours=' + h;
  var total = 0;

  for (var i = 0; i < 20; i++) {
    var resp = UrlFetchApp.fetch(url, { muteHttpExceptions: true });
    var code = resp.getResponseCode();
    var body = {};
    try { body = JSON.parse(resp.getContentText()); } catch (e) {}

    if (code !== 200) {
      throw new Error('Синхронизация Supabase: HTTP ' + code + ' ' + resp.getContentText().slice(0, 300));
    }
    total += body.synced || 0;
    if (body.complete || !body.next_from) break;
    url = SUPABASE_SYNC_URL + '?from=' + body.next_from;
  }

  Logger.log('Supabase: синхронизировано сделок: ' + total);
  return total;
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
  var n = syncDealsToSupabase(72); // сразу догружаем последние 3 дня
  try {
    SpreadsheetApp.getActiveSpreadsheet().toast(
      'Портал обновляется каждые ' + SUPABASE_SYNC_EVERY_MIN + ' мин. Догружено сделок: ' + n,
      'Автосинхронизация Supabase включена', 8);
  } catch (e) {}
}

function clearSupabaseSyncTrigger() {
  deleteTriggersByHandler_('syncDealsToSupabase');
  try { SpreadsheetApp.getActiveSpreadsheet().toast('Автосинхронизация Supabase отключена', 'Триггер удалён', 5); } catch (e) {}
}
